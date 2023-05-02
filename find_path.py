from graph_embeddings import Embeddings
import numpy as np
import pandas as pd
from scipy import spatial
from scipy.spatial import distance
from collections import defaultdict
from assign_nodes import unique_nodes
import re
from tqdm import tqdm
import copy
from create_graph import create_graph,create_igraph_graph,create_graph
from graph import KnowledgeGraph
from visualize_subgraph import output_visualization
from tqdm import tqdm



#Go from label to entity_uri (for PKL original labels file) or Label to Idenifier (for microbiome PKL)
# kg_type adds functionality for kg-covid19
def get_uri(labels,value, kg_type,s):

    manually_chosen_uris = {}

    try:
        uri = manually_chosen_uris[value]
        return uri
    except KeyError:
        
        #Added since I know what this once should be, otherwise would have to automatically select this for every subgraph
        if value == 'depressive disorder' and kg_type == 'kg-covid19':
            uri = 'MONDO:0002050'
        else:
            try:
                if len(labels.loc[labels['label'] == value,'entity_uri']) == 1:
                    uri = labels.loc[labels['label'] == value,'entity_uri'].values[0]
                elif len(labels.loc[labels['label'] == value,'entity_uri']) > 1:
                    l = labels.loc[labels['label'] == value,'entity_uri']
                    uri = [i for i in l if 'MONDO' in i][0]
                    '''
                    if 'disorder' in value or 'disease' in value:
                        l = [i for i in (labels.loc[labels['label'] == value,'entity_uri'])]
                        uri = [i for i in l if 'MONDO' in i][0]
                    '''
                    #For manual selection
                    if (len(uri) == 0) and (value not in manually_chosen_uris.keys()):
                        print(value)
                        print(labels.loc[labels['label'] == value,'entity_uri'])
                        uri = input("Please input the ID/uri of the desired node: ")
                        manually_chosen_uris[value] = uri
            except IndexError:
                if kg_type == 'kg-covid19':
                    uri = s.loc[s['target_label'] == value,'target_id'].values[0].split("/")[-1].split('>')[0].replace("_",":")
        
        return uri

def get_label(labels,value,kg_type):
    if kg_type == 'pkl':
        label = labels.loc[labels['entity_uri'] == value,'label'].values[0]
    if kg_type != 'pkl':
        label = labels.loc[labels['entity_uri'] == value,'label'].values[0]        
    return label



def get_key(dictionary,value):

    for key, val in dictionary.items():
        if val == value:
            return key

def define_path_triples(g_nodes,triples_df,path_nodes,search_type):


    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #Keep track of # of mechanisms generated for this node pair in file name for all shortest paths
    count = 1 

    #When there is no connection in graph, path_nodes will equal 1 ([[]]) - for all shortest path search, and [] for all simple path search
    if len(path_nodes) == 0:
        pass
    elif len(path_nodes[0]) != 0:
        for p in range(len(path_nodes)):
            #Dataframe to append each triple to
            full_df = pd.DataFrame()
            n1 = g_nodes[path_nodes[p][0]]  
            for i in range(1,len(path_nodes[p])):
                n2 = g_nodes[path_nodes[p][i]]
                if search_type.lower() == 'all':
                    #Try first direction which is n1 --> n2
                    df = triples_df.loc[(triples_df['subject'] == n1) & (triples_df['object'] == n2)]
                    full_df = pd.concat([full_df,df])
                    if len(df) == 0:
                        #If no results, try second direction which is n2 --> n1
                        df = triples_df.loc[(triples_df['object'] == n1) & (triples_df['subject'] == n2)]
                        full_df = pd.concat([full_df,df])
                elif search_type.lower() == 'out':
                    #Only try direction n1 --> n2
                    df = triples_df.loc[(triples_df['subject'] == n1) & (triples_df['object'] == n2)]
                    full_df = pd.concat([full_df,df])
                full_df = full_df.reset_index(drop=True)
                n1 = n2
        
            #For all shortest path search
            if len(path_nodes) > 1:
                #Generate df
                full_df.columns = ['S','P','O']
                mechanism_dfs['mech#_'+str(count)] = full_df
                count += 1

        #For shortest path search
        if len(path_nodes) == 1 or len(path_nodes) == 0:
            #Generate df
            full_df.columns = ['S','P','O']
            return full_df

    #Return dictionary if all shortest paths search
    if len(path_nodes) > 1:
        return mechanism_dfs

def find_all_shortest_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type,s):

    print('Searching for all shortest paths between ',start_node,' and ',end_node)

    node1 = get_uri(labels_all,start_node, kg_type,s)
    node2 = get_uri(labels_all,end_node, kg_type,s)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #list of nodes
    path_nodes = graph.get_all_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)
    
    #Remove duplicates for bidirectional nodes, only matters when search type=all for mode
    path_nodes = list(set(tuple(x) for x in path_nodes))
    path_nodes = [list(tup) for tup in path_nodes]

    #Dictionary of all triples that are shortest paths, not currently used
    mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
    
    return path_nodes

