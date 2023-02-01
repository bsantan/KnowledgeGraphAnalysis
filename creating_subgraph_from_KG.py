from inputs import *
from create_graph import create_graph
from assign_nodes import interactive_search_wrapper_without_file
from create_subgraph import user_defined_edge_exclusion
from visualize_subgraph import output_visualization
from evaluation import *
from graph_experiments import *
from find_path import template_based_search

def main():

    microbe_phenio_triples_file = '/Users/brooksantangelo/Documents/HunterLab/Exploration/kg_microbe_phenio/output_data/merged-kg/kgx_merged-kg_edges.tsv'
    microbe_phenio_labels_file = '/Users/brooksantangelo/Documents/HunterLab/Exploration/kg_microbe_phenio/output_data/merged-kg/kgx_merged-kg_nodes.tsv'

    mgmlink_triples_file = '/Users/brooksantangelo/Documents/HunterLab/MGMLink/git/MGMLink/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'
    mgmlink_labels_file = '/Users/brooksantangelo/Documents/HunterLab/MGMLink/git/MGMLink/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels_NewEntities.txt'

    mikg4md_relations_file = '/Users/brooksantangelo/Documents/HunterLab/ISMB2023/Mikg4md_experiment/Microbe_Neurotransmitter_MentalDisorder_EvidenceAB.csv'

    graphs = [[microbe_phenio_triples_file,microbe_phenio_labels_file],[mgmlink_triples_file,mgmlink_labels_file]]
    kg_types = ['kg-covid19','pkl']

    #graphs = [[mgmlink_triples_file,mgmlink_labels_file]]
    #kg_types = ['pkl']

    #Work looking at only depressive disorder only went to Experiment2 folder, added /all_mechs_onePath or _twoPaths folder for all diseases
    output_dir = '/Users/brooksantangelo/Documents/HunterLab/ISMB2023/Experiment2'

    
    embedding_dimensions = 128
    weights = True
    search_type = 'all'
    pdp_weight = 0.4
    '''
    ## Source and target nodes of interest
    #microbe = 'Bifidobacterium dentium'
    #neurotransmitter = 'gamma-aminobutyric acid'
    #mental_disorder = 'depressive disorder' #MONDO:0002050

    #Get source and target nodes from MiKG4MD findings
    #Get all bacteria related to depression, and and neurotransmitters between that
    mikg4md_relations = pd.read_csv(mikg4md_relations_file)
    
    depression_relations = mikg4md_relations
    '''
    '''
    #To evaluate only 1 disease
    depression_relations = mikg4md_relations[mikg4md_relations['mental_disorder'] == 'Depressive disorder']
    #For testing
    depression_relations = depression_relations[depression_relations['microbe'] == 'Lactobacillus plantarum']
    depression_relations = depression_relations[depression_relations['neurotransmitter'] == 'Serotonin']
    '''

    print("Creating knowledge graph object from inputs.....")

    for i in range(len(graphs)):
        if kg_types[i] == 'kg-covid19':
            continue
        path_nums_dict = {}
        print('Graph: ',kg_types[i])
        g = create_graph(graphs[i][0],graphs[i][1])

        #Want to exclude the biolink:category, biolink:in_taxon, MAYBE biolink:related_to, biolink:part_of
        #Want to exclude the <http://purl.obolibrary.org/obo/RO_0002160> - only in taxon, <http://purl.obolibrary.org/obo/BFO_0000050> - part of
        #Want to exclude type edge for mikg4md

        
        if weights == True:
            g = user_defined_edge_exclusion(g,kg_types[i])
            #g = user_defined_node_exclusion(g,kg_types[i])
        
        #print('microbe to disease')
        #input_df = pd.DataFrame.from_dict({'source':depression_relations['microbe'],'target':depression_relations['mental_disorder']})
    
        #Remove nodes that take too many resources in path search
        '''
        s = s[s.source != 'Burkholderia oklahomensis']
        s = s[s.source != 'Acinetobacter baumannii']
        s = s[s.source != 'Erysipelatoclostridium ramosum DSM 1402']
        s = s[s.source != 'Bacteroides uniformis']
        s = s[s.source != 'Clostridium']
        s = s[s.source != 'Fusobacterium varium ATCC 27725']
        s = s[s.source != 'Bacillus cereus group']
        depression_relations = depression_relations[depression_relations.microbe != 'Burkholderia oklahomensis']
        depression_relations = depression_relations[depression_relations.microbe != 'Acinetobacter baumannii']
        depression_relations = depression_relations[depression_relations.microbe != 'Clostridium ramosum']
        depression_relations = depression_relations[depression_relations.microbe != 'Bacteroides uniformis']
        depression_relations = depression_relations[depression_relations.microbe != 'Clostridium']
        depression_relations = depression_relations[depression_relations.microbe != 'Fusobacterium varium']
        depression_relations = depression_relations[depression_relations.microbe != 'Bacillus cereus']
        '''

        
        #microbe to disease
        '''
        #s will only include 1 source/target
        
        ###########
        s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'onePath')
        onePath_tracker = []
        for j in range(len(depression_relations)):
            microbe = depression_relations.iloc[j].loc['microbe']
            mental_disorder = depression_relations.iloc[j].loc['mental_disorder']
            
            #if microbe == 'Lactobacillus plantarum' and mental_disorder == 'Sex behavior disorder':
            #    continue
            #if microbe == 'Coprococcus':
            #    continue
            #if microbe == 'Fusobacterium ulcerans' and mental_disorder == 'Sleep disorders':
            #    continue
            #if microbe == 'Fusobacterium ulcerans' and mental_disorder == 'Eating disorders':
            #    continue
            
            print(microbe,mental_disorder)
            l = [microbe,mental_disorder]
            #s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'onePath')
            if l not in onePath_tracker:
                nodes_input_df = pd.DataFrame([{'source':microbe,'target':mental_disorder}])
                one_path_search(nodes_input_df,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,graphs[i][0],output_dir,embedding_dimensions,kg_types[i],pdp_weight)
            onePath_tracker.append(l)
        '''
        #############
        '''
        print('microbe to neurotransmitter to disease')
        input_df = pd.DataFrame.from_dict({'source':[depression_relations['microbe'],depression_relations['neurotransmitter']],'target':[depression_relations['neurotransmitter'],depression_relations['mental_disorder']]})
        l1 = list(depression_relations['microbe']) + list(depression_relations['neurotransmitter'])
        l2 = list(depression_relations['neurotransmitter']) + list(depression_relations['mental_disorder'])
        input_df = pd.DataFrame.from_dict({'source':l1,'target':l2})  
        #s will only include 1 source/target
        s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'twoPaths')

        twoPath_tracker = []

        for j in range(len(depression_relations)):
            microbe = depression_relations.iloc[j].loc['microbe']
            neurotransmitter = depression_relations.iloc[j].loc['neurotransmitter']
            mental_disorder = depression_relations.iloc[j].loc['mental_disorder']
            l = [microbe,neurotransmitter,mental_disorder]
            #s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'onePath')
            if l not in twoPath_tracker:
                nodes_input_df = pd.DataFrame.from_dict({'source':[microbe,neurotransmitter],'target':[neurotransmitter,mental_disorder]})
                #s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'twoPaths')
                two_path_search(nodes_input_df,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,graphs[i][0],output_dir,embedding_dimensions,kg_types[i],pdp_weight)
                twoPath_tracker.append(l)
        '''
        #############
        #For specifically serotonin search
        '''
        #Search intermediate nodes between microbe and NT/Disease
        i_node = 'serotonin(1+)'
        i_node_l = [i_node for i in range(len(depression_relations['neurotransmitter']))]
        '''
        #############
        '''
        #Have specific edges to exclude for these pairs: biolink:capable_of, biolink:has_attribute
        if weights == True:
            g = user_defined_edge_exclusion(g,kg_types[i])

        print('microbe to intermediate')
        #Comment out if doing serotonin specifically
        input_df = pd.DataFrame.from_dict({'source':[i_node_l,depression_relations['neurotransmitter']],'target':[depression_relations['neurotransmitter'],depression_relations['mental_disorder']]})
        l1 = i_node_l + list(depression_relations['neurotransmitter'])
        l2 = list(depression_relations['neurotransmitter']) + list(depression_relations['mental_disorder'])
        input_df = pd.DataFrame.from_dict({'source':l1,'target':l2})  
        print(input_df)
        #s will only include 1 source/target
        s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'intermPath')   

        intermPath_tracker = []

        for j in range(len(depression_relations)):
            neurotransmitter = depression_relations.iloc[j].loc['neurotransmitter']
            interm = i_node_l[0]
            mental_disorder = depression_relations.iloc[j].loc['mental_disorder']
            l = [interm,neurotransmitter,mental_disorder]
            #s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'onePath')
            if l not in intermPath_tracker:
                #nodes_input_df = pd.DataFrame.from_dict({'source':[interm,neurotransmitter],'target':[neurotransmitter,mental_disorder]})
                nodes_input_df = pd.DataFrame.from_dict({'source':[neurotransmitter,interm],'target':[interm,mental_disorder]})
                #s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'twoPaths')
                two_path_search(nodes_input_df,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,graphs[i][0],output_dir,embedding_dimensions,kg_types[i],pdp_weight)
                intermPath_tracker.append(l)
        '''

        #############
        '''
        print('random search')
        input_df = pd.DataFrame.from_dict([{'source':'regulation of synaptic plasticity','target':'depressive disorder'}])
        s = interactive_search_wrapper_without_file(g, input_df, output_dir,kg_types[i],'randPath') 
        #Issue in get_nodes_from_input since adding duplicate source/target_label columns - it works if you try again once the pkl_randPath_Input_Nodes_.csv file is created
        one_path_search(input_df,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,graphs[i][0],output_dir,embedding_dimensions,kg_types[i],pdp_weight)c
        '''

        
        #Template based search
        if kg_types[i] == 'pkl':
            template = ['X','metabolite','disease']# #  #['microbe','metabolite','gene','protein','process','metabolite','disease'] #['process','metabolite']  #['microbe','metabolite','gene','protein','process','metabolite','disease'] #['process','metabolite'] #['microbe','metabolite','gene','protein','process','metabolite','disease'] #['microbe','metabolite','gene','protein','process','disease'] #'microbe','metabolite', ,'protein','process','disease']#['microbe','gene','protein','process','neurotransmitter','disease']
        elif kg_types[i] == 'kg-covid19':
            template =  ['microbe','process','metabolite','process','disease']
        template_based_paths_df = template_based_search(template,kg_types[i],g,search_type)

        name = '_'.join(template)


        template_noa_df = output_visualization(name,'',template_based_paths_df,output_dir+'/' + kg_types[i]+'_'+search_type+'_template_based')
        

if __name__ == '__main__':
    main()