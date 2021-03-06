#NAME OF THE FILE: EasyNGS_with_UI_v3.py
#BY: Kiranmayee Dhavala, Alok Subbarao, Renu Jayakrishnan, Harjot Hans
#DATE SUBMITTED: 12/17/2014
#Python Version(s): 2.7.4





import EasyNGS_output_module_v2_3 as ngs
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

"""
Modification history:
    Author: Alok Subbarao
Date: 12/13/14, 12/17/14
Added the graph seen at the bottom, updated variables to pull from classes

"""



mapped_reads = []
mapkeys = ngs.design.ID
mapvals = ngs.design.refseq

temp_dictionary=dict(zip(mapkeys,mapvals)) #create a dictionary of 
                                           #barcode as keys, sequences as values

design_dictionary = dict(zip(temp_dictionary.values(), temp_dictionary.keys()))#new dictionary which swaps the keys and the values


##mapreads editted by jeff, 12/14 5pm##

def mapreads(x):
    """Description: given sequences in a list x, each sequence is looked up in design_dictionary
    If the sequence(s) in x match to something in design_dictionary, it is appended to the mapped_reads list
    Postconditions: This function works in conjunction with the get_sam_match function; it clears mapped reads
    in order to work with chunking of large files
    Side effects: None
    Returns: mapped_reads, but mapped_reads becomes an empty set once the function runs
    """
    mapped_reads = []
    for sequence in x:
        if sequence in design_dictionary:
            match = design_dictionary.get(sequence), sequence
            mapped_reads.append(match)
    return mapped_reads
    



##chunking (get_sam_match) rebuilt by jeff, 12/14 5pm##
"""Author: Jeff Byrnes; this comment written by Alok - Jeff has created the chunking function which will scale
    to any size file"""
def get_sam_match(fname):
    """
    
    Description: This file reads through the Sam file in 25000 line chunks and maps all reads
    using the design_dictionary. 
    Postconditions: Must be called in order for the mapped reads to occur 
    Side effects: May not work properly on machines with low memory 
    Return: this function returns sam_match which is a list of all the reads and the corresponding ID in the design file
    """
    sam_match = []
    raw = pd.read_csv(fname, chunksize = 25000, low_memory=False, sep = ",")
    #wholefile= pd.concat((raw),ignore_index=True)
    for chunk in raw:
        currentreads = chunk.ix[:,9]
        
        sam_match.append(mapreads(currentreads))

    return sam_match


mapped_read_data = get_sam_match('EasyNGS_Sam.csv')
#this provides the ID and sequence of all reads in the Sam file that map to the design file
#this includes repeats, i.e. the same sequence is present multiple times in SAM file


mapIDs = [ID for ID, seq in set(mapped_read_data[0])]
mapSeqs = [seq for ID, seq in set(mapped_read_data[0])]
#taking the set removes repeats so each ID, sequence only appears once




##Depth_count & Plot deisgned by jeff: 12/14 7pm##
"""
Modification History
Author: Alok Subbarao on 12/16/14
Used the chunking method created by Jeff, remade depth count/plot
introduced a collections.defaultdictionary to be able to easily
calculate depth and frequency for histogram purposes
"""
    

bins = defaultdict(int)
#create a default dictionary with integer keys which is currently empty
    
listofdepth = []
def get_depth_count_sam(fname):
    """Description: this function provides a count of each depth for histogram purposes
    Postconditions: This is a void function; it simply reads the SAM file and calculates data for histogram
    Returns: nothing, void function"""
    raw = pd.read_csv(fname, chunksize = 2500, low_memory = False, sep = ",")
    for chunk in raw:
        depth = list(chunk.ix[:,3])
        vals = set(depth)
        listofdepth.append(depth) 
        for i in depth:
            bins[i] += 1
  
    return None

depthlist=[]


get_depth_count_sam('EasyNGS_Mpileup.csv') 
#run the function above so that the bins dictionary is populated

#mygraph = plt.bar(bins.keys(),bins.values())
thisgraph, ax = plt.subplots(1)
def GraphDepth():
    """Description: Graphs the depth and calculates the mean, median, and standard deviation
    Postconditions: None
    Returns: A histogram"""
    for i in listofdepth:
        for j in i:
            j = int(j)
            depthlist.append(j)
    
    mu = np.mean(depthlist)
    median = np.median(depthlist)
    sigma = np.std(depthlist)  
    """This function takes no arguments, it simply graphs depth vs. frequency"""
    thisgraph = plt.bar(bins.keys(),bins.values())
    
    plt.xlabel("Depth")
    plt.ylabel("Frequency of Depth")
    plt.title("Histogram of Depth")
    textstr = '$\mu=%.2f$\n$\mathrm{median}=%.2f$\n$\sigma=%.2f$'%(mu, median, sigma)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(.75, .75, textstr, transform = ax.transAxes, fontsize = 14, bbox = props)
    
    plt.show()

GraphDepth()

    
 