def find_all_simple_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type,s ,length):


    node1 = get_uri(labels_all,start_node, kg_type,s)
    node2 = get_uri(labels_all,end_node, kg_type,s)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #list of nodes
    path_nodes = graph.get_all_simple_paths(v=node1, to=node2, mode=search_type,cutoff=length)
    #Remove duplicates for bidirectional nodes, only matters when search type=all for mode
    path_nodes = list(set(tuple(x) for x in path_nodes))
    path_nodes = [list(tup) for tup in path_nodes]

    #Dictionary of all triples that are shortest paths, not currently used
    mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
    
    return path_nodes

def get_embedding(emb,node):

    embedding_array = emb[str(node)]
    embedding_array = np.array(embedding_array)

    return embedding_array

def calc_cosine_sim(emb,path_nodes,g_nodes,triples_df,search_type,labels_all,kg_type):

    target_emb = get_embedding(emb,path_nodes[0][len(path_nodes[0])-1])

    #Dict of all embeddings to reuse if they exist
    embeddings = defaultdict(list)

    #List of total cosine similarity for each path in path_nodes, should be same length as path_nodes
    paths_total_cs = []

    for l in path_nodes:
        cs = 0
        for i in range(0,len(l)-1):
            if l[i] not in list(embeddings.keys()):
                e = get_embedding(emb,l[i])
                embeddings[l[i]] = e
            else:
                e = embeddings[l[i]]
            cs += 1 - spatial.distance.cosine(e,target_emb)
        paths_total_cs.append(cs)

    chosen_path_nodes_cs = select_path(paths_total_cs,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(g_nodes,triples_df,chosen_path_nodes_cs,search_type)

    df = convert_to_labels(df,labels_all,kg_type)

    return df,paths_total_cs

def calc_pdp(path_nodes,graph,w,g_nodes,triples_df,search_type,labels_all,kg_type):

    #List of pdp for each path in path_nodes, should be same length as path_nodes
    paths_pdp = []

    for l in path_nodes:
        pdp = 1
        for i in range(0,len(l)-1):
            dp = graph.degree(l[i],mode='all',loops=True)
            dp_damped = pow(dp,-w)
            pdp = pdp*dp_damped

        paths_pdp.append(pdp)

    chosen_path_nodes_pdp = select_path(paths_pdp,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(g_nodes,triples_df,chosen_path_nodes_pdp,search_type)

    df = convert_to_labels(df,labels_all,kg_type)

    return df,paths_pdp

def select_path(value_list,path_nodes):

    #Get max cs from total_cs_path, use that idx of path_nodes then create mechanism
    max_index = value_list.index(max(value_list))
    #Must be list of lists for define_path_triples function
    chosen_path_nodes = [path_nodes[max_index]]

    return chosen_path_nodes

def convert_to_labels(df,labels_all,kg_type):

    full_new_df = pd.DataFrame()

    if kg_type == 'pkl' or kg_type == 'mikg4md':
        for i in range(len(df)):
            data = []
            new_df = pd.DataFrame()
            s_label = [labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['S'],'label'].values[0]]
            #df.iloc[i].loc['S'] = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['S'],'label'].values[0]
            try:
                p_label = [labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['P'],'label'].values[0]]
                #df.iloc[i].loc['P'] = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['P'],'label'].values[0]
            except IndexError:
                df_a = pd.DataFrame.from_dict([{'label':df.iloc[i].loc['P'].split('#')[1],'entity_uri':df.iloc[i].loc['P']}])
                labels_all = pd.concat([labels_all,df_a])
                #labels_all = labels_all.append(df_a)
                labels_all.reset_index(drop=True)
                p_label = [labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['P'],'label'].values[0]]
                #df.iloc[i].loc['P'] = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['P'],'label'].values[0]
            try:
                o_label = [labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O'],'label'].values[0]]
                #df.iloc[i].loc['O'] = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O'],'label'].values[0]
            except IndexError:
                print('Index error with ',df.iloc[i].loc['O'])
                try:
                    df_a = pd.DataFrame.from_dict([{'label':df.iloc[i].loc['O'].split('#')[1],'entity_uri':df.iloc[i].loc['O']}])
                #Errors if name is not after a "#" such as evidence level
                except IndexError:
                    break
                labels_all = pd.concat([labels_all,df_a])
                labels_all.reset_index(drop=True)
                o_label = [labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O'],'label'].values[0]]
                #df.iloc[i].loc['O'] = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O'],'label'].values[0]
            data.append(s_label)
            data.append(p_label)
            data.append(o_label)
            new_df = pd.DataFrame([data],columns=df.columns)
            full_new_df = pd.concat([full_new_df,new_df],axis=0)
        full_new_df = full_new_df.reset_index(drop=True)
        return full_new_df
    if kg_type != 'pkl':
        for i in range(len(df)):
            data = []
            s_label = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['S'],'label'].values[0]
            data.append(s_label)
            o_label =  labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O'],'label'].values[0]
            data.append(df.iloc[i].loc['P'])
            data.append(o_label)
            new_df = pd.DataFrame([data],columns=df.columns)
            
            full_new_df = pd.concat([full_new_df,new_df],axis=0)

        full_new_df = full_new_df.reset_index(drop=True)

        #df = df.reset_index(drop=True)
        #return df

    return full_new_df

# Wrapper functions
#Returns the path as a dataframe of S/P/O of all triples' labels within the path
def find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type,s):

    node1 = get_uri(labels_all,start_node,kg_type,s)
    node2 = get_uri(labels_all,end_node,kg_type,s)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    if len(path_nodes[0]) > 0:

        df = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
        df = convert_to_labels(df,labels_all,kg_type)

    else:
        df = pd.DataFrame()

    return df

