import pandas as pd
import re
import os

# set column number and width to display all information
pd.set_option('display.max_rows', None)



# Read in the user example file and output as a pandas dataframe
def read_user_input(user_example_file):
	examples = pd.read_csv(user_example_file, sep= "|")
	return(examples)

# Get list of unique nodes
# Inputs:	examples		pandas dataframe of user input examples.
# Outputs:	nodes 			set of unique nodes
def unique_nodes(examples):
	# get unique node values
	nodes = list(set(pd.melt(examples)["value"].values))

	return(nodes)

# Search through labels to find nodes based on input feature
# Inputs: 	node 		string for user input example.
#			kg			knowledge graph of class Knowledge Graph
#			ontology	specific ontology to restrict search of nodes

def find_node(node, kg, ontology = ""):
	nodes = kg.labels_all

	results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)][["label", "entity_uri"]]

	return(results)
                

# Create a list of nodes for input

def search_nodes(nodes, kg, examples):
	print('searching nodes: ',nodes)
	examples["source_label"] = ""
	examples["target_label"] = ""
	for node in nodes:
		orig_node = node
		search_loop = True
		while(search_loop):
			print("User Search Node: ", node)
			found_nodes = find_node(node,kg)
			nrow = found_nodes.shape[0]
			if nrow == 0:
				print("No search terms returned")
				node = input("Please try another input term: ")
			else:
				search_loop = False	
		print("Found", nrow, "features in KG")
		user_input = ""
		bad_input = True
	
		if nrow < 20:
			while(bad_input):
				print(found_nodes.iloc[0:nrow,].to_string())
				user_input = input("Input node 'label': ")
				if node_in_search(found_nodes,user_input):
					#Manage if there are 2 duplicate label names
					if len(found_nodes[found_nodes['label'] == user_input][['label','entity_uri']]) > 1:
						user_input = input("Input node 'entity_uri': ")
						if node_id_in_search(found_nodes,user_input):
							node_label = kg.labels_all.loc[kg.labels_all['entity_uri'] == user_input,'label'].values[0]
							bad_input = False
					else:
						node_label= user_input
						bad_input = False
				elif node_in_labels(kg,user_input):
					node_label= user_input
					bad_input = False
				else:
					print("Input not in search results.... try again")
		else:	
			i = 0
			while(bad_input):
				high = min(nrow,(i+1)*20)
				print(found_nodes.iloc[i*20:high,].to_string())
				user_input = input("Input node 'label' or 'f' for the next 20 features or 'b' for the previous 20: ")
				if user_input == 'f':
					i+=1
				elif user_input == 'b':
					i-=1
				else:
					i+=1
					if node_in_search(found_nodes,user_input):
						node_label = user_input
						bad_input = False
					else:
						print("Input not in search results.... try again")
		'found good input'
		examples.loc[examples["source"] == orig_node,"source_label"] = node_label
		## Skip this line for comparing kg-covid19/monarch graph to pkl only
		examples.loc[examples["target"] == orig_node,"target_label"] = node_label
	examples.drop_duplicates(keep='first', inplace=True)
	print('examples complete: ',examples)
	return(examples)

#An automatic way of doing search_node without user input, if what is given in file is exact
def extract_label(nodes, kg, examples):
	examples["source_label"] = ""
	examples["target_label"] = ""
	for node in nodes:
		node_label = kg.labels_all.loc[kg.labels_all['entity_uri'] == node,'label'].values[0]
		examples.loc[examples["source"] == node,"source_label"] = node_label
		examples.loc[examples["target"] == node,"target_label"] = node_label

	return(examples)

# Check if search input is in the list of integer_ids
def node_in_search(found_nodes, user_input):
	if user_input in found_nodes[["label"]].values:
		return(True)
	else:
		return(False)

# Check if search input is in the list of integer_ids
def node_id_in_search(found_nodes, user_input):
	if user_input in found_nodes[["entity_uri"]].values:
		return(True)
	else:
		return(False)

# Check if search input is in the all nodes
def node_in_labels(kg, user_input):
	labels = kg.labels_all

	if user_input in labels[["label"]].values:
		return(True)
	else:
		return(False)

#subgraph_df is a dataframe with source,targe headers and | delimited
def create_input_file(examples,output_dir,kg_type,experiment_paths):
    input_file = output_dir+"/"+kg_type+'_'+experiment_paths+"_Input_Nodes_.csv"
    #examples = examples[["source_label","target_label"]]
    #examples.columns = ["source", "target"]
    examples.to_csv(input_file, sep = "|", index = False)



# Check if the input_nodes file already exists
def check_input_existence(output_dir,kg_type,experiment_paths):
	print('checking for: ',output_dir+'/'+kg_type+'_'+experiment_paths+"_Input_Nodes_")
	exists = 'false'
	mapped_file = ''
	for fname in os.listdir(output_dir):
		if bool(re.match(kg_type+'_'+experiment_paths+"_Input_Nodes_",fname)):
			print(fname)
			exists = 'true'
			mapped_file = fname
	return exists,mapped_file



# Wrapper function
def interactive_search_wrapper(g,user_input_file, output_dir,kg_type,experiment_paths,input_type,input_df):
	if input_type == 'file':
		exists = check_input_existence(output_dir,kg_type,experiment_paths)
		if(exists[0] == 'false'):
			print('Interactive Node Search')
			#Interactively assign node
			u = read_user_input(user_input_file)
			n = unique_nodes(u)
			s = search_nodes(n,g,u)
			create_input_file(s,output_dir,kg_type,experiment_paths)
		else:
			print('Node mapping file exists... moving to embedding creation')
			mapped_file = output_dir + '/'+ exists[1]
			s = pd.read_csv(mapped_file, sep = "|")
	else:
		n = unique_nodes(input_df)
		s = extract_label(n,g,input_df)
		#create_input_file(s,output_dir,kg_type,experiment_paths)
	
	return(s)

'''   
#To REMOVE                    
# Wrapper function without input file that is user defining the full mechanism
def interactive_search_wrapper_without_file(g,u, output_dir,kg_type,experiment_paths):

    exists = check_input_existence(output_dir,kg_type,experiment_paths)
    if(exists[0] == 'false'):
        print('Interactive Node Search')
        #Interactively assign node
        n = unique_nodes(u)
		#Added removing duplicates here
        s = search_nodes(n,g,u)
        create_input_file(s,output_dir,kg_type,experiment_paths)
    else:
        print('Node mapping file exists... moving to embedding creation')
        mapped_file = output_dir + '/'+ exists[1]
        s = pd.read_csv(mapped_file, sep = "|")
    return(s)
'''