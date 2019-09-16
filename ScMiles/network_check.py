#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 16:23:54 2018

@author: Wei Wei

Apply Breadth First Seach to check if the reactant and product are connected.
Return True if connected; return False if not.

"""


__all__ = ['network_check', 'pathway']


##### initial connection check ###########
def listToGraph(MS_list, graph):
    import re
    for name in MS_list:
        [anchor1, anchor2] = list(map(int,(re.findall('\d+', name))))
        if str(anchor1) not in graph:
            graph[str(anchor1)] = set()
        graph[str(anchor1)].add(str(anchor2))
        if str(anchor2) not in graph:
            graph[str(anchor2)] = set()
        graph[str(anchor2)].add(str(anchor1))
      
    
def network_check(parameter, MS_list):
    from log import log
    if len(parameter.reactant) == 2:
        reactant = 'MS' + str(parameter.reactant[0]) + '_' + str(parameter.reactant[1])
        if reactant not in MS_list:
            log("Reactant and product are NOT connected yet.")  
            return False
        
    if len(parameter.product) == 2:    
        product = 'MS' + str(parameter.product[0]) + '_' + str(parameter.product[1])
        if product not in MS_list:
            log("Reactant and product are NOT connected yet.")  
            return False
  
    first = str(parameter.reactant[0])
    last = str(parameter.product[0])
    graph = {}
    listToGraph(MS_list, graph)
    
    visited, queue = set(), [first]
    while queue:
        anchor = queue.pop(0)
        if anchor not in visited:
            visited.add(anchor)
            if anchor in graph:
                queue.extend(graph[anchor] - visited)
    
#    print(visited)
    if last in visited:
        log("Reactant and product are connected.")  
        return True
    else:
        log("Reactant and product are NOT connected yet.")  
        return False
###################################
        

def pathway(parameter, k, MS_list):
    graph = {}
    for i in range(len(k)):
        for j in range(len(k[i])):
            if k[i][j] != 0:
                if str(i) not in graph:
                    graph[str(i)] = set(str(j))
                else:
                    graph[str(i)].add(str(j))
                    
    start = str(0)
    goal = str(44)
    
#    print(start)
#    print(goal)
#    return(list(bfs(graph, start, goal)))
    try:
        return next(bfs(graph, start, goal))
    except StopIteration:
        return None
    
    
def bfs(graph, start, goal):    
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in graph[vertex] - set(path):
           if next == goal:
               yield path + [next]
           else:
               queue.append((next, path + [next]))


# connection of free traj 
def listToGraph2(network, graph):
    for name in network.keys():
        if name not in graph:
            graph[name] = set()
        for value in network[name]:
            graph[name].add(value)
#    print(graph)       
    

def network_ms_check(parameter):
    network = parameter.network.copy()
    from log import log
    if len(parameter.reactant) == 2:
        reactant = str(parameter.reactant[0]) + '_' + str(parameter.reactant[1])
        if reactant not in network.keys():
            log("Reactant and product are NOT connected yet.")  
            return False
        
    if len(parameter.product) == 2:    
        product = str(parameter.product[0]) + '_' + str(parameter.product[1])
        if product not in [item for sublist in network.values() for item in sublist]:
            log("Reactant and product are NOT connected yet.")  
            return False
    
    graph = {}
    listToGraph2(network, graph)
    
    if len(parameter.reactant) == 2 and len(parameter.product) == 2:
        first = str(parameter.reactant[0]) + '_' + str(parameter.reactant[1]) 
        last = str(parameter.product[0]) + '_' + str(parameter.product[1]) 
        visited, queue = set(), [first]
        while queue:
            anchor = queue.pop(0)
            if anchor not in visited:
                visited.add(anchor)
                if anchor in graph:
                    queue.extend(graph[anchor] - visited)
        if last in visited:
            print(first,last, visited)
            log("Reactant and product are connected.")  
            return True
    #    print(visited)
        log("Reactant and product are NOT connected yet.")  
        return False    
    
    for i in range(parameter.AnchorNum):
        lst = [parameter.reactant[0], i + 1]
        lst.sort()
        first = str(lst[0]) + '_' + str(lst[1]) 
        if first not in network.keys():
            continue
        for j in range(parameter.AnchorNum):
            lst = [parameter.product[0], j + 1]
            lst.sort()
            last = str(lst[0]) + '_' + str(lst[1]) 
            if last not in [item for sublist in network.values() for item in sublist]:
                continue
            visited, queue = set(), [first]
            while queue:
                anchor = queue.pop(0)
                if anchor not in visited:
                    visited.add(anchor)
                    if anchor in graph:
                        queue.extend(graph[anchor] - visited)
            if last in visited:
                print(first,last, visited)
                log("Reactant and product are connected.")  
                return True
#    print(visited)
    log("Reactant and product are NOT connected yet.")  
    return False


    
if __name__ == '__main__':
    from parameters import *
    from call import *
    new = parameters()
    ms = read_milestone_folder(new)
#    print(ms)
#    ms = ['MS10_14','MS1_11','MS11_12','MS11_14','MS1_2','MS13_14','MS1_5','MS1_6','MS2_3',
#          'MS3_10','MS3_14','MS4_5','MS4_7','MS5_6','MS5_7','MS7_12','MS7_8','MS9_10','MS9_13','MS9_14']
#    ms = ['MS8_11', 'MS23_26', 'MS19_22', 'MS26_29', 'MS24_27', 'MS10_11', 'MS22_25', 'MS13_14', 
#          'MS25_26', 'MS31_34', 'MS7_10', 'MS23_24', 'MS12_15', 'MS34_35', 'MS11_14', 'MS2_3', 
#          'MS5_8', 'MS10_13', 'MS31_32', 'MS25_28', 'MS2_5', 'MS6_9', 'MS18_21', 'MS13_16', 
#          'MS4_7', 'MS21_24', 'MS11_12', 'MS17_20', 'MS28_31', 'MS19_20', 'MS20_23', 'MS27_30', 
#          'MS9_12', 'MS16_19', 'MS14_17', 'MS33_36', 'MS1_4', 'MS4_5', 'MS1_2', 'MS35_36', 
#          'MS15_18', 'MS5_6', 'MS29_32', 'MS30_33', 'MS3_6']
#    ms = ['MS12_15','MS15_18','MS18_21','MS21_25']
    print(network_check(new, ms))
    