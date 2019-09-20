#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:35:54 2019

@author: Wei Wei

This subroutine stores the milestone information.
It initializes the milestone list, also contains the function that provides initial and final milestone.

"""

import os, re, time
import pandas as pd
import numpy as np
from run import *
from colvar import *
from log import log
from parameters import *
from network_check import *

class milestones: 

    def __init__(self, parameter) -> None:
        self.parameter = parameter
        
    def __enter__(self):
        return self
               
    def __exit__(self, exc_type, exc_value, traceback):
        return 
            
    def __repr__(self) -> str:
        return ('miletstones details.'
                .format(self.anchor_orig, self.anchor_dest, self.lifetime))


    def __get_next_frame_num(self, struPath):
        next_frame = 1
        while True:
            pdbPath = struPath + '/' + str(next_frame) 
            if os.path.exists(pdbPath):
                next_frame += 1
            else:
                break
        return next_frame
    
    def __traj_from_anchors(self, anchor, initialNum):
        colvar(self.parameter, free='yes', initial='yes').generate()      
        run(self.parameter).submit(a1=anchor, a2=999, initial='yes', initialNum=initialNum)
        

    def initialize(self, status=0):
        from sampling import move_restart
        MS_list = set()
        if self.parameter.milestone_search == 0 and status == 0:
            for i in range(1, self.parameter.AnchorNum):
                name = 'MS' + str(i) + '_' + str(i + 1)
                MS_list.add(name)
            if self.parameter.pbc != []:
                name = 'MS' + str(self.parameter.pbc[0]) + '_' + str(self.parameter.pbc[1])
                MS_list.add(name)
            return MS_list
        elif status == 1:
            MS_list = self.__read_milestone_folder()
            self.parameter.finished_constain = MS_list.copy()
            move_restart(MS_list)
            return MS_list
        else:
            while True:    
            #    # free runs from each anchors, markdown once it reaches another cell (i.e. closer to another anchor ). 
                self.__seek_milestones()
                MS_list = self.__read_milestone_folder()
            #    # check if reactant and product are connected.
                if network_check(self.parameter, MS_list=MS_list) == True:
                    break
            # read folders to get the milestones list 
            MS_list = self.__read_milestone_folder()
            return MS_list
    

    def get_initial_ms(self, path):
        path_split = path.split("/")
#        if self.parameter.iteration == 1:
    #        print(path_split)
        initial_ms = list(map(int,(re.findall('\d+', path_split[-3]))))
    #        initial_ms = [int(path_split[-3].split("_")[0]), int(path_split[-3].split("_")[1])]
#        else:
#            path_split[-2] = str(int(path_split[-2]) - 1)
#            path_prev = "/" + os.path.join(*path_split)
#            ms = pd.read_csv(path_prev + '/end.txt',header=None,delimiter=r'\s+').values.tolist()
#            initial_ms = [ms[0][0], ms[0][1]]
        with open(path + '/start.txt', 'w+') as f1:
            print(initial_ms[0], initial_ms[1], file=f1)    
        return initial_ms
        
    
    def get_final_ms(self, path):
        state = path + "/stop.colvars.state"
        if not os.path.isfile(state):
            return -1, [0, 0]
        final_ms = [0, 0]
        # read state file generated at termination point 
        # smallest rmsd indicates new cell #
        RMSDs, lifetime = self.read_state(state)
        final_ms[0] = RMSDs.index(sorted(RMSDs)[0]) + 1
        
        if self.parameter.pbc != []:
            if final_ms[0] == self.parameter.AnchorNum or final_ms[0] == 1:
                # open traj file to read the very last output
                # smallest rmsd indicates previous cell #
                traj = path + "/" + self.parameter.outputname + ".colvars.traj"
                firstRMSD = self.parameter.colvarsNum + 1
                try:
                    RMSDs_prev = pd.read_fwf(traj, widths=self.parameter.trajWidths).values[-1,firstRMSD:].astype(np.float64).tolist()
                except:
                    print(traj)
                    return -1, [0, 0]
                final_ms[1] = RMSDs_prev.index(sorted(RMSDs_prev)[0]) + 1 
            else:
                final_ms[1] = RMSDs.index(sorted(RMSDs)[1]) + 1 
        else:
            # use the second min value for previous cell #
            final_ms[1] = RMSDs.index(sorted(RMSDs)[1]) + 1 
        
        if self.parameter.iteration >= 1:
            try:
                start_ms = pd.read_csv(path + '/start.txt', header=None, delimiter=r'\s+').values.tolist()[0]
            except:
                return -1, [0, 0]
            if start_ms[0] not in final_ms and start_ms[1] not in final_ms:
                return -1, [0, 0]
        final_ms.sort()
        final_info = path + '/end.txt'
        if not os.path.isfile(final_info):
            with open(final_info, 'w+') as f1:
                print(final_ms[0], final_ms[1], file=f1)    
        time_info = path + '/lifetime.txt'
        if not os.path.isfile(time_info):
            with open(time_info, 'w+') as f1:
                print(lifetime, file=f1)    
        return lifetime, final_ms
 
    
    def __seek_milestones(self):
        from shutil import copy
        milestones = set()
        filePath = os.path.dirname(os.path.abspath(__file__)) 
        seekdir = os.path.abspath(os.path.join(filePath, os.pardir)) + '/crd/seek'
        pardir = os.path.abspath(os.path.join(filePath, os.pardir)) 
        
        for an in range(1, self.parameter.AnchorNum+1):
            initialNum = self.__get_next_frame_num(seekdir + '/structure' + str(an))
            for i in range(self.parameter.initial_traj):
                if not os.path.exists(seekdir + '/structure' + str(an) + '/' + str(i + initialNum)):
                    os.makedirs(seekdir + '/structure' + str(an) + '/' + str(i + initialNum))
                self.__traj_from_anchors(an, i + initialNum)
                
        log("{} trajectories started from each anchor, run for {} ps.".format(self.parameter.initial_traj, self.parameter.initialTime))
        
        finished = []
        while True:
            for i in range(1, self.parameter.AnchorNum + 1):
                MSname = 'a' + str(i)
                if run(self.parameter).check(MSname=MSname) == False:
                    continue
                elif MSname in finished:
                    continue
                else:
                    finished.append(MSname)
            if (len(finished) == self.parameter.AnchorNum):
                break
            time.sleep(60)
        
        for i in range(1, self.parameter.AnchorNum + 1):
            curt_frame = self.__get_next_frame_num(seekdir + '/structure' + str(i))
            for traj in range(1, curt_frame):
                path = seekdir + '/structure' + str(i) + '/' + str(traj)
                if not os.path.exists(path):
                    continue
                if os.path.isfile(path + '/end.txt'):
                    continue
                timetmp, final_ms =  self.get_final_ms(path)
                if final_ms == [0, 0]:
                    continue
                name = 'MS' + str(final_ms[0]) + '_' + str(final_ms[1])
                if name in milestones:
                    continue
                ms_path = pardir + '/crd/' + str(final_ms[0]) + '_' + str(final_ms[1])
                if os.path.exists(ms_path):
                    continue          
                elif not os.path.isfile(path + '/' + self.parameter.outputname + '.restart.coor'):
                    continue
                else:
                    os.makedirs(ms_path)
                    copy(path + '/' + self.parameter.outputname + '.restart.coor', 
                         ms_path + '/seek.ms.pdb')
                    milestones.add(name)

        log("{} milestomes have been identified.".format(len(milestones)))  
        return milestones  
            

    def __read_milestone_folder(self):
        filePath = os.path.dirname(os.path.abspath(__file__)) 
        pardir = os.path.abspath(os.path.join(filePath, os.pardir)) + '/crd'
        MS_list = set()
        for i in range(1, self.parameter.AnchorNum):
            for j in range(i, self.parameter.AnchorNum + 1):
                name = str(i) + '_' + str(j)
                if os.path.exists(pardir + '/' + name):
                    MS_list.add('MS' + name)
        return MS_list

    def read_state(self, path):
        file = open(path, 'r').read()
        time = int(re.findall(r"[-+]?\d*\.\d+|\d+", file)[0])
#        print(time)
        numbers = re.findall(r"[-+]?\ *[0-9]+\.?[0-9]*(?:[eE]\ *[-+]?\ *[0-9]+)", file)
        numbers.pop(0)
#        print(numbers)
        numbers = numbers[self.parameter.colvarsNum:]
        rmsd = [abs(float(x)) for x in numbers]
#        print(rmsd)
        return rmsd, time
    
                
if __name__ == '__main__':
    from parameters import *
    new = parameters()
    milestones(new).get_final_ms('/home/weiw/examples/water3/3_4/1/950')
