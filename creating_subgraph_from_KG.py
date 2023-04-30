from inputs import *
from create_graph import create_graph
from assign_nodes import interactive_search_wrapper
from create_subgraph import automatic_defined_edge_exclusion
from visualize_subgraph import output_visualization
from evaluation import *
from graph_experiments import *
from find_path import get_template_based_paths
import ast
from collections import defaultdict
import tqdm as tqdm
import random

def main():

    '''
    microbe_phenio_triples_file = '/Users/brooksantangelo/Documents/HunterLab/Exploration/kg_microbe_phenio/output_data/merged-kg/kgx_merged-kg_edges.tsv'
    microbe_phenio_labels_file = '/Users/brooksantangelo/Documents/HunterLab/Exploration/kg_microbe_phenio/output_data/merged-kg/kgx_merged-kg_nodes.tsv'

    mgmlink_triples_file = '/Users/brooksantangelo/Documents/HunterLab/MGMLink/git/MGMLink/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'
    mgmlink_labels_file = '/Users/brooksantangelo/Documents/HunterLab/MGMLink/git/MGMLink/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels_NewEntities.txt'

    mikg4md_relations_file = '/Users/brooksantangelo/Documents/HunterLab/ISMB2023/Mikg4md_experiment/Microbe_Neurotransmitter_MentalDisorder_EvidenceAB.csv'
    '''

    input_dir,output_dir,kg_types,embedding_dimensions,weights,search_type,pdp_weight,experiment_type,input_type = generate_arguments()

    kg_types = ast.literal_eval(kg_types)

    for kg_type in kg_types:
        triples_list_file,labels_file,input_file = get_graph_files(input_dir,output_dir, kg_type, input_type)


    
        #embedding_dimensions = 128
        #weights = True
        #search_type = 'all'
        #pdp_weight = 0.4

        print("Creating knowledge graph object from inputs.....")

        #if kg_type == 'kg-covid19':
        #    continue
        path_nums_dict = {}
        print('Graph: ',kg_type)

        g = create_graph(triples_list_file,labels_file, kg_type)

        if weights == True:
            #Want to exclude the biolink:category, biolink:in_taxon, MAYBE biolink:related_to, biolink:part_of
            #Want to exclude the <http://purl.obolibrary.org/obo/RO_0002160> - only in taxon, <http://purl.obolibrary.org/obo/BFO_0000050> - part of, <http://purl.obolibrary.org/obo/RO_0001025> - located in
            #Want to exclude type edge for mikg4md
            g = automatic_defined_edge_exclusion(g,kg_type)
        
        if input_type == 'file':
            #Input file will have one microbe, one disease
            s = interactive_search_wrapper(g,input_file,output_dir,kg_type,experiment_type,input_type,pd.DataFrame()) #experiment_paths)


        if experiment_type == 'one_path':
            if input_type == 'file':
                #Update to do all shortest paths search
                one_path_search(s,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,search_type,triples_list_file,output_dir,kg_type)
            if input_type != 'file':
                #Find all microbe to disease pairs
                if kg_type != 'pkl':
                    microbes = g.labels_all['entity_uri'][g.labels_all['entity_uri'].str.contains('NCBITaxon:')].values.tolist()
                    diseases = g.labels_all['entity_uri'][g.labels_all['entity_uri'].str.contains('MONDO:')].values.tolist()
                if kg_type == 'pkl':
                    microbes = g.labels_all['label'][g.labels_all['label'].str.contains('CONTEXTUAL ')].values.tolist()
                    microbes = [get_uri(g.labels_all,i,kg_type,pd.DataFrame()) for i in microbes]
                    random.seed(4)
                    microbes = random.choices(microbes, k=193)
                    diseases = g.labels_all['entity_uri'][g.labels_all['entity_uri'].str.contains('MONDO_')].values.tolist()
                    diseases = random.choices(diseases, k=32)
                print(len(microbes),len(diseases))

                for m in tqdm.tqdm(microbes):
                    for d in diseases:
                        all_pairs = {}
                        all_pairs['source'] = m 
                        all_pairs['target'] = d 
                        input_df = pd.DataFrame.from_dict([all_pairs])
                        s = interactive_search_wrapper(g,input_file,output_dir,kg_type,experiment_type,input_type,input_df)
                        one_path_search(s,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,search_type,triples_list_file,output_dir,kg_type)

        elif experiment_type == 'two_paths':
            #Update to do all shortest paths search
            two_path_search(s,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,search_type,triples_list_file,output_dir,kg_type)
        elif experiment_type == 'template_based':
            template_based_search(kg_type, g, search_type,output_dir)



        ###DO I want to search all shortest path for 1 microbe-disease pair, defined in input_file, or do I want to search the shortest path for all microbe-diesease pairs, which I would have to derive from the KG itself like I did from MIkg4md for ISMB Paper --> maybe just do that again for this KG

        #For now, just do one microbe-one disease and find all shortest paths

        #############
        #Need to update


if __name__ == '__main__':
    main()