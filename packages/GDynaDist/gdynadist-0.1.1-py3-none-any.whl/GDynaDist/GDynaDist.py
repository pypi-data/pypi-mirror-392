import pandas as pd
from scipy.sparse import csr_matrix, diags
import numpy as np
from copy import copy
from datetime import datetime
from EDRep import CreateEmbedding
    
class TGraph:
    '''Class to handle the temporal graph data
    
    * self.df (pandas datframe): preprocessed dataframe, ready to be used for the distance computation
    * self.NodeMapper: (dict): dictionary mapping the nodes ids to integers
    * self.n (int): number of nodes
    * self.T (int): number of snapshots:
    * self.t_agg (float): aggregation parameter
    * self.taumin (float): shortest interaction duration utilized
    * self.X (array): embedding matrix
    * self.symmetric (bool): this parameter specifies if the graph is directed
    '''

    def __init__(self, df, NodeMapper, n, T, t_agg, taumin, X, symmetric):
        self.df = df
        self.NodeMapper = NodeMapper
        self.n = n
        self.T = T
        self.t_agg = t_agg
        self.taumin = taumin
        self.X = X
        self.symmetric = symmetric


class Graphs4Distance:
    '''Class to handle the temporal graphs and compute the distance.
    
    * self.verbose: sets the level of verbosity. With verbose = 0, the progress will not be printed. With verbose = 1, only some messages will be printed, while verbose = 2 is the highest verbosity level.
    * self.dim (int): embedding dimension
    * self.n_epochs (int): number of training epochs to obtain the embeddings
    * self.k (int): Order of the Gaussian approximation of EDRep. By default set to 1.
    * self.eta (float): learning rate. By default set to 0.8
    * self.seed (int): seed used for the random number generator
    * self.graphs (dict): a dictionary containing TGraph class element
    '''

    def __init__(self, verbose: int = 2, dim: int = 32, n_epochs: int = 30, k: int = 1, eta: float = 0.8, seed: int = 123):
        self.verbose = verbose
        self.dim = dim
        self.n_epochs = n_epochs
        self.k = k
        self.eta = eta
        self.seed = seed
        self.graphs = dict() 


    def LoadDataset(self, df_: pd.DataFrame, name, nodes = None, taumin = None, t_agg: float = 1., format = None, symmetric: bool = True):
        '''This function loads and preprocesses the input data and returns a class
        
        Inputs:
            * df_ (pandas dataframe): input data. This dataframe must have the columns `i`, `j`, and `t` which indicate an interaction between `i` and `j` starting at time `t`. The dataframe might also have the column `tau` which indicates the duration of the interaction OR the column `w` which assigns a weight to the interaction, assuming it to be istanteneous.
            * name (str, float, int): this argument is a code used to identify the graph. 
            
        Option inputs:
            * nodes (array): by default it is set to None and the nodes are inferred from the edge list. If the node list is specified, then one can include nodes that do not appear in the edge list as well.
            * taumin (int): when using the (i,j,t,tau) representation, this parameters allows the user to discretize time. If it is not specified, the shortest tau will be used.
            * t_agg (float): this parameter sets the time aggregation considering simulataneous all interactions happening at the same time. Note that it is different from taumin which only sets the minimal duration of an interaction event in the case in which time is continuous. This parameter is crucial to dicrease the number of snapshots and speed up the distance computation, but also to change the time-scale under analysis.
            * format (string): specifies the format of the time column if it is expressed in date-time format. The use of this variable follows the datetime package. If time is expressed in terms of epochs, this input has to be left to None
            * symmetric (bool): this specifies if the graph is unidirected (symmetric = True) or directed (symmetric = False)
            
        Outputs:
            TGraph class instance
        '''

        verbose = self.verbose
        df = copy(df_)

        
        # list the columns in the dataframe
        cols = list(df.columns)

        # convert the date-time format to a number of seconds
        if format:
            df.t = df.t.map(lambda x: datetime.strptime(x, format).timestamp())

        if np.sum([type(x*1.) is not np.float64 for x in df.t.values]) > 0:
            print(DeprecationWarning('The time column is not properly formatted. If you are using date-time, please use the `format` parameter to make the conversion to float numbers'))


        if not np.isin(['i', 'j', 't'], df.columns).all():
            print(DeprecationWarning('ERROR: the input is not properly formatted, since at least one among the columns `i`, `j`, `t` is missing.\nThe columns `i` and `j` denote the indeces of the interacting nodes. The column `t` denotes the interaction time.'))

        if 'tau' in cols:
            # convert to the ijt format
            df = _ijttau2ijt(df, taumin, verbose)

            if 'w' in cols:
                print(DeprecationWarning('ERROR: the input has an incompatible format.\nIf the input dataframe has the column tau, it cannot have also the column w describing the edge weights'))

        else:
            if 'w' not in cols:
                df['w'] = 1


        # create the node mapping
        if nodes is not None:
            all_nodes = nodes
        else:
            all_nodes = np.unique(df[['i', 'j']].values)
        n = len(all_nodes)

        if verbose >= 1:
            print(f'The graph has n = {n} nodes')
            
        NodeMapper = dict(zip(all_nodes, np.arange(n)))

        df.i = df.i.map(lambda x: NodeMapper[x])
        df.j = df.j.map(lambda x: NodeMapper[x])

        # shift and aggregate time
        df.t = df.t - df.t.min()
        df.t = (df.t/t_agg).astype(int)

        df = df.groupby(['i', 'j', 't']).sum().reset_index()
        
        # check the maximum T
        T = df.t.max()+1

        if verbose >= 1:
            print(f'The number of snapshot is T = {T}.')
        if verbose == 2:
            print(f'To reduce the T and speed up the distance computation, consider to increase the parameter `t_agg`.')

        self.graphs[name] = TGraph(df, NodeMapper, n, T, t_agg, taumin, None, symmetric)

        return
    

    def GraphDynamicEmbedding(self, name, keep_graph: bool = False):
        '''This function computes the embedding of a dynamical graph using the EDRep algorithm

        Inputs:
            * name (string / int / float): this is a code to identify the temporal graph  
              
        Optional inputs: 
            * keep_graph (bool): if this parameter is set to False (dafault), the dataframe containing the temporal graph will be deleted after the embedding has been computed, otherwise it will be kept. Note that keeping the dataframe may unnecessarily occupy memory space. 
            
        Output:
            * X (array): embedding vector
        '''

        if not self.graphs[name].X is None:
            print(Warning('The embedding has already been computed. If you want to compute it again, run\n ```Data.graphs[graph_name].X = None```'))
            return

        if self.graphs[name].df is None:
            print(DeprecationWarning(f'The graph {name} does not exist and the embedding cannot be computed. Please load it using the function LoadDataset()'))
            return

        dim, n_epochs, k, verbose, eta, seed = self.dim, self.n_epochs, self.k, self.verbose, self.eta, self.seed

        # save the seed state
        rdn_state = np.random.get_state()

        # set the seed
        np.random.seed(seed)

        df, n = self.graphs[name].df, self.graphs[name].n

        # group the graphs by time
        df_grouped = df.groupby('t')
        df_idx1 = df_grouped.i.apply(list)
        df_idx2 = df_grouped.j.apply(list)
        df_w = df_grouped.w.apply(list)
        all_times = list(df_grouped.indices.keys())

        # get the graph matrix for each time-step
        Pt = []

        for t in all_times[::-1]:

            # build the adjacency matrix @t
            A = csr_matrix((df_w.loc[t], (df_idx1.loc[t], df_idx2.loc[t])), shape = (n,n))
            if self.graphs[name].symmetric:
                A = A + A.T
            A = A + diags(np.ones(n))   

            # get the Laplacian matrix
            d = A@np.ones(n)
            D_1 = diags(d**(-1))
            Pt.append(D_1.dot(A))

        if verbose >= 1:
            print(f'Computing the embeddings of {name}')

        # get the P matrix
        if len(df) > n*(n-1)/2:
            P = [np.sum(np.cumprod(Pt))/len(Pt)]

            # create the embedding
            res = CreateEmbedding(P, dim = dim, n_epochs = n_epochs, k = k, eta = eta, verbose = (verbose == 2))
        else:
            res = CreateEmbedding(Pt, dim = dim, n_epochs = n_epochs, k = k, eta = eta, verbose = (verbose == 2), sum_partials = True)

        self.graphs[name].X = res.X

        if keep_graph == False:
            if verbose >= 1:
                print(f'Deleting {name}')
            
            del self.graphs[name].df
            self.graphs[name].df = None

        # reset the random state
        np.random.set_state(rdn_state)

        return

    def GetDistance(self, name_1, name_2, distance_type = 'unmatched', node_mapping = None):
        '''This function computes the distance between 

        Use: d = EmbDistance(X, Y)

        Inputs:
            * X, Y (arrays): input embeddings corresponding to the two temporal graphs. The number of rows of the two matrices must be the same.
            
        Optional inputs:
            * distance_type (string): can be 'unmatched' or 'matched'
            * Node mapping (dict): when using the matched distance, this parameter must be specified and it indicates the mapping known bijective mapping between the nodes in the first graph and the nodes in the second graph. It is expressed as a dictionary.
        Output:
            * d (float): distance between the two graphs.
        '''

        if self.graphs[name_1].X is None:
            self.GraphDynamicEmbedding(name_1)

        if self.graphs[name_2].X is None:
            self.GraphDynamicEmbedding(name_2)

        X, Y = self.graphs[name_1].X, self.graphs[name_2].X
        
        n1, d1 = X.shape
        n2, d2 = Y.shape

        # run initial checks

        if d1 != d2:
            raise DeprecationWarning('The embedding matrices have different dimensions')
        else:
            d = d1

        
        if distance_type not in ['unmatched', 'matched']:
            raise DeprecationWarning('The distance type is not valid')
        
        else:
            if (distance_type == 'matched') and (n1 != n2):
                raise DeprecationWarning("The input matrices do not have the same size")
            else:
                n = n1

        if distance_type == 'matched':
            if node_mapping is None:
                raise DeprecationWarning("The node mapping has not been specified and it must be given as an input when using the matched distance")

            if node_mapping is 'Same':
                nodes = list(self.graphs[name_1].NodeMapper.keys())
                node_mapping = dict(zip(nodes, nodes))
                
            # apply the known bijective mapping to the rows of the two embedding matrices
            kk = [self.graphs[name_1].NodeMapper[x] for x in node_mapping.keys()]
            vv = [self.graphs[name_2].NodeMapper[x] for x in node_mapping.values()]
            SameBasisDict = dict(zip(vv, kk))
            idx = np.argsort([SameBasisDict[x] for x in np.arange(len(kk))])
            Y = Y[idx]

            Mxx = X.T@X
            Mxy = X.T@Y
            Myy = Y.T@Y
            d = np.sqrt(np.abs(np.linalg.norm(Mxx)**2 + np.linalg.norm(Myy)**2 - 2*np.linalg.norm(Mxy)**2))

        else:
            λ1 = np.linalg.eigvalsh(X.T@X)
            λ2 = np.linalg.eigvalsh(Y.T@Y)
            d = np.linalg.norm(λ1-λ2)
    
        return d

##########################################


def _ijttau2ijt(df, taumin, verbose):
    '''This function converts the input from the format ijttau to ijt'''

    # get the minimal duration of an interaction
    taumin_est = df.tau.min()

    if taumin:
        if taumin_est < taumin:
            if verbose >= 1:
                print(Warning('Warning: note that the selected value of `taumin` is smaller than the observed one.\nAll interactions with a duration smaller than `taumin` will be increased by default.'))
        
        else:
            taumin = taumin_est

    else:
        taumin = taumin_est

    if verbose == 2:
        print(f'taumin = {taumin}')
    
    # discretize the duration
    df.tau = np.maximum(1, (df.tau/taumin).astype(int))

    # repeat each row tau times and move to the ijt notation
    new_df = df.loc[df.index.repeat(df.tau)]
    new_df['increment'] = new_df.groupby(level = 0).cumcount()
    new_df.t = new_df.t + new_df.increment*taumin

    # add the weights
    new_df['w'] = 1

    # keep only the relevant columns
    new_df = new_df[['i', 'j', 't', 'w']]

    # aggregate
    return new_df