def prioritize_path_cs(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions, kg_type,s):

    path_nodes = find_all_shortest_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,False,search_type, kg_type,s)

    e = Embeddings(triples_file,output_dir,input_dir,embedding_dimensions, kg_type)
    emb = e.generate_graph_embeddings()
    df,paths_total_cs = calc_cosine_sim(emb,path_nodes,g_nodes,triples_df,search_type,labels_all, kg_type)

    return path_nodes,df,paths_total_cs

#Returns dictionary of data frames with all mechanisms/subgraphs with labels
def return_all_simple_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,kg_type,s,length):

    path_nodes = find_all_simple_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,False,search_type, kg_type,s,length)
    mechanism_dfs = {}
    labels_mechanisms_dfs = {}

    #Will get dictionary from define_path_triples if more than 1 path, otherwise is df
    if len(path_nodes) == 1:
        df = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
        labels_mechanisms_dfs['1'] = convert_to_labels(df,labels_all,kg_type)
    if len(path_nodes) > 1:
        #Dictionary of all triples that are shortest paths, not currently used
        mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
        for k,v in mechanism_dfs.items():
            labels_mechanisms_dfs[k] = convert_to_labels(v,labels_all,kg_type)

    return labels_mechanisms_dfs


def prioritize_path_pdp(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight, kg_type,s):

    path_nodes = find_all_shortest_paths(start_node,end_node,graph,g_nodes,labels_all,triples_df,False,search_type, kg_type,s)

    df,paths_pdp = calc_pdp(path_nodes,graph,pdp_weight,g_nodes,triples_df,search_type,labels_all, kg_type)

    return path_nodes,df,paths_pdp

# expand nodes by drugs 1 hop away
def drugNeighbors(graph,nodes, kg_type):
    neighbors = []
    if kg_type == 'kg-covid19':
        nodes = list(graph.labels_all[graph.labels_all['label'].isin(nodes)]['entity_uri'])
    for node in nodes:
        tmp_nodes = graph.igraph.neighbors(node,mode = "in")
        tmp = graph.igraph.vs(tmp_nodes)['name']
        drug_neighbors = [i for i in tmp if re.search(r'Drug|Pharm',i)]
        if len(drug_neighbors) != 0:
            for source in drug_neighbors:
                path = graph.igraph.get_shortest_paths(v = source, to = node)
                path_triples = define_path_triples(graph.igraph_nodes,graph.edgelist,path, 'all')
                path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type)
                neighbors.append(path_labels)
    all_neighbors = pd.concat(neighbors)
    return all_neighbors
    


def drug_neighbors_wrapper(input_nodes_df, subgraph_df,graph,kg_type):
    subgraph_nodes = unique_nodes(subgraph_df[['S','O']])
    all_neighbors = drugNeighbors(graph,subgraph_nodes,kg_type)
    updated_subgraph = pd.concat([subgraph_df,all_neighbors])
    for_input = pd.concat([all_neighbors[['S','O']],all_neighbors[['S','O']]],axis = 1)
    for_input.columns = ['source', 'target', 'source_label', 'target_label']
    updated_input_nodes_df = pd.concat([input_nodes_df, for_input])
    return updated_input_nodes_df, updated_subgraph


def get_node_namespace(kg_type,node_type):

    if kg_type == 'pkl':
        namespace_dict = {'microbe':'http://github.com/callahantiff/PheKnowLator/pkt/','gene':'http://www.ncbi.nlm.nih.gov/gene/','protein':'http://purl.obolibrary.org/obo/PR_','metabolite':'http://purl.obolibrary.org/obo/CHEBI_','process':'http://purl.obolibrary.org/obo/GO_','neurotransmitter':'http://purl.obolibrary.org/obo/CHEBI_','disease':'http://purl.obolibrary.org/obo/MONDO_','serotonin':'<http://purl.obolibrary.org/obo/CHEBI_28790>','depressive disorder':'<http://purl.obolibrary.org/obo/MONDO_0002050>'}
    if kg_type == 'kgx':
        namespace_dict = {'microbe':'NCBITaxon:','gene':'PR:','metabolite':'CHEBI:','process':'GO:','neurotransmitter':'CHEBI:','disease':'MONDO:'}
    if kg_type == 'uniprot_kg':
        namespace_dict = {'microbe':'NCBITaxon:','metabolite':'CHEBI:','process':'GO:','protein':'Uniprot:','disease':'MONDO:','reaction':'Rhea:'}
    
    namespace = namespace_dict[node_type]

    return namespace

