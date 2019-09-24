#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 11:23:40 2018

@author: 
"""

from milestone import milestone
from compute import *
import numpy as np
from log import log
from datetime import datetime
import os
from milestones import milestones

__all__ = ['milestoning']


def del_restarts(parameter, path, times, total_fs: int, freq: int) -> None:
    import os
    lst = []
    for time in times:
        lst.append(time // freq)
#        pardir = os.path.abspath(os.path.join(self.path, os.pardir))
#        print(lst)
    for i in range(1, total_fs // 100 + 1):
        if i not in lst:
            name = path + '/' + parameter.outputname +'.' + str(i * freq) + '.coor'
            if os.path.isfile(name):
                os.remove(name)
            name = path + '/' + parameter.outputname +'.' + str(i * freq) + '.vel'
            if os.path.isfile(name):
                os.remove(name)
            name = path + '/' + parameter.outputname +'.' + str(i * freq) + '.xsc'
            if os.path.isfile(name):
                os.remove(name)


def K_order(k, t, t_std, index):
    """
    argv:
          k: original K matrix, random order 
              
          t: original t array, same order as K
          
          t_std: standard deviation of t, same order as K
          
          index: milestones index for original K and t
   
    return:
          ordered K, t, t_std, and the new index for them
    """
#    index_new = dict(sorted(index.items(), key=lambda x:x[1]))
    index_new = {}
    for i, ms in enumerate(sorted(index.values(), key=lambda x:x[0])):
        index_new[i] = ms
    mapping = []
    for i, ms in enumerate(list(index_new.values())):
        mapping.append([k for k,v in index.items() if v == ms][0])
    dimension = len(k)
    k_new = np.zeros((dimension,dimension)).astype(int)
    t_new = np.zeros((dimension))
    t_std_new = np.zeros((dimension))
    for dimY in range(dimension):
        t_new[dimY] = t[mapping[dimY],[0]]
        t_std_new[dimY] = t_std[mapping[dimY],[0]]
        for dimX in range(dimension):
            k_new[dimX][dimY] = k[mapping[dimX]][mapping[dimY]]
#    print(index)
#    print(index_new)
    return k_new, t_new, t_std_new, index_new


def backup(parameter, files: list) -> None:
    from shutil import move, copy
    import os
    scriptPath = os.path.dirname(os.path.abspath(__file__)) 
    pardir = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_output/current'
    time = str(datetime.now()).split('.')[0]
    for file in files:
        if os.path.isfile(pardir + file): 
            if not os.path.exists(pardir + '/results'):
                os.makedirs(pardir + '/results')
            backup_Folder = pardir + '/results/' + str(parameter.iteration) + '_' + time
            if not os.path.exists(backup_Folder):
                os.makedirs(backup_Folder)
                
            if file == '/log':
                copy(pardir + file, backup_Folder + file)
            else:
                move(pardir + file, backup_Folder + file)
        

def milestoning(parameter):
    import multiprocessing as mp
    import pandas as pd
    ms = milestone()
    scriptPath = os.path.dirname(os.path.abspath(__file__)) 
    data_path = os.path.join(scriptPath, os.pardir) + '/crd'
    outputpath = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_output'
    outputpath = outputpath + '/current'
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    ms.read_anchors(parameter.AnchorPath)
    
    files = ['/k.txt', '/k_norm.txt', '/life_time.txt', '/info.txt', '/results.txt', '/list.txt', '/ms_index.npy', '/log', '/committor.txt', '/enhanced_count']
#    backup(files)
    
    path_list = []
    anchor_orig_list = []
    enhanced_count = {}
    for anchor1 in range(1, parameter.AnchorNum + 1):
        for anchor2 in range(anchor1 + 1, parameter.AnchorNum + 1):
            MSname = str(anchor1) + '_' + str(anchor2)
            MSpath = data_path + "/" + MSname
            if not os.path.exists(MSpath):
                continue

            for config in range(1, parameter.nframe):
                traj_filepath = data_path + "/" + MSname + '/' + str(parameter.iteration) + '/' + str(config) + \
                                "/" + parameter.outputname + ".colvars.traj"
                if not os.path.isfile(traj_filepath) or os.stat(traj_filepath).st_size == 0:
                    continue
                if os.path.isfile(data_path + '/' + MSname + '/' + str(parameter.iteration) + '/' + str(config) + '/enhanced'):
                    try:
                        enhanced_count[MSname] += 1
                    except:
                        enhanced_count[MSname] = 1
                path_list.append(traj_filepath)
#                anchor_orig_list.append([anchor1, anchor2])

    for path in path_list:
        
        start_info = os.path.dirname(os.path.abspath(path)) + '/start.txt'
        end_info = os.path.dirname(os.path.abspath(path)) + '/end.txt'
        time_info = os.path.dirname(os.path.abspath(path)) + '/lifetime.txt'
        
#        print(path)

        milestones(parameter).get_final_ms(os.path.dirname(os.path.abspath(path)))
        
        if not os.path.isfile(start_info) or os.stat(start_info).st_size == 0:
            continue
        if not os.path.isfile(end_info) or os.stat(end_info).st_size == 0:
            continue
        if not os.path.isfile(time_info) or os.stat(time_info).st_size == 0:
            continue
        
        start = pd.read_csv(start_info, header=None, delimiter=r'\s+').values.tolist()[0]
        end = pd.read_csv(end_info, header=None, delimiter=r'\s+').values.tolist()[0]
        time = pd.read_csv(time_info, header=None, delimiter=r'\s+').values.tolist()[0]
#        print(time)
        
        if start == end or end == [0,0]:
            continue
        
        if parameter.ignorNewMS and 'MS' + str(start[0]) + '_' + str(start[1]) not in parameter.MS_list:
            continue
        
        if str(start[0]) + '_' + str(start[1]) not in parameter.network.keys():
            parameter.network[str(start[0]) + '_' + str(start[1])] = set()
        parameter.network[str(start[0]) + '_' + str(start[1])].add(str(end[0]) + '_' + str(end[1]))
        
        anchor_orig = []
        anchor_dest = []
        lifetime = []
        
        anchor_orig.append([int(start[0]), int(start[1])])
        anchor_dest.append([int(end[0]), int(end[1])])
        lifetime.append(int(time[0]))
#        time.append(int(result[i, 5]))
         
#        del_restarts(parameter, os.path.dirname(os.path.abspath(path)), time, 100000, 100)
        
        if len(anchor_dest) == 0:
            continue
        
        name_dest = 'MS' + str(anchor_dest[0][0]) + '_' + str(anchor_dest[0][1])
        if parameter.ignorNewMS and name_dest not in parameter.MS_list:
            continue
        for i in range(len(anchor_orig)):    
            name_orig = str(anchor_orig[i][0]) + '_' + str(anchor_orig[i][1])
            name_dest = str(anchor_dest[i][0]) + '_' + str(anchor_dest[i][1])
            
            ms.add_ms(anchor_orig[i][0], anchor_orig[i][1], 'orig')
            ms.add_ms(anchor_dest[i][0], anchor_dest[i][1], 'dest')
            
            index1 = [k for k,v in ms.ms_index.items() if v == anchor_orig[i]]
            index2 = [k for k,v in ms.ms_index.items() if v == anchor_dest[i]]
            
            ms.k_count[index1, index2] += 1
            
            if ms.t_hash.get(name_orig):
                new_slice = str(ms.t_hash.get(name_orig)) + "," + str(lifetime[i])
            else:
                new_slice = str(lifetime[i])
            ms.t_hash[name_orig] = new_slice  
    

    
#    with open(outputpath + '/info.txt', 'w+') as f:
#        print(ms, file=f)
#        print(np.shape(ms.k_count), file=f)
#        print(ms.known, file=f)
#        print(ms.new, file=f)
#        print(ms.ms_index, file=f)
#        print("*****", file=f)
#        print(ms.t_hash, file=f)
    
    t = np.zeros((len(ms.ms_index), 1))
    t_std = np.zeros((len(ms.ms_index), 1))  
    for i in range(len(t)):
        name = str(ms.ms_index.get(i)[0]) + '_' + str(ms.ms_index.get(i)[1])
        if ms.t_hash.get(name):
            time_list = list(map(float, ms.t_hash.get(name).split(',')))
            t[i, 0] = np.mean(time_list)
            t_std[i, 0] = np.std(time_list, ddof=1) 
        
    k_ordered, t_ordered, t_std_ordered, index_ordered = K_order(ms.k_count, t, t_std, ms.ms_index)
    ms.k_count = k_ordered.copy()
    t = t_ordered.copy()
    t_std = t_std_ordered.copy()
    ms.ms_index = index_ordered.copy()    
    
    with open(outputpath + '/k.txt', 'w+') as fk:
        m = ['{}_{}'.format(item[0], item[1]) for item in list(ms.ms_index.values())]
        print(''.join(['{:>10}'.format(item) for item in m]),file=fk)
        print('',file=fk)
        print('\n'.join([''.join(['{:10d}'.format(item) for item in row])for row in ms.k_count]),file=fk)
        
    with open(outputpath + '/life_time.txt', 'w+') as f1:
        m = ['{}_{}'.format(item[0], item[1]) for item in list(ms.ms_index.values())]
        print(''.join(['{:>10}'.format(item) for item in m]),file=f1)
        print('',file=f1)
        print('\n'.join([''.join(['{:10.2f}'.format(item) for item in np.squeeze(t)])]),file=f1)
        print('\n'.join([''.join(['{:10.2f}'.format(item) for item in np.squeeze(t_std)])]),file=f1)
  
    k_ave = k_average(ms.k_count)    
    with open(outputpath + '/k_norm.txt', 'w+') as f1:
        f1.write('\n'.join([''.join(['{:10.5f}'.format(item) for item in row])for row in k_ave]))   
    np.save(outputpath + '/ms_index.npy', ms.ms_index)   
    
    parameter.kij = k_ave.copy()
    parameter.index = []
    for i in range(len(ms.ms_index)):
        parameter.index.append(ms.ms_index[i])
    
#    with open(outputpath + '/enhanced_count', 'w+') as f1:
#        for i in enhanced_count:
#            print(i, enhanced_count[i], file=f1)  
    
    compute(parameter)
    log("Computing finished. Mean first passage time: {:20.7f} fs".format(parameter.MFPT))  
    backup(parameter, files)
    return ms, ms.new, ms.known

if __name__ == '__main__':
    from parameters import *
    new = parameters()
    new.initialize()
#    new.nframe = 1000
    new.MS_list = ['MS1_2','MS2_3','MS3_4','MS4_5','MS5_6','MS6_7','MS7_8','MS8_9','MS9_10','MS10_11','MS11_12',#[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],\
               'MS1_12']#[3,8],[4,8],[5,7],[5,8],[7,9],[8,10],[8,11]]
    new.iteration = 1
    milestoning(new)
#print(ms)
#print(np.shape(ms.k_count))
#print(ms.t_hash)
#print(ms.known)
#print(ms.new)
#print(ms.ms_index)
