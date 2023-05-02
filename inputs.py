import argparse
import os

#Define arguments for each required and optional input
def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ## Required inputs
    parser.add_argument("--input-dir",dest="InputDir",required=True,help="InputDir")

    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")

    parser.add_argument("--knowledge-graphs",dest="KGs",required=True,help="Knowledge Graph: either 'pkl' for PheKnowLator or 'kg-covid19' for KG-Covid19, enter as list")

    ## Optional inputs
    parser.add_argument("--embedding-dimensions",dest="EmbeddingDimensions",required=False,default=128,help="EmbeddingDimensions")

    parser.add_argument("--weights",dest="Weights",required=False,help="Weights", type = bool, default = True)

    parser.add_argument("--search-type",dest="SearchType",required=False,default='all',help="SearchType")

    parser.add_argument("--pdp-weight",dest="PdpWeight",required=False,default=0.4,help="PdpWeight")

    parser.add_argument("--experiment-type",dest="ExperimentType",required=False,default='one_path',help="ExperimentType")

    parser.add_argument("--input-type",dest="InputType",required=False,default='file',help="InputType")

    return parser

# Wrapper function
def generate_arguments():

    #Generate argument parser and define arguments
    parser = define_arguments()
    args = parser.parse_args()

    input_dir = args.InputDir
    output_dir = args.OutputDir
    kg_types = args.KGs
    embedding_dimensions = args.EmbeddingDimensions
    weights = args.Weights
    search_type = args.SearchType
    pdp_weight = args.PdpWeight
    experiment_type = args.ExperimentType
    input_type = args.InputType

    return input_dir,output_dir,kg_types,embedding_dimensions,weights,search_type,pdp_weight,experiment_type,input_type

def get_graph_files(input_dir,output_dir, kg_type, input_type):

    if kg_type == "pkl":
        existence_dict = {
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':'false',
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':'false',
            '_search_input':'false',
        }

        for fname in os.listdir(input_dir):
            if '_search_input' in fname:
                input_file = input_dir + '/' + fname
                existence_dict['_search_input'] = 'true'

        for k in list(existence_dict.keys()):
            for fname in os.listdir(input_dir + '/' + kg_type):
                if k in fname:
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':
                        labels_file = input_dir + '/' + kg_type + '/' + fname
                    existence_dict[k] = 'true'

    if kg_type != "pkl":
        existence_dict = {
            'merged-kg_edges':'false',
            'merged-kg_nodes':'false',
            '_search_input':'false',
        }

        for fname in os.listdir(input_dir):
            if '_search_input' in fname:
                input_file = input_dir + '/' + fname
                existence_dict['_search_input'] = 'true'

        for k in list(existence_dict.keys()):
            for fname in os.listdir(input_dir + '/' + kg_type):
                if k in fname:
                    if k == 'merged-kg_edges':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'merged-kg_nodes':
                        labels_file = input_dir + '/' + kg_type + '/' + fname
                    existence_dict[k] = 'true'

    #Check for existence of all necessary files, error if not

    #### Add exception
    for k in existence_dict:
        if existence_dict[k] == 'false':
            if input_type != 'file' and k == '_search_input':
                input_file = ''
                pass
            else:
                raise Exception('Missing file in input directory: ' + k)

    #Check for existence of output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return triples_list_file,labels_file,input_file