#Returns all neighbors of a source node type that are a target node type with a specific edge type
def get_specific_neighbors_by_edge(count,graph,node_type1,triples_edge_type,node_type2,kg_type,type2_neighbors,search_type):

    neighbors = []
    all_type2_neighbors = []

    previous_nodes = {}

    #if direction == 'reverse':
    #    type2_neighbors = []

    #triples_edge_type = graph.edgelist.loc[graph.edgelist['predicate'] == edge]

    #Get all nodes of node_type1
    if count == 1:
        g_node_type1 = list(graph.labels_all[graph.labels_all['entity_uri'].str.contains(node_type1)]['entity_uri'])
        try:
            g_node_type1.remove('<http://github.com/callahantiff/PheKnowLator/pkt/9632542199d7d436bdb9e43a46b05929>')
        except ValueError:
            pass
        try:
            g_node_type1.remove('<http://github.com/callahantiff/PheKnowLator/pkt/93a541ff207b2f9e1d2ecf46c1f99ea4>')
        except ValueError:
            pass
    elif count > 1:
        g_node_type1 = type2_neighbors
    #t_2_nodes = 0
    #Get all neighbors of each of the nodes in this node type
    node_type2_neighbors = []
    print('searching between: ',node_type1,node_type2)
    for node in tqdm(g_node_type1):
        node_label = graph.labels_all.loc[graph.labels_all['entity_uri'] == node,'label'].values[0]
        if ~(node_type1 == 'Uniprot:' and node_type2 == 'Rhea:') | (node_type1 == 'GO:' and node_type2 == 'MONDO:') | (node_type1 == 'CHEBI:' and node_type2 == 'GO:'):
            try:
                all_triples = triples_edge_type.loc[(triples_edge_type['subject'] == node) & (triples_edge_type['object'].str.contains(node_type2))]
            except IndexError:
                continue
            #Get each neighbor of each of the nodes in this node type
            for t in range(len(all_triples)):
                path_triples = pd.DataFrame()
                df = pd.DataFrame()
                path_triples['S'] = [node]
                path_triples['P'] = [all_triples.iloc[t].loc['predicate']] #.values[0]]
                path_triples['O'] = [all_triples.iloc[t].loc['object']]
                try:
                    df['S_ID'] = [node]
                    df['P_ID'] = [path_triples['P'].values[0]]
                    df['O_ID'] = [path_triples['O'].values[0]]
                    df['S'] = [node_label]
                    df['P'] = [previous_nodes[path_triples['P'].values[0]]]
                    df['O'] = [previous_nodes[path_triples['O'].values[0]]]
                    neighbors.append(df)
                except KeyError:
                    df = pd.DataFrame()
                    path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type)
                    path_triples_new = copy.deepcopy(path_triples)
                    path_triples_new = path_triples_new.rename({'S': 'S_ID', 'P': 'P_ID','O':'O_ID'}, axis=1)
                    df = pd.concat([df,path_triples_new])
                    df = pd.concat([df,path_labels],axis=1)
                    neighbors.append(df)
                    previous_nodes[df['S_ID'].values[0]] = df['S'].values[0]
                    previous_nodes[df['P_ID'].values[0]] = df['P'].values[0]
                    previous_nodes[df['O_ID'].values[0]] = df['O'].values[0]
                node_type2_neighbors.append(all_triples.iloc[t].loc['object'])
            all_triples = pd.DataFrame()
        
            try:
                all_triples = triples_edge_type.loc[(triples_edge_type['object'] == node) & (triples_edge_type['subject'].str.contains(node_type2))]
            except IndexError:
                continue
            for t in range(len(all_triples)):
                #try:
                path_triples = pd.DataFrame()
                df = pd.DataFrame()
                path_triples['S'] = [all_triples.iloc[t].loc['subject']]
                path_triples['P'] = [all_triples.iloc[t].loc['predicate']] #.values[0]]
                path_triples['O'] = [node]#.values[0]]
                try:
                    df['S_ID'] = [path_triples['S'].values[0]]
                    df['P_ID'] = [path_triples['P'].values[0]]
                    df['O_ID'] = [node]
                    df['S'] = [previous_nodes[path_triples['S'].values[0]]]
                    df['P'] = [previous_nodes[path_triples['P'].values[0]]]
                    df['O'] = [node_label]
                    neighbors.append(df)
                except KeyError:
                    df = pd.DataFrame()
                    path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type)
                    path_triples_new = copy.deepcopy(path_triples)
                    path_triples_new = path_triples_new.rename({'S': 'S_ID', 'P': 'P_ID','O':'O_ID'}, axis=1)
                    df = pd.concat([df,path_triples_new])
                    df = pd.concat([df,path_labels],axis=1)
                    neighbors.append(df)
                    previous_nodes[df['S_ID'].values[0]] = df['S'].values[0]
                    previous_nodes[df['P_ID'].values[0]] = df['P'].values[0]
                    previous_nodes[df['O_ID'].values[0]] = df['O'].values[0]
                node_type2_neighbors.append(all_triples.iloc[t].loc['subject'])
        else:
            try:
                all_triples = triples_edge_type.loc[(triples_edge_type['object'] == node) & (triples_edge_type['subject'].str.contains(node_type2))]
            except IndexError:
                continue
            for t in range(len(all_triples)):
                #try:
                path_triples = pd.DataFrame()
                df = pd.DataFrame()
                path_triples['S'] = [all_triples.iloc[t].loc['subject']]
                path_triples['P'] = [all_triples.iloc[t].loc['predicate']] #.values[0]]
                path_triples['O'] = [node]#.values[0]]
                try:
                    df['S_ID'] = [path_triples['S'].values[0]]
                    df['P_ID'] = [path_triples['P'].values[0]]
                    df['O_ID'] = [node]
                    df['S'] = [previous_nodes[path_triples['S'].values[0]]]
                    df['P'] = [previous_nodes[path_triples['P'].values[0]]]
                    df['O'] = [node_label]
                    neighbors.append(df)
                except KeyError:
                    df = pd.DataFrame()
                    path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type)
                    path_triples_new = copy.deepcopy(path_triples)
                    path_triples_new = path_triples_new.rename({'S': 'S_ID', 'P': 'P_ID','O':'O_ID'}, axis=1)
                    df = pd.concat([df,path_triples_new])
                    df = pd.concat([df,path_labels],axis=1)
                    neighbors.append(df)
                    previous_nodes[df['S_ID'].values[0]] = df['S'].values[0]
                    previous_nodes[df['P_ID'].values[0]] = df['P'].values[0]
                    previous_nodes[df['O_ID'].values[0]] = df['O'].values[0]
                node_type2_neighbors.append(all_triples.iloc[t].loc['subject'])

    try:
        all_neighbors = pd.concat(neighbors)
    except ValueError:
        print('No edges between: ',node_type1,node_type2)
        all_neighbors = pd.DataFrame()

    #returns df of S/P/O for all neighbors
    return all_neighbors,node_type2_neighbors




