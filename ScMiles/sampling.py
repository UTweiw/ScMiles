#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 15:06:01 2019

@author: Wei Wei

Running sampling.

"""

import time
import re
import os
from colvar import *
from parameters import *
from log import *
from network_check import *
from log import log
from run import *


class sampling:
    def __init__(self, parameter, jobs):
        self.parameter = parameter
        self.jobs = jobs
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return
    
    def __repr__(self) -> str:
        return ('Sampling on milestones.')    

    def constrain_to_ms(self):
        import os
        MS_list = self.parameter.MS_list.copy()
        finished = self.parameter.Finished.copy()
        # rootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in MS_list:
            if name in finished or name in self.parameter.finished_constain:
                continue
            if not self.jobs.check(MSname=name):
                continue
            lst = re.findall('\d+', name)
            anchor1 = int(lst[0])
            anchor2 = int(lst[1])
            restartsPath = self.parent_path + '/crd/' + str(anchor1) + '_' + str(anchor2) + '/restarts'
            if not os.path.exists(restartsPath):
                constrain = colvar(self.parameter, anchor1, anchor2)
                constrain.generate()
                self.jobs.submit(a1=anchor1, a2=anchor2)
                
        log("{} milestones identified.".format(str(len(MS_list))))             
        log("Sampling on each milestone...")   

    def check_sampling(self):
        import re
        from datetime import datetime
        finished = set()
        MS_list = self.parameter.MS_list.copy()
        while True:
            for name in self.parameter.MS_list:
                if not self.jobs.check(MSname=name):
                    continue
                elif name in self.parameter.finished_constain:
                    continue
                elif name in finished:
                    continue
                else:
                    [anchor1, anchor2] = list(map(int,(re.findall('\d+', name))))
                    finished.add(name)
                    if name not in self.parameter.finished_constain:
                        log("Finished sampling on milestone ({},{}).".format(anchor1, anchor2))  
                        self.parameter.finished_constain.add(name)
                            
            if finished | self.parameter.finished_constain == MS_list:
                self.parameter.Finished = finished.copy()
                log("Finished sampling on all milestones.")    
                log("Ready to launch free trajectories.") 
                self.move_restart(self.parameter.MS_list)
                return self.parameter.Finished
            print("Next check in 600 seconds. {}".format(str(datetime.now())))
            time.sleep(600)   # 600 seconds

    def move_restart(self, names):
        import os
        import glob
        from shutil import move
        # rootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in names:
            [anchor1, anchor2] = list(map(int,(re.findall('\d+', name))))
            ms = str(anchor1) + '_' + str(anchor2)
            filePath = self.parent_path + '/crd/' + ms
            restartFolder = filePath + '/restarts'
            if not os.path.exists(restartFolder):
                os.makedirs(restartFolder)
            for ext in ["coor", "vel", "xsc"]:
                for file in glob.glob(filePath + '/*.' + ext):
                    move(file, restartFolder)
                
            
if __name__ == '__main__':
    from parameters import *
    from run import *
    new = parameters()
    new.initialize()
    jobs = run(new, 1, 2)
    test = sampling(new, jobs)
#    print(new.anchors)
#    test.generate()