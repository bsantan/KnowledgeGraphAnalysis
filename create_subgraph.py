# Given a starting graph of node pairs, find all paths between them to create a subgraph
from find_path import find_shortest_path
from find_path import prioritize_path_cs
from find_path import prioritize_path_pdp
import pandas as pd
from tqdm import tqdm
from evaluation import output_path_lists
from evaluation import output_num_paths_pairs

def subgraph_shortest_path(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,kg_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in range(len(input_nodes_df)):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        shortest_path_df = find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,kg_type,input_nodes_df)
        all_paths.append(shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    return df

# Have user define weights to upweight
def user_defined_edge_weights(graph, triples_df,kg_type ):
    if kg_type == 'pkl':
        #If manually adding edges to remove
        edges = graph.labels_all[graph.labels_all['entity_type'] == 'RELATIONS'].label.tolist()
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_weight= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done."')
        while(still_adding):
            user_input = input('Edge or "Done": ')
            if user_input == 'Done':
                still_adding = False
            else:
                to_weight.append(user_input)
        to_weight = graph.labels_all[graph.labels_all['label'].isin(to_weight)]['entity_uri'].tolist()
        


    if kg_type == 'kg-covid19':
        edges = set(list(graph.igraph.es['predicate']))
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_weight= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done"')
        while(still_adding):
            user_input = input('Edge or "Done"')
            if user_input == 'Done':
                still_adding = False
            else:
                to_weight.append(user_input)

    edges= graph.igraph.es['predicate']
    graph.igraph.es['weight'] = [10 if x in to_weight else 1 for x in edges]
    return(graph)

# Have user define weights to upweight
def user_defined_edge_exclusion(graph,kg_type ):
    '''
    if kg_type == 'pkl':
        #If manually adding edges to remove
        continuing = True
        try:
            edges = graph.labels_all[graph.labels_all['entity_type'] == 'RELATIONS'].label.tolist()
        except KeyError:
            print('Issue with edge weight generation - pkl')
            continuing = False
            pass
        if continuing:
            print("### Unique Edges in Knowledge Graph ###")
            print('\n'.join(edges))
            still_adding = True
            to_drop= []
            print('\n')
            print('Input the edges to avoid in the path search (if possible). When finished input "Done."')
            while(still_adding):
                user_input = input('Edge or "Done": ')
                if user_input == 'Done':
                    still_adding = False
                else:
                    to_drop.append(user_input)
            to_drop = graph.labels_all[graph.labels_all['label'].isin(to_drop)]['entity_uri'].tolist()
 
    if kg_type == 'kg-covid19' or kg_type == 'pkl' or kg_type == 'mikg4md':
        
        #If manually adding edges to drop
        continuing = True
        try:
            edges = set(list(graph.igraph.es['predicate']))
        except KeyError:
            print('Issue with edge weight generation - kg-covid19')
            continuing = False
            pass
        if continuing:
            print(edges)
            print(len(edges))
            print("### Unique Edges in Knowledge Graph ###")
            print('\n'.join(edges))
            still_adding = True
            to_drop= []
            print('\n')
            print('Input the edges to avoid in the path search (if possible). When finished input "Done"')
            while(still_adding):
                user_input = input('Edge or "Done"')
                if user_input == 'Done':
                    still_adding = False
                else:
                    to_drop.append(user_input)
        '''

    #If not manually adding edges to remove:
    if kg_type == 'pkl':
        to_drop = ['<http://purl.obolibrary.org/obo/RO_0002160>','<http://purl.obolibrary.org/obo/BFO_0000050>','<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>']
    if kg_type == 'kg-covid19':
        to_drop = ['biolink:category','biolink:in_taxon']
    for edge in to_drop:
        graph.igraph.delete_edges(graph.igraph.es.select(predicate = edge))
    return(graph)


def user_defined_node_exclusion(graph,kg_type):

    #If not manually adding edges to remove:
    if kg_type == 'pkl':
        to_drop = ['<http://purl.obolibrary.org/obo/RO_0002160>','<http://purl.obolibrary.org/obo/BFO_0000050>','<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>']
    if kg_type == 'kg-covid19':
        to_drop = ['MONDO:0000001']
    for edge in to_drop:
        graph.igraph.delete_vertices(graph.igraph.vs.select(predicate = node))
    return(graph)

    
def subgraph_prioritized_path_cs(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        path_nodes,cs_shortest_path_df,paths_total_cs = prioritize_path_cs(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,
        search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type,input_nodes_df)
        all_paths.append(cs_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        output_path_lists(output_dir,paths_total_cs,'CosineSimilarity',i)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,'CosineSimilarity')

    return df,paths_total_cs

def subgraph_prioritized_path_pdp(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight,output_dir, kg_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        path_nodes,pdp_shortest_path_df,paths_pdp = prioritize_path_pdp(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight,kg_type,input_nodes_df)
        all_paths.append(pdp_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        output_path_lists(output_dir,paths_pdp,'PDP',i)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,'PDP')

    return df,paths_pdp