#Returns all neighbors of a source node type that are a target node type with a specific edge type
def get_specific_neighbors_by_edge_removal(count,graph,node_type1,edges_list,node_type2,kg_type,type2_neighbors,search_type):

    neighbors = []
    all_type2_neighbors = []

    triples_edge_type = graph.edgelist.loc[~graph.edgelist['predicate'] == edges_list[0]]
    if len(edges_list) > 1:
        for i in edges_list:
            triples_edge_type = triples_edge_type.loc[~triples_edge_type['predicate'] == edges_list[i]]

    #Get all nodes of node_type1
    if count == 1:
        g_node_type1 = list(graph.labels_all[graph.labels_all['entity_uri'].str.contains(node_type1)]['entity_uri'])
        try:
            g_node_type1.remove('<http://github.com/callahantiff/PheKnowLator/pkt/9632542199d7d436bdb9e43a46b05929>')
        except ValueError:
            pass
        try:
            g_node_type1.remove('<http://github.com/callahantiff/PheKnowLator/pkt/93a541ff207b2f9e1d2ecf46c1f99ea4>')
        except ValueError:
            pass
    elif count > 1:
        g_node_type1 = type2_neighbors
    t_2_nodes = 0
    #Get neighbors of each of the nodes in this node type
    node_type2_neighbors = []
    for node in tqdm(g_node_type1):
        n = triples_edge_type.loc[(triples_edge_type['subject'] == node) & (graph.edgelist['object'].str.contains(node_type2)),'object'].values[0]
        node_type2_neighbors.append(n)
        if len(node_type2_neighbors) != 0:
            for l in node_type2_neighbors:
                all_type2_neighbors.append(l)
        
            for source in node_type2_neighbors:
                df = pd.DataFrame()
                path = graph.igraph.get_shortest_paths(v = source, to = node,mode=search_type)
                path_triples = define_path_triples(graph.igraph_nodes,graph.edgelist,path, search_type)
                path_triples_new = copy.deepcopy(path_triples)
                path_triples_new = path_triples_new.rename({'S': 'S_ID', 'P': 'P_ID','O':'O_ID'}, axis=1)
                #path_triples_new.columns={'S_ID','P_ID','O_ID'}
                path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type)
                df = pd.concat([df,path_triples_new])
                df = pd.concat([df,path_labels],axis=1)
                neighbors.append(df)

    try:
        all_neighbors = pd.concat(neighbors)
    except ValueError:
        print('No edges between: ',node_type1,node_type2)
        all_neighbors = pd.DataFrame()

    #returns df of S/P/O for all neighbors
    return all_neighbors,all_type2_neighbors




