
#Outputs the patterns of nodes that describe the shortest path between a specific set of pairs (microbe - metabolie). Skim only lists each node type once, full lists every occurance of a node type in the shortest path found. 

import csv
import pandas as pd
import argparse
import os
import glob
from collections import Counter
from create_graph import create_graph
from collections import defaultdict


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--directory",dest="Directory",required=True,help="Directory")
    parser.add_argument("--graph-type",dest="GraphType",required=True,help="GraphType")
    parser.add_argument("--full-or-skim",dest='FullOrSkim',required=False,help="FullOrSkim",default='skim')
    parser.add_argument("--output-patterns",dest='OutputPatterns',required=False,help="OutputPatterns",default=True)

    return parser

###Read in all files
def process_files(csv_file,labels_df,full_or_skim,ont_types,output_patterns):

    pathway_df = pd.read_csv(csv_file,sep='|')
    print(csv_file)

    #Only return pattern if it exists
    if len(pathway_df) > 0:

        if full_or_skim == 'skim':

            
            #### To look at content of all paths easily ####
            if not output_patterns:
                pattern = pathway_df.iloc[0].loc['S']  #'P']  for checking edge types

                for i in range(0,len(pathway_df)):
                    if pathway_df.iloc[i].loc['S'] not in pattern:   #'P'] not in pattern:
                        pattern = pattern + " --- " + pathway_df.iloc[i].loc['S']  #'P']
                    if pathway_df.iloc[i].loc['O'] not in pattern:   #'P'] not in pattern:
                        pattern = pattern + " --- " + pathway_df.iloc[i].loc['O']  #'P']

            
            if output_patterns:
                #### To look at patterns of paths ###
                pattern = check_ont_type(pathway_df.iloc[0].loc['S'],ont_types,labels_df)  

                for i in range(0,len(pathway_df)):
                    if check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df) not in pattern:   
                        pattern = pattern + " --- " + check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df) 
                    if check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df) not in pattern:   
                        pattern = pattern + " --- " + check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df) 

                #alphabetize order of patterns so that there are no duplicates, only interested in the content not the order
                i_list = sorted(pattern.split(' --- '))
                pattern = i_list[0]
                for i in range(1,len(i_list)):
                    pattern = pattern + " --- " + i_list[i]

                #Add final node in pattern
                #print('final node: ',pathway_df.iloc[len(pathway_df)-1].loc['O'])
                #if check_ont_type(pathway_df.iloc[len(pathway_df)-1].loc['O'],ont_types,labels_df) not in pattern:
                #    pattern = pattern + " --- " + check_ont_type(pathway_df.iloc[len(pathway_df)-1].loc['O'],ont_types,labels_df)            
            
        elif full_or_skim == 'full':

            pattern = check_ont_type(pathway_df.iloc[0].loc['S'],ont_types,labels_df) + " --- " + pathway_df.iloc[0].loc['P'] + " --- " + check_ont_type(pathway_df.iloc[0].loc['O'],ont_types,labels_df)

            for i in range(1,len(pathway_df)):
                #print(pathway_df.iloc[i].loc['O'],pathway_df.iloc[i].loc['O'])
                #print(check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df))
                new_triple = " --- " + pathway_df.iloc[i].loc['P'] + " --- " + check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df)
                pattern = pattern + new_triple

    else:
        pattern = 'none'
        
    name = csv_file.split('.csv')[0]

    return pattern,name

def check_ont_type(node,ont_types,labels_df):

    label = labels_df.loc[labels_df['label'] == node,'id'].values[0]
    for i in list(ont_types.keys()):
        if i in label:
            return ont_types[i]


def get_path_length(csv_file):

    pathway_df = pd.read_csv(csv_file,sep='|')

    path_length = len(pathway_df)

    return path_length


