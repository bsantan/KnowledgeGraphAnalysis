
from upsetplot import from_memberships, plot
from upsetplot import UpSet
from matplotlib import pyplot
import csv
import pandas as pd
import argparse
from itertools import chain
import numpy as np
from matplotlib import cm
from matplotlib import pyplot as plt
import seaborn as sns
from collections import defaultdict


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--pkl-directory",dest="PklDirectory",required=True,help="PklDirectory")
    parser.add_argument("--kg-directory",dest="KgDirectory",required=True,help="KgDirectory")

    return parser

def get_data(directory,kg_type):

    df = pd.read_csv(directory+'/Pattern_Counts_Skim.csv')

    print(directory)

    #Get all unique node types
    patterns = []
    counts = []
    patterns_orig = df.Pattern.unique()
    for i in patterns_orig:
        i_list = sorted(i.split(' --- '))
        if i_list not in patterns:
            #Patterns is now list of unique nodes
            patterns.append(i_list)
            counts.append(df.loc[df['Pattern'] == i,'Count'].values[0])
    unique_nodes = list(set([x for n in patterns for x in n]))

    cols = unique_nodes + ['kg_type']

    df = pd.DataFrame()

    for l in range(len(patterns)):
        #Keeps track of row # based on number of paths with this pattern
        counter = 0
        while counter < counts[l]:
            #a = np.zeros(shape=(1,len(unique_nodes)))
            a = np.full((1,len(cols)), 0, dtype=int)
            df2 = pd.DataFrame(a,columns = cols)
            df2['kg_type'] = kg_type
            #Keeps track of column name based on node type in pattern
            for i in patterns[l]:
                df2[i] = int(1)
            counter += 1
            df = pd.concat([df,df2],ignore_index=True)

    return df


def path_len_dist(directory,kg_type):

    df = pd.read_csv(directory+'/Pattern_Counts_Skim.csv')

    #path_lengths = defaultdict(list)
    path_length_df = pd.DataFrame()

    for i in range(len(df)):
        p_len = df.iloc[i].loc['Path_Length']
        #Create list of path lengths
        path_lengths = p_len.split(',')
        for j in path_lengths:
            #New df that will append a row for each path length for this pattern
            df2 = {} #columns = ['kg_type','Pattern','Path_Length']
            df2['kg_type'] = kg_type
            df2['Pattern'] = df.iloc[i].loc['Pattern']
            df2['Path_Length'] = int(j)
            df3 = pd.DataFrame.from_dict([df2])
            path_length_df = pd.concat([path_length_df,df3],ignore_index=True)

    ax = sns.boxplot(x="Pattern", y="Path_Length", hue="kg_type", data=path_length_df)    
    ax.set_xticklabels(ax.get_xticklabels(),rotation=30)
    plt.show()

def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()

    pkl_directory = args.PklDirectory
    kg_directory = args.KgDirectory
    
    
    pkl_df = get_data(pkl_directory,'pkl')
    kg_df = get_data(kg_directory,'kg')

    full_df = pd.merge(pkl_df,kg_df,how='outer')
    full_df = full_df.replace(np.nan, int(0))
    cols = list(full_df.columns)
    cols.remove('kg_type')
    for i in cols:
        if i != 'kg_type':
            full_df[i] = full_df[i].astype(int)
    full_df = full_df.set_index((full_df[cols[0]] == 1))
    for i in range(1,len(cols)):
        full_df = full_df.set_index((full_df[cols[i]] == 1),append=True)


    #Create upset plot
    upset = UpSet(full_df,intersection_plot_elements=0)  # disable the default bar chart
    upset.add_stacked_bars(by="kg_type", colors=cm.Dark2,
                        title="Path Count per KG", elements=20)
    
    upset.plot()
    plt.suptitle("Microbe-Neurotransmitter-Disease Path Patterns Found in Each KG") #Microbe-Neurotransmitter-Disease for two paths as input to command line, Microbe-Disease for one paths
    plt.legend(["MGMLink","kg-microbe-phenio"])
    save_dir = pkl_directory.split('pkl_shortest_path')[0]

    plt.show()

    #plt.savefig(save_dir+'/upset_plot.png')


if __name__ == '__main__':
    main()