#Returns all neighbors of a source node type that are a target node type
def get_specific_neighbors(count,graph,node_type1,node_type2,kg_type,type2_neighbors,search_type):

    neighbors = []
    all_type2_neighbors = []

    #Get all nodes of node_type1
    if count == 1:
        g_node_type1 = list(graph.labels_all[graph.labels_all['entity_uri'].str.contains(node_type1)]['entity_uri'])
        try:
            g_node_type1.remove('<http://github.com/callahantiff/PheKnowLator/pkt/9632542199d7d436bdb9e43a46b05929>')
        except ValueError:
            pass
        try:
            g_node_type1.remove('<http://github.com/callahantiff/PheKnowLator/pkt/93a541ff207b2f9e1d2ecf46c1f99ea4>')
        except ValueError:
            pass
    elif count > 1:
        g_node_type1 = type2_neighbors
    t_2_nodes = 0
    #Get neighbors of each of the nodes in this node type
    for node in tqdm(g_node_type1):
    #for node in tqdm(g_node_type1[0:10]):
        tmp_nodes = graph.igraph.neighbors(node,mode = search_type)
        tmp = graph.igraph.vs(tmp_nodes)['name']
        node_type2_neighbors = [i for i in tmp if re.search(r'{}'.format(node_type2),i)]
        t_2_nodes += len(node_type2_neighbors)
        
        if len(node_type2_neighbors) != 0:
            for l in node_type2_neighbors:
                all_type2_neighbors.append(l)
        
            for source in node_type2_neighbors:
                df = pd.DataFrame()
                path = graph.igraph.get_shortest_paths(v = source, to = node,mode=search_type)
                path_triples = define_path_triples(graph.igraph_nodes,graph.edgelist,path, search_type)
                path_triples_new = copy.deepcopy(path_triples)
                path_triples_new = path_triples_new.rename({'S': 'S_ID', 'P': 'P_ID','O':'O_ID'}, axis=1)
                #path_triples_new.columns={'S_ID','P_ID','O_ID'}
                path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type)
                df = pd.concat([df,path_triples_new])
                df = pd.concat([df,path_labels],axis=1)
                neighbors.append(df)
        
    try:
        all_neighbors = pd.concat(neighbors)
    except ValueError:
        print('No edges between: ',node_type1,node_type2)
        all_neighbors = pd.DataFrame()

    #returns df of S/P/O for all neighbors, plus the uris of each
    return all_neighbors,all_type2_neighbors

