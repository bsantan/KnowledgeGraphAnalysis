from graph import KnowledgeGraph
import pandas as pd
import csv
import json
from igraph import * 


###Read in all files, outputs triples and labels as a df
def process_pkl_files(triples_file,labels_file):
    #Edgelist uses IDs
    triples_df = pd.read_csv(triples_file,sep = '\t')
    triples_df.columns = triples_df.columns.str.strip().str.lower()
    triples_df = triples_df[['subject', 'predicate', 'object']]
    #triples_df.columns.str.lower()

    #labels = pd.read_csv(labels_file, sep = '\t', usecols = ['id','category','name','description'])  #,'iri','synonym'])
    labels = pd.read_csv(labels_file, sep = '\t', low_memory=False)
    labels.columns = labels.columns.str.strip().str.lower()
    labels = labels.rename(columns={'identifier':'entity_uri'})
    '''
    if 'id' in labels.columns:
        labels = labels[['id','name']] 
        labels.columns = ['id','label'] #,'entity_uri','synonym']
    elif 'identifier' in labels.columns:
        labels.columns = ['id','label']
    '''
    #Handle nodes with no label
    labels.loc[pd.isna(labels["label"]),'label'] = labels.loc[pd.isna(labels["label"]),'entity_uri']
    
    return triples_df,labels

#Creates igraph object and a list of nodes
def create_igraph_graph(edgelist_df,labels):

    edgelist_df = edgelist_df[['subject', 'object', 'predicate']]

    g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

    g_nodes = g.vs()['name']

    return g,g_nodes

# Wrapper function
# Includes a "kg_type" parameter for graph type. Options include 'pkl' for PheKnowLator and 'kg-covid19' for KG-Covid19
def create_graph(triples_file,labels_file, kg_type):
    if kg_type == "pkl":
        triples_df,labels = process_pkl_files(triples_file,labels_file)
    elif kg_type != "pkl":
        triples_df,labels = process_kg_covid19_files(triples_file,labels_file)
    else:
        raise Exception('Invalid graph type! Please set kg_type to "pkl" or "kg-covid19"')

    g_igraph,g_nodes_igraph = create_igraph_graph(triples_df,labels)
    # Created a PKL class instance
    pkl_graph = KnowledgeGraph(triples_df,labels,g_igraph,g_nodes_igraph)

    return pkl_graph





###Read in all kg_covid19 files, outputs triples and labels as a df
def process_kg_covid19_files(triples_file,labels_file):
    triples_df = pd.read_csv(triples_file,sep = '\t', usecols = ['subject', 'object', 'predicate'])
    triples_df.columns.str.lower()

    triples_df=triples_df.astype(str)

    labels = pd.read_csv(labels_file, sep = '\t', usecols = ['entity_uri','label'])    

    '''
    labels = pd.read_csv(labels_file, sep = '\t', usecols = ['id','name','description','xrefs','synonym'])
    labels.columns = ['id','label', 'description/definition','synonym','entity_uri']
    labels.loc[pd.isna(labels["label"]),'label'] = labels.loc[pd.isna(labels["label"]),'id']
    labels.loc[pd.isna(labels["entity_uri"]),'entity_uri'] = labels.loc[pd.isna(labels["entity_uri"]),'id']
    '''
    
    return triples_df,labels
