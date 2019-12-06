#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 15:21:21 2018

@author: Wei Wei

A class that stores all of the information from input 
"""


class parameters:
    def __init__(self, MS_list=None, Finished=None, MS_new=None, 
                 ignorNewMS=None, coor=None, NVT=None
                 nodes=None, timeFactor=None, current_iteration_time=None,
                 sampling_interval=None,
                 maxIteration=None, network=None,
                 boundary=None, iteration=None, method=None, pbs=None,
                 reactant_milestone=None, product_milestone=None,
                 reactant=None,product=None,
                 bincoordinates=None, binvelocities=None, extendedSystem=None,
                 customColvars=None,
                 colvarsTrajFrequency=None, colvarsRestartFrequency=None, colvarsNum=None,
                 forceConst=None,
                 trajWidths=None, username=None, tolerance=None, err_sampling=None,
                 initial_traj=None, initialTime=None,
                 startTraj=None, trajPerLaunch=None, interval=None, freeTraj_walltime=None,
                 nframe=None, structure=None, coordinates=None, finished_constain=None,
                 outputname=None,
                 namd_conf=None,
                 AnchorPath=None, AnchorNum=None,  
                 new_anchor=None, anchor_dist=None,
                 jobsubmit=None, jobcheck=None,anchors=None,
                 atomNumbers=None, error=None, MFPT=None, kij=None, index=None,
                 flux=None,
                 sing=None) -> None:

        self.iteration = 0    # current iteration number
        
        self.method = 0       # 0 for classic milestoning; 1 for exact milestoning: iteration
        
        self.maxIteration = 100    # max iteration
        
        self.network = {}  # network for free trajectories
        
        self.milestone_search = 0   # 0 for traverse; 1 for seek
        
        self.pbc = []       # periodic boundary for 1D at the moment
        
        self.current_iteration_time = {}   # current iteration time
        
        self.timeFactor = 1    # fs per step

        self.sampling_interval = 1000   # output restarts every *** timesteps
        
        self.jobsubmit = jobsubmit    # command for job submission
        
        self.jobcheck = jobcheck    # command for job check 
        
        self.nodes = []  # available node list
        
        self.initial_traj = initial_traj    # number of trajs start from each anchor
        
        self.initialTime = initialTime     # time step in ps for initial trajs
        
        self.MS_list = set()    # milestone list
        
        self.ignorNewMS = False    # ignore new milestones found by free traj

        self.Finished = set()   # milestones that finished free trajs
        
        self.finished_constain = set()  # milestones that finished sampling
        
        self.MS_new = set()    # new milestone reached
        
        self.error = error     #

        self.NVT = False            # NVT for free trajectories
        
        self.boundary = [-1, -1]     # milestone number for reactant and product
        
        self.reactant_milestone = []   # milestone list for reactant
        
        self.product_milestone = []    # milestone list for product
        
        self.reactant = reactant     # voronoi cell for reactant
        
        self.product = product       # voronoi cell for product
         
        self.MFPT = MFPT       
        
        self.namd_conf = False       # additional modification required for NAMD configuration
        
        self.colvarsNum = colvarsNum  # number of colvars, used for read command
        
        self.forceConst = 1  # force constant for harmonic constrain
        
        self.trajWidths = trajWidths  # width for each traj output, default = 13
        
        self.customColvars = 0       # customized colvar: 0 - no; 1- yes
        
        self.colvarsTrajFrequency = colvarsTrajFrequency   # how often to output colvars
        
        self.colvarsRestartFrequency = colvarsRestartFrequency    # how often to write to file
        
        self.AnchorPath = AnchorPath   # file path for anchor
        
        self.AnchorNum = AnchorNum     # total number of anchor
        
        self.new_anchor = False         # find new anchor
        
        self.anchor_dist = 100.0          # new anchor seperation distance
            
        self.bincoordinates = bincoordinates  # coordinates file name
        
        self.binvelocities = binvelocities # velocity file name
        
        self.extendedSystem = extendedSystem    # extended system file name
        
        self.coor = coor     # coordinates
        
        self.nframe = nframe    # number of sampling frame
        
        self.startTraj = startTraj    # initial sampling frame 
        
        self.trajPerLaunch = trajPerLaunch    # number of free trajs to launch each time
        
        self.freeTraj_walltime = freeTraj_walltime  # walltime for free trajectories
        
        self.interval = interval    # interval between each frame taken
        
        self.structure = structure   # structure file name; psf
        
        self.coordinates = coordinates   # structure file name; pdb
        
        self.outputname = outputname    # output name
        
        self.username = username    # user name on cluster
        
        self.tolerance = tolerance   # tolerance for MFPT convergency
        
        self.err_sampling = 1000    # number of error sampling
        
        self.sing = True      # k matrix singularity
        
        self.kij = []       #kij matrix
        
        self.index = []     # milestone index
        
        self.flux = []      #flux
        
        self.__read_input()
        
        import os
        scriptPath = os.path.dirname(os.path.abspath(__file__)) 
        nodeFile = scriptPath + '/nodelist'
        if os.path.isfile(nodeFile):
            self.__read_nodelist(nodeFile)
    
    def __read_input(self):
        import os
        scriptPath = os.path.dirname(os.path.abspath(__file__)) 
        inputfolder = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_input'
        inputFile = inputfolder + '/input.txt'
        with open(file=inputFile) as f:
            for line in f:
                line = line.rstrip()
                info = line.split(" ")
                
                if '#' in info:
                    continue
                
                if "method" in info:
                    self.method = int(info[1])
                           
                if "initial_iteration" in info:
                    self.iteration = int(info[1]) - 1
                if "max_iteration" in info:
                    self.maxIteration = int(info[1])
                
                if "milestoneSearch" in info:
                    self.milestone_search = int(info[1])
                    
                if "pbc" in line:
                    rm = line.replace(","," ").replace("  "," ").split(" ")
                    rm.pop(0)
                    self.pbc = list(map(int, rm))

                if "structure" in info:
                    self.structure = info[1]
                if "coordinates" in line:
                    self.coordinates = info[1]
                if "outputname" in line:
                    self.outputname = info[1]
                if "NVT" in line:
                    if str(info[1]).lower() == 'true' or 'yes' or 'on':
                    self.NVT = True

                if "time_step" in line:
                    self.timeFactor = float(info[1])    
                    
                if "initial_traj" in line:
                    self.initial_traj = int(info[1])
                if "initial_time" in line:
                    self.initialTime = int(info[1])                  
                if "ignore_new_ms" in line:
                    self.ignorNewMS = True if info[1] == 'yes' or info[1] == 'on' else False   
                    
                if "colvarType" in line:
                    self.colvarType = info[1]   
                if "custom_colvar" in line:
                    self.colvarsNum = int(info[1])
                if "colvarsTrajFrequency" in line:
                    self.colvarsTrajFrequency = info[1]
                if "colvarsRestartFrequency" in line:
                    self.colvarsRestartFrequency = info[1]
                if "customColvars" in line:
                    self.customColvars = 1 if info[1] == 'yes' or info[1] == 'on' else 0
                if "force_const" in line:
                    self.forceConst = int(info[1])
                    
                if "anchorsNum" in line:
                    self.AnchorNum = int(info[1])    
                if "find_new_anchor" in line:
                    if str(info[1]).lower() == 'true' or 'yes' or 'on':
                        self.new_anchor = True
                if "new_anchor_dist" in line:
                    self.anchor_dist = float(info[1])         
#                if "anchorsPath" in line:
#                    self.AnchorPath = info[1]
                            
                # reactant_milestone
                if "reactant" in line:
                    rm = line.replace(","," ").replace("  "," ").split(" ")
                    rm.pop(0)
                    if len(rm) == 2:
                        self.reactant = list(map(int, rm))
                    elif len(rm) == 1:
                        self.reactant = [int(rm[0])]
                # product_milestone
                if "product" in line:
                    pm = line.replace(","," ").replace("  "," ").split(" ")
                    pm.pop(0)
                    if len(pm) == 2:
                        self.product = list(map(int, pm))
                    elif len(pm) == 1:
                        self.product = [int(pm[0])]                       
                    
                if "total_trajs" in line:
                    self.nframe = int(info[1])    
                if "start_traj" in line:
                    self.startTraj = int(info[1])                  
                if "traj_per_launch" in line:
                    self.trajPerLaunch = int(info[1])  
                if "interval" in line:
                    self.interval = int(info[1])                
                
                if "tolerance" in line:
                    self.tolerance = float(info[1])   
                if "error_sampling" in line:    
                    self.err_sampling = int(info[1])   
                      
                if "jobsubmission" in line:
                    self.jobsubmit = str(info[1])
                if "jobcheck" in line:
                    self.jobcheck = str(info[1])
                if "username" in line:
                    self.username = str(info[1])

                if "namd_conf_custom" in line:
                    if str(info[1]).lower() == 'true' or 'yes' or 'on':
                        self.namd_conf = True
                    
        self.trajWidths = [13]
        for i in range(self.colvarsNum + self.AnchorNum):
            self.trajWidths.append(23)

    def __read_nodelist(self, nodelist):
        with open(file=nodelist) as f:
            for line in f:
                if "#" in line:
                    continue
                line = line.split("\n")
                self.nodes.append(str(line[0]))

    def initialize(self):
        import pandas as pd
        import os
        import re
        scriptPath = os.path.dirname(os.path.abspath(__file__)) 
        inputfolder = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_input'
        outputfolder = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_output'
        self.anchors = pd.read_fwf(inputfolder+'/anchors.txt', header=None).values
        self.AnchorPath = inputfolder+'/anchors.txt'
        crdfolder = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/crd'
        if not os.path.exists(crdfolder):
            os.makedirs(crdfolder)
        if not os.path.exists(outputfolder):
            os.makedirs(outputfolder) 
        currentfolder = outputfolder + '/current'
        if not os.path.exists(currentfolder):
            os.makedirs(currentfolder)     
        # read initial run time for seek and time step setup
        with open(inputfolder + '/free.namd', 'r') as f:   
            for line in f:
                info = line.split("#")[0].split()
                # info = line.split()
                if len(info) < 1:
                    continue
                if "run" in info[0].lower():
                    self.freeTraj_walltime = int(re.findall(r"[-+]?\d*\.\d+|\d+", info[1])[0])
                    break
                if "timestep" in info[0].lower():
                    try: 
                        self.timeFactor = float(re.findall(r"[-+]?\d*\.\d+|\d+", info[1])[0])
                    except:
                        continue
        # read restart frequency to get the name of restart files
        # such restart files will be used as the initial position for free traj
        with open(inputfolder + '/sample.namd', 'r') as f:
            for line in f:
                info = line.split("#")[0].split()
                if len(info) < 1:
                    continue
                if "restartfreq" in info[0].lower():
                    self.sampling_interval = int(re.findall(r"[-+]?\d*\.\d+|\d+", info[1])[0])
        # initial log file
        from log import log
        logname = currentfolder + '/log'
        if os.path.exists(logname):
            os.remove(logname)            
        log("Initialized with {} anchors.".format(self.AnchorNum))
#        print(self.namd_conf ) 


if __name__ == '__main__':
    new = parameters()
    new.initialize()
    print(new.timeFactor)