def get_template_based_paths(template,kg_type,graph,search_type):

    df = pd.DataFrame()

    #Get first node namespace
    n_1_namespace = get_node_namespace(kg_type,template[0])
    count = 1
    type2_neighbors = []
    
    if kg_type == 'pkl':

        #Create each edge type that is needed for the template
        triples_microbe_gene_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0011016>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0011013>')]
        triples_microbe_metabolite_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == '<http://github.com/callahantiff/PheKnowLator/pkt/9632542199d7d436bdb9e43a46b05929>') | (graph.edgelist['predicate'] == '<http://github.com/callahantiff/PheKnowLator/pkt/93a541ff207b2f9e1d2ecf46c1f99ea4>')]
        triples_metabolite_gene_edge_type = graph.edgelist.loc[graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0002434>']
        triples_PR_gene_edge_type = graph.edgelist.loc[graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/pr#has_gene_template>']
        triples_gene_PR_edge_type = graph.edgelist.loc[graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0002205>']
        triples_PR_GO_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0000056>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0000085>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0002353>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/pw#part_of>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0002215>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0002331>')]
        triples_GO_MONDO_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004021>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004024>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/BFO_0000054>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/mondo#disease_triggers>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004020>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0009501>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004026>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0009501>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004028>')]
        
        triples_metabolite_disease_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004028>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/mondo#disease_responds_to>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/mondo#disease_has_basis_in_accumulation_of>') | (graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0004020>')]

        triples_GO_metabolite_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == '<http://purl.obolibrary.org/obo/RO_0002436>') & (graph.edgelist['subject'].str.contains('/CHEBI_')) & (graph.edgelist['object'].str.contains('/GO_'))]


        for n in template[1:]:
            n_namespace = get_node_namespace(kg_type,n)
            #Df of triples
            print(n_1_namespace,n_namespace)

            #For protein-gene search with specific relationships
            if n_1_namespace == 'http://purl.obolibrary.org/obo/PR_' and n_namespace == 'http://www.ncbi.nlm.nih.gov/gene/':
                print('getting neighbors from protein to gene')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_PR_gene_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For gene-protein search with specific relationships
            elif n_1_namespace == 'http://www.ncbi.nlm.nih.gov/gene/' and n_namespace == 'http://purl.obolibrary.org/obo/PR_':
                print('getting neighbors from gene to protein')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_gene_PR_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For protein-GO search, need to remove "subClassOf" edges from this- cellular components 
            elif n_1_namespace == 'http://purl.obolibrary.org/obo/PR_' and n_namespace == 'http://purl.obolibrary.org/obo/GO_' or n_1_namespace == 'http://purl.obolibrary.org/obo/GO_' and n_namespace == 'http://purl.obolibrary.org/obo/PR_':
                print('getting neighbors from protein to GO/GO-protein')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_PR_GO_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For microbe-gene search
            elif n_1_namespace == 'http://github.com/callahantiff/PheKnowLator/pkt/' and n_namespace == 'http://www.ncbi.nlm.nih.gov/gene/':
                print('getting neighbors from microbe to gene')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_microbe_gene_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For GO-Disease search
            elif n_1_namespace == 'http://purl.obolibrary.org/obo/GO_' and n_namespace == 'http://purl.obolibrary.org/obo/MONDO_':
                print('getting neighbors from go to mondo')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_GO_MONDO_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For microbe-metab search
            elif n_1_namespace == 'http://github.com/callahantiff/PheKnowLator/pkt/' and n_namespace == 'http://purl.obolibrary.org/obo/CHEBI_':
                print('getting neighbors from microbe to metab')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_microbe_metabolite_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For metab-gene search
            elif n_1_namespace == 'http://purl.obolibrary.org/obo/CHEBI_' and n_namespace == 'http://www.ncbi.nlm.nih.gov/gene/':
                print('getting neighbors from metab to gene')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_metabolite_gene_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For metab-disease search
            elif n_1_namespace == 'http://purl.obolibrary.org/obo/CHEBI_' and n_namespace == 'http://purl.obolibrary.org/obo/MONDO_':
                print('getting neighbors from metab to gene')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_metabolite_disease_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For go-metab search
            elif n_1_namespace == 'http://purl.obolibrary.org/obo/GO_' and n_namespace == 'http://purl.obolibrary.org/obo/CHEBI_':
                print('getting neighbors from process to metab')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_GO_metabolite_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            else:
                print('in get_specific_neighbors')
                n_neighbors_df,type2_neighbors = get_specific_neighbors(count,graph,n_1_namespace,n_namespace,kg_type,type2_neighbors,search_type)

            df = pd.concat([df,n_neighbors_df],axis=0)
            n_1_namespace = n_namespace
            count += 1

    elif kg_type == 'uniprot_kg':   

        #Create each edge type that is needed for the template 
        triples_microbe_protein_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == 'expresses')]
        triples_reaction_protein_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == 'catalysed_by')]
        triples_reaction_process_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == 'affects')]
        triples_disease_process_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == 'biolink:has_participant')]
        triples_process_chemical_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == 'biolink:has_participant')]
        triples_reaction_chemical_edge_type = graph.edgelist.loc[(graph.edgelist['predicate'] == 'has_cofactor')]

        print(len(triples_microbe_protein_edge_type))

        for n in template[1:]:
            n_namespace = get_node_namespace(kg_type,n)
            #Df of triples
            print(n_1_namespace,n_namespace)

            #['microbe','protein','reaction','process','disease'] # ['microbe','protein','reaction','chemical','process','disease'] ]

            #For protein-gene search with specific relationships
            if n_1_namespace == 'NCBITaxon:' and n_namespace == 'Uniprot:':
                print('getting neighbors from microbe to protein')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_microbe_protein_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For reaction-protein search with specific relationships
            elif n_1_namespace == 'Uniprot:' and n_namespace == 'Rhea:': #reverse
                print('getting neighbors from reaction to protein')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_reaction_protein_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For reaction-process search with specific relationships
            elif n_1_namespace == 'Rhea:' and n_namespace == 'GO:':
                print('getting neighbors from reaction to process')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_reaction_process_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For disease-process search with specific relationships
            elif n_1_namespace == 'GO:' and n_namespace == 'MONDO:': #reverse
                print('getting neighbors from disease to process')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_disease_process_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For process-chemical search with specific relationships
            #Sometimes forward, sometimes reverse so CHECK
            elif n_1_namespace == 'CHEBI:' and n_namespace == 'GO:': #reverse
                print('getting neighbors from process to chemical')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_process_chemical_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            #For reaction-chemical search with specific relationships
            elif n_1_namespace == 'Rhea:' and n_namespace == 'CHEBI:':
                print('getting neighbors from reaction to chemical')
                n_neighbors_df,type2_neighbors = get_specific_neighbors_by_edge(count,graph,n_1_namespace,triples_reaction_chemical_edge_type,n_namespace,kg_type,type2_neighbors,search_type)
            else:
                print('in get_specific_neighbors')
                n_neighbors_df,type2_neighbors = get_specific_neighbors(count,graph,n_1_namespace,n_namespace,kg_type,type2_neighbors,search_type)
        
            df = pd.concat([df,n_neighbors_df],axis=0)
            n_1_namespace = n_namespace
            count += 1
        
    return df

