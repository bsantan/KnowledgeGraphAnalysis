# KnowledgeGraphAnalysis

This repository enables the generation of paths from a given knowledge graph, and visualization of those paths using upset plots. The scripts shown here are created for specific use cases of creating paths from MGMLink, KG-microbe-phenio, or uniprot-KG.

## Running the Script

1. First the paths can be created using the creating_subgraph_from_KG.py script using one path mode (microbe to disease, for example), two path mode (microbe - neurotransmitter - disease, for example), or a template based search.

```
python creating_subgraph_from_KG.py
python creating_subgraph_from_KG.py --input-dir INPUT-DIR  --output-dir OUTPUT-DIR --knowledge-graphs "['KG1','KG2']" --input-type INPUT-TYPE --experiment-type EXPERIMENT-TYPE
```

2. Next, all paths generated can be evaluated for common node patterns using the Find_Common_Paths_diffKGs.py script, which aggregates all paths in the input directory and identifies which ontology/resource the nodes in that path are from. Skim only lists each node type once, and full will list every occurance of the node type. The graph type specifies which format the node identifiers are in to align them to their correpsonding ontology or database.

```
python Find_Common_Paths_diffKGs.py --directory <Directory of paths> --graph-type <pkl or kg-covid19>
```
necessary outputs: Pattern_Counts_Skim.csv to the same directory as all paths

3. Create an upset plot of the paths found from step #2 for 2 different graphs using the upset_plot.py script. This script will take as an input the directory of the Pattern_Counts_Skim.csv file for each graph type, and will output an upset plot representing the number of path patterns for each graph. 

```
python upset_plot.py --pkl-directory <directory of patterns for pkl graph> --kg-directory <directory of patterns for kg-covid19 graph>
```