def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    
    directory = args.Directory
    graph_type = args.GraphType
    full_or_skim = args.FullOrSkim
    output_patterns = args.OutputPatterns

    microbe_phenio_triples_file = '/Users/brooksantangelo/Documents/HunterLab/Exploration/kg_microbe_phenio/output_data/merged-kg/kgx_merged-kg_edges.tsv'
    microbe_phenio_labels_file = '/Users/brooksantangelo/Documents/HunterLab/Exploration/kg_microbe_phenio/output_data/merged-kg/kgx_merged-kg_nodes.tsv'

    mgmlink_triples_file = '/Users/brooksantangelo/Documents/HunterLab/MGMLink/git/MGMLink/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'
    mgmlink_labels_file = '/Users/brooksantangelo/Documents/HunterLab/MGMLink/git/MGMLink/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels_NewEntities.txt'

    if graph_type == 'kg-covid19':
        graph = [microbe_phenio_triples_file,microbe_phenio_labels_file]
        ont_types = {'CHEBI:':'CHEBI','PR:':'PRO','MONDO:':'MONDO','/hgnc/':'hgnc','CL:':'CLO','CARO:':'CARO','BSPO:':'BSPO','NCBITaxon:':'NCBITaxon/ContextualMicrobe','BTO:':'BTO','GO:':'GO','CHR:':'CHR','FBbt:':'FBbt','FMA:':'FMA','HP:':'HPO','MA:':'MA','MP:':'MPO','OBA:':'OBA','PATO:':'PATO','PLANA:':'PLANA','UBERON:':'UBERON','UPHENO:':'UPHENO','WBbt:':'WBbt','ZP:':'ZP','ENSEMBL:':'ENSEMBL','CHEMBL.':'CHEMBL','NBO:':'MONDO','ENVO:':'ENVO','ECOCORE:':'ECOCORE','MFOMD:':'MONDO','BFO:':'BFO'}
    
    if graph_type == 'pkl':
        graph = [mgmlink_triples_file,mgmlink_labels_file]
        ont_types = {'pkt/':'NCBITaxon/ContextualMicrobe','/CHEBI_':'CHEBI','/PR_':'PRO','/PW_':'REACTOME_PW','/gene':'gene','/MONDO_':'MONDO','/HP_':'HPO','/VO_':'vaccine entity','/EFO_':'EFO','FAKEURI_':'other chemical','NCBITaxon_':'NCBITaxon/ContextualMicrobe','/GO_':'GO','/DOID_':'MONDO','NBO_':'MONDO'}
    

    g = create_graph(graph[0],graph[1])
    
    csv_files = glob.glob(os.path.join(directory, "*Subgraph*.csv"))

    patterns_all = []
    names_all = []
    path_lengths = defaultdict(list)
    

    for f in csv_files:

        pattern,name = process_files(f,g.labels_all,full_or_skim,ont_types,output_patterns)
        path_length = get_path_length(f)
        if pattern != 'none':
            patterns_all.append(pattern)
            path_lengths[pattern].append(path_length)
            names_all.append(name)

    #Get count of each pattern
    patterns_count = dict(Counter(patterns_all))

    #Create df of Pattern/Name/count
    patterns_all_df = pd.DataFrame({'Pattern':patterns_all})
    patterns_all_df['Name'] = names_all
    counts = []
    for i in range(len(patterns_all_df)):
        counts.append(patterns_count[patterns_all_df.iloc[i].loc['Pattern']])
        #d = {}
        #p = patterns_all_df.iloc[i].loc['Pattern']
        #d['Count'] = patterns_count[p]

        #patterns_all_df = patterns_all_df.append(d,ignore_index=True)

    path_lengths_str = []
    patterns_all_df['Count'] = counts
    for i in range(len(patterns_all_df)):
        p = patterns_all_df.iloc[i].loc['Pattern']
        p_str = ','.join(map(str,path_lengths[p]))
        path_lengths_str.append(p_str)
    patterns_all_df['Path_Length'] = path_lengths_str
    patterns_all_df = patterns_all_df.sort_values(by=['Pattern','Count'])
    #patterns_df = pd.DataFrame.from_dict(patterns_count, orient='index',columns = ['Count'])
    #patterns_df.reset_index(inplace=True)
    #patterns_df = patterns_df.rename(columns = {'index':'Pattern'})

    #Generate df of only the patterns/no filename to get unique patterns
    patterns_all_unique = patterns_all_df.Pattern.drop_duplicates()


    if full_or_skim == 'skim':
        patterns_all_df.to_csv(directory+'/PathLabel_Counts_Skim.csv',sep=',',index=False)  #Patterns_ #PathLabel_ if outputting the actual paths, not the patterns
        patterns_all_unique.to_csv(directory+'/PathLabel_Counts_Skim_Unique.csv',sep=',',index=False) #Patterns_ #PathLabel_ if outputting the actual paths, not the patterns
    elif full_or_skim == 'full':
        patterns_all_df.to_csv(directory+'/Pattern_Counts_Full.csv',sep=',',index=False)
        patterns_all_unique.to_csv(directory+'/Pattern_Counts_Full_Unique.csv',sep=',',index=False)

if __name__ == '__main__':
    main()