def template_based_subgraph_output(output_dir,kg_type,template,template_df,subfolder_name):

    #Takes in a file that shows all triples among a specific pattern, creates all the separate path files, and then evaluates the content of them by creating a histogram per category

    #length of templates - i.e. 7, so need 7 pairs (0,1 , 1,2 , 2,3 , 3,4 , 4,5 , 5,6 , 6,7)
    path_length = len(template)

    search_type = 'all'

    #Template df has duplicate rows
    template_df.drop_duplicates(inplace=True)

    triples_df = template_df[['S_ID','P_ID','O_ID']]
    triples_df = triples_df.rename({'S_ID': 'subject', 'P_ID': 'predicate','O_ID':'object'}, axis=1)

    #Create a smaller labels df in order to create igraph object
    labels = pd.DataFrame()

    a = []
    for i in range(len(template_df)):
        df = pd.DataFrame()
        if template_df.iloc[i].loc['S_ID'] not in a:
            df['entity_uri'] = [template_df.iloc[i].loc['S_ID']]
            df['label'] = [template_df.iloc[i].loc['S']]
            labels = pd.concat([labels,df],axis=0)
            a.append(template_df.iloc[i].loc['S_ID'])
        df = pd.DataFrame()
        if template_df.iloc[i].loc['P_ID'] not in a:
            df['entity_uri'] = [template_df.iloc[i].loc['P_ID']]
            df['label'] = [template_df.iloc[i].loc['P']]
            labels = pd.concat([labels,df],axis=0)
            a.append(template_df.iloc[i].loc['P_ID'])
        df = pd.DataFrame()
        if template_df.iloc[i].loc['O_ID'] not in a:
            df['entity_uri'] = [template_df.iloc[i].loc['O_ID']]
            df['label'] = [template_df.iloc[i].loc['O']]
            labels = pd.concat([labels,df],axis=0)
            a.append(template_df.iloc[i].loc['O_ID'])


    g_igraph,g_nodes_igraph = create_igraph_graph(triples_df,labels)
    g = KnowledgeGraph(triples_df,labels,g_igraph,g_nodes_igraph)

    unique_types = {}
    if kg_type == 'pkl':
        for i in range(len(template_df)):
            if '<http://github.com/callahantiff/PheKnowLator/pkt' in template_df.iloc[i].loc['S_ID']:
                if '<http://github.com/callahantiff/PheKnowLator/pkt' not in unique_types.keys():
                    unique_types['<http://github.com/callahantiff/PheKnowLator/pkt'] = 'S'
            elif '<http://github.com/callahantiff/PheKnowLator/pkt' in template_df.iloc[i].loc['O_ID']:
                if '<http://github.com/callahantiff/PheKnowLator/pkt' not in unique_types.keys():
                    unique_types['<http://github.com/callahantiff/PheKnowLator/pkt'] = 'O'
            elif '<http://www.ncbi.nlm.nih.gov/gene/' in template_df.iloc[i].loc['S_ID']:
                if '<http://www.ncbi.nlm.nih.gov/gene/' not in unique_types.keys():
                    unique_types['<http://www.ncbi.nlm.nih.gov/gene/'] = 'S'
            elif '<http://www.ncbi.nlm.nih.gov/gene/' in template_df.iloc[i].loc['O_ID']:
                if '<http://www.ncbi.nlm.nih.gov/gene/' not in unique_types.keys():
                    unique_types['<http://www.ncbi.nlm.nih.gov/gene/'] = 'O'
            else:
                if template_df.iloc[i].loc['S_ID'].split('<http://purl.obolibrary.org/obo/')[1].split('_')[0] not in unique_types.keys():
                    unique_types[template_df.iloc[i].loc['S_ID'].split('<http://purl.obolibrary.org/obo/')[1].split('_')[0]] = 'S'
                if template_df.iloc[i].loc['O_ID'].split('<http://purl.obolibrary.org/obo/')[1].split('_')[0] not in unique_types.keys():
                    unique_types[template_df.iloc[i].loc['O_ID'].split('<http://purl.obolibrary.org/obo/')[1].split('_')[0]] = 'O'

    elif kg_type != 'pkl':
        for i in range(len(template_df)):
            if template_df.iloc[i].loc['S_ID'].split(':')[0] not in unique_types.keys():
                unique_types[template_df.iloc[i].loc['S_ID'].split(':')[0]] = 'S'
            if template_df.iloc[i].loc['O_ID'].split(':')[0] not in unique_types.keys():
                unique_types[template_df.iloc[i].loc['O_ID'].split(':')[0]] = 'O'

    print(unique_types)

    start_nodes = template_df.loc[template_df[list(unique_types.values())[0]+'_ID'].str.contains(list(unique_types.keys())[0])]
    start_nodes = list(start_nodes[list(unique_types.values())[0]])
    end_nodes = template_df.loc[template_df[unique_types['MONDO']+'_ID'].str.contains('MONDO')]
    end_nodes = list(end_nodes[list(unique_types.values())[len(unique_types)-1]])


    #Not allow duplicates
    list_of_mechs = []


    print("Finding subgraphs for template based using all shortest path search......")

    template = '_'.join(map(str,template))

    for s in tqdm(start_nodes):
        for o in end_nodes:

            subgraph_dict = return_all_simple_paths(s,o,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,None,search_type,kg_type,s,path_length)  

            if len(subgraph_dict) > 0:
                count = 1
                for k,v, in subgraph_dict.items():
                    df = v

                    # Define output filenames for s
                    source_name = df.iloc[0].loc['S'] 
                    source_name = source_name.replace('CONTEXTUAL ','')
                    source_name = source_name.replace(' ','_')
                    source_name = source_name.replace(':','_')
                    target_name = df.iloc[-1].loc['O']
                    target_name = target_name.replace(' ','_')

                    cs_noa_df = output_visualization(pd.DataFrame(),source_name,target_name+'_'+str(count),df,output_dir + '/' + subfolder_name + '/' + template)
                    count += 1



