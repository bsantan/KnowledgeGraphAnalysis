

from inputs import *
from create_graph import create_graph
from create_subgraph import subgraph_shortest_path
from visualize_subgraph import output_visualization
from evaluation import *

def check_for_existance(source_node,target_node,output_dir):

    filename = output_dir+"/"+source_node+"_"+target_node+"_Subgraph.csv"

    print('checking for existance of : ',filename)

    #Check for existence of output directory
    if not os.path.exists(filename):
        exists = 'false'
    else:
        exists = 'true'

    print(exists)
    return exists


def get_nodes_from_input(input_df,s):

    print(input_df)

    #Add only first row if length is 1
    if len(input_df) == 1:
        df = pd.DataFrame()
        df['source_label'] = [s.loc[s['source'] == input_df.iloc[0].loc['source'],'source_label'].values[0]]
        df['target_label'] = [s.loc[s['target'] == input_df.iloc[0].loc['target'],'target_label'].values[0]]
        input_df = pd.concat([input_df,df],axis=1)

    #Add other rows if there is more than 1
    elif len(input_df) > 1:
        df = pd.DataFrame()
        s1 = [s.loc[s['source'] == input_df.iloc[0].loc['source'],'source_label'].values[0]]
        t1 = [s.loc[s['target'] == input_df.iloc[0].loc['target'],'target_label'].values[0]]
        s2 = [s.loc[s['source'] == input_df.iloc[1].loc['source'],'source_label'].values[0]]
        t2 = [s.loc[s['target'] == input_df.iloc[1].loc['target'],'target_label'].values[0]]
        df['source_label'] = s1 + s2
        df['target_label'] = t1 + t2
        input_df = pd.concat([input_df,df],axis=1)

    print('new input df: ',input_df)
    return input_df

#input_df is the selected nodes we want to search, s is the original mapped file with all source/target/source_label
def one_path_search(input_df,s,igraph,igraph_nodes,labels_all,edgelist,weights,search_type,triples_file,output_dir,embedding_dimensions,kg_type,pdp_weight):

    input_df = get_nodes_from_input(input_df,s)

    print('one_path_search input df: ',input_df)

    # Define output filenames for s
    source_name = input_df.iloc[0].loc['source_label'] 
    source_name = source_name.replace('CONTEXTUAL ','')
    source_name = source_name.replace(' ','_')
    source_name = source_name.replace(':','_')
    target_name = input_df.iloc[0].loc['target_label']
    target_name = target_name.replace(' ','_')
    
    print("Finding subgraph using user input and 1 shortest path......")

    exists = check_for_existance(source_name,target_name,output_dir+'/' + kg_type+'_shortest_path')

    if exists == 'false':

        subgraph_sp = subgraph_shortest_path(input_df,igraph,igraph_nodes,labels_all,edgelist,False,search_type,kg_type)

        print("Outputting CS visualization......")

        cs_noa_df = output_visualization(source_name,target_name,subgraph_sp,output_dir+'/' + kg_type+'_shortest_path')


def two_path_search(input_df,s,igraph,igraph_nodes,labels_all,edgelist,weights,search_type,triples_file,output_dir,embedding_dimensions,kg_type,pdp_weight):

    input_df = get_nodes_from_input(input_df,s)

    # Define output filenames for s
    source_name = input_df.iloc[0].loc['source_label'] 
    source_name = source_name.replace('CONTEXTUAL ','')
    source_name = source_name.replace(' ','_')
    source_name = source_name.replace(':','_')
    middle_name = input_df.iloc[0].loc['target_label']
    middle_name = middle_name.replace(' ','_')
    target_name = input_df.iloc[1].loc['target_label']
    target_name = target_name.replace(' ','_')
    target_name = middle_name+'_'+target_name


    print("Finding subgraph using user input and 1 shortest path......")

    exists = check_for_existance(source_name,target_name,output_dir+'/' + kg_type+'_shortest_path')

    if exists == 'false':

        subgraph_sp = subgraph_shortest_path(input_df,igraph,igraph_nodes,labels_all,edgelist,False,search_type,kg_type)

        print("Outputting CS visualization......")

        cs_noa_df = output_visualization(source_name,target_name,subgraph_sp,output_dir+'/' + kg_type+'_shortest_path')
