#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 10:06:33 2019

@author: jonyoung
"""

# method from 'Optimal Matching for Observational Studies' by Rosenbaum
# https://www.jstor.org/stable/pdf/2290079.pdf

# import what we need
import pandas as pd
import numpy as np
import networkx as nwx
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt

def pairwise_matching(group_1, group_2, distance_metric, distance_matrix=None) :
    
    # discover which group is smaller
    if len(group_1) < len(group_2) :
        
        group_small = group_1
        group_large = group_2
        
    else :
        
        group_small = group_2
        group_large = group_1
        
        # flip distance matrix if there is one
        if distance_metric == 'precomputed' :
            
            distance_matrix = np.tranpose(distance_matrix)
        
    n_small = len(group_small)
    n_large = len(group_large)
    
    # get names of subjects in each group
    group_small_names = group_small['ID'].tolist()
    group_large_names = group_large['ID'].tolist()
        
    # create digraph
    G = nwx.DiGraph()

    # add nodes
    # source and sink
    G.add_node('source', demand=-n_small)
    G.add_node('sink', demand=n_small)
    
    # nodes for smaller group
    for subject_name in group_small_names :
    
        G.add_node(subject_name) 
    
    # and for larger group
    for subject_name in group_large_names :
    
        G.add_node(subject_name) 

    # add edges from source to all subject in small group
    # with capacity =1, cost (weight)=0
    for subject_name in group_small_names :
        
        G.add_edge('source', subject_name, weight = 0, capacity = 1)

    # add edges fron all controls to sink
    # with capacity =1, cost (weight)=0
    for subject_name in group_large_names :
        
        G.add_edge(subject_name, 'sink',  weight = 0, capacity = 1)    
    
    # if distance metric is not precomputed, compute one according to the supplied metric
    if distance_metric != 'precomputed' :
        
        # pull matching data out of groups - all cols except 'ID'
        # and convert to numpy matrix
        group_small_data = group_small.iloc[:, group_small.columns != 'ID'].as_matrix()
        group_large_data = group_large.iloc[:, group_large.columns != 'ID'].as_matrix()
        
        # calculate the distance matrix
        distance_matrix = cdist(group_small_data, group_large_data, metric=distance_metric).astype(int)
        
    # add edges from each small group subject to each large group subject
    # with capacity = 1 and cost(weight) from the distance matrix
    for i, subject_name_1 in enumerate(group_small_names) :
            
        for j, subject_name_2 in enumerate(group_large_names) :
                
            distance = distance_matrix[i, j]
            G.add_edge(subject_name_1, subject_name_2, weight = distance, capacity = 1)   
            
    # find the matching by running a min cost flow on G
    flowDict = nwx.min_cost_flow(G)
    
    # output the matching
    matching = []
    for subject_1 in group_small_names :
        
        # get edges for subject
        subject_1_edges = flowDict[subject_1]
        
        for subject_2 in group_large_names :
            
            edge = subject_1_edges[subject_2]
            if edge == 1 :
                
                break
            
        # group 1 first in output tuples to match inpit    
        if len(group_1) < len(group_2) :
        
            matching.append((subject_1, subject_2))
        
        else :
        
            matching.append((subject_2, subject_1))
            
    return matching
                

        
        
        
        
        

    
    
