import pandas as pd
from find_path import return_all_simple_paths, get_node_namespace
from visualize_subgraph import output_visualization
from create_graph import create_igraph_graph,create_graph
from graph import KnowledgeGraph
from tqdm import tqdm


#Takes in a file that shows all triples among a specific pattern, creates all the separate path files, and then evaluates the content of them by creating a histogram per category


output_dir = '/Users/brooksantangelo/Documents/HunterLab/ISMB2023/Experiment2/pkl_all_template_based'

#length of templates - i.e. 7, so need 7 pairs (0,1 , 1,2 , 2,3 , 3,4 , 4,5 , 5,6 , 6,7)
path_length = 7

template_file = output_dir+ '/microbe_metabolite_gene_protein_process_metabolite_disease__Subgraph_X.csv' #'/microbe_metabolite_process_disease__Subgraph.csv' #
kg_type = 'pkl'

search_type = 'all'

template_df = pd.read_csv(template_file,sep='|')
#Template df has duplicate rows
template_df.drop_duplicates(inplace=True)

triples_df = template_df[['S_ID','P_ID','O_ID']]
triples_df = triples_df.rename({'S_ID': 'subject', 'P_ID': 'predicate','O_ID':'object'}, axis=1)


labels = pd.DataFrame()

a = []
for i in range(len(template_df)):
    df = pd.DataFrame()
    if template_df.iloc[i].loc['S_ID'] not in a:
        df['id'] = [template_df.iloc[i].loc['S_ID']]
        df['label'] = [template_df.iloc[i].loc['S']]
        labels = pd.concat([labels,df],axis=0)
        a.append(template_df.iloc[i].loc['S_ID'])
    df = pd.DataFrame()
    if template_df.iloc[i].loc['P_ID'] not in a:
        df['id'] = [template_df.iloc[i].loc['P_ID']]
        df['label'] = [template_df.iloc[i].loc['P']]
        labels = pd.concat([labels,df],axis=0)
        a.append(template_df.iloc[i].loc['P_ID'])
    df = pd.DataFrame()
    if template_df.iloc[i].loc['O_ID'] not in a:
        df['id'] = [template_df.iloc[i].loc['O_ID']]
        df['label'] = [template_df.iloc[i].loc['O']]
        labels = pd.concat([labels,df],axis=0)
        a.append(template_df.iloc[i].loc['O_ID'])


g_igraph,g_nodes_igraph = create_igraph_graph(triples_df,labels)
g = KnowledgeGraph(triples_df,labels,g_igraph,g_nodes_igraph)

unique_types = {}
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

print(unique_types)

start_nodes = template_df.loc[template_df[list(unique_types.values())[0]+'_ID'].str.contains(list(unique_types.keys())[0])]
start_nodes = list(start_nodes[list(unique_types.values())[0]])
end_nodes = template_df.loc[template_df[unique_types['MONDO']+'_ID'].str.contains('MONDO')]
end_nodes = list(end_nodes[list(unique_types.values())[len(unique_types)-1]])


#Not allow duplicates
list_of_mechs = []


print("Finding subgraphs all shortest path search......")

for s in tqdm(start_nodes):
    for o in end_nodes:
        print(s,o)

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

                cs_noa_df = output_visualization(source_name,target_name+'_'+str(count),df,output_dir+'/microbe_metabolite_gene_protein_process_metabolite_disease_X_paths')
                count += 1
