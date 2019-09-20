#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 11:06:15 2018

@author: Wei Wei

Main script which inclues major workflow.

"""

import time
import numpy as np
from parameters import *
from network_check import *
from log import log
from sampling import *
from milestones import *
from analysis import analysis_kernel
from traj import *

# run free trajectories without sampling
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--skipSampling', action='store_true', help='skip sampling',
                    required=False)
args = parser.parse_args()  
status = 1 if args.skipSampling  else 0

# initialize environment
MFPT_temp = 1
MFPT_converged = False
parameter = parameters()
parameter.initialize()
jobs = run(parameter)
samples = sampling(parameter, jobs)

# initialize with reading anchor info and identifying milestones 
parameter.MS_list = milestones(parameter).initialize(status=0)

#initialize iteration number
parameter.iteration = 0

while True:
    free_trajs = traj(parameter, jobs)
    
#    print(parameter.MS_list)
    # apply harmonic constraints that populate samples at each milestones.
    if parameter.MS_list != parameter.finished_constain:
        samples.constrain_to_ms()   # start to constrain
        time.sleep(60)
        
    samples.check_sampling()    # check if the samplings are finished

    # next iteration; for iteration methods
    if parameter.method == 1:
        parameter.iteration += 1 
        print("Iteration # {}".format(parameter.iteration))
        log("Iteration # {}".format(parameter.iteration))
        free_trajs.iteration_initialize()
    else:
        parameter.iteration = 1 
            
    # lauch free runs from the samples 
    current_snapshot = free_trajs.launch()
    
    # compute kernel, flux, probability, life time of each milstone, and MFPT as well
    analysis_kernel(parameter)
    
    # If any NEW milestone has been reached
    if len(parameter.MS_new) != 0 and not parameter.ignorNewMS:
        log("Reached {} new milestone(s).".format(len(parameter.MS_new)))
        temp = parameter.MS_new.copy()
        for ms in temp:
            name = 'MS' + ms
            parameter.MS_list.add(name)
            parameter.MS_new.remove(ms)
            if parameter.method == 1:
                parameter.finished_constain.add(name)
        del temp   
#        continue
    
    # break if all the snapshots have been used
    if current_snapshot >= parameter.nframe:
        break
    
    # break if reach max iteration
    if parameter.iteration >= parameter.maxIteration:
        break

        
    # if no results
    elif np.isnan(parameter.MFPT) or parameter.MFPT < 0:
        log("Preparing for more free trajectories...")
        MFPT_temp = 1
        parameter.MFPT = 0
        parameter.Finished = set()
        
    # If the calculated MFPT is not converged yet, more runs.
    elif np.abs(parameter.MFPT - MFPT_temp) / MFPT_temp > parameter.tolerance:
        log("Preparing for more free trajectories...")
        MFPT_temp = parameter.MFPT
        parameter.MFPT = 0
        parameter.Finished = set()
        
    # Break if MFPT is converged.
    else:
        print("Previous MFPT: {}".format(MFPT_temp))
        print("Current MFPT: {}".format(parameter.MFPT))
        MFPT_converged = True
        break

# Double check 
if MFPT_converged == True:
    print("MFPT converged. Exiting...")
    log("MFPT converged. Exiting...")
else:
    print("Error: MFPT not converged! Exiting...")
    log("Error: MFPT not converged! Exiting...")
