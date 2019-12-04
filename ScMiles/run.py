#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 17:25:27 2018

@author: Wei Wei

This subroutine generates NAMD configuration based on templete and submits jobs.
"""

import os, time
from shutil import copy
import subprocess
from shutil import copyfile
#from find_milestone import *
#from milestones import *
from namd_conf_custom import *


class run:
    
    def __init__(self, parameter) -> None:
        self.parameter = parameter
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return 
            
    def __repr__(self) -> str:
        return ('Submit jobs.')

    def submit(self, a1=None, a2=None, snapshot=None, frame=None, initial=None, initialNum=None):
        '''job submission'''
        scriptPath = os.path.dirname(os.path.abspath(__file__)) 
        inputdir = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_input'
        templateScript = inputdir + "/submit"
        newScript = self.__prepare_script(templateScript, a1, a2, snapshot, initial, initialNum)
        templatepath = inputdir 
        self.__prepare_namd(templatepath, a1, a2, snapshot,frame, initial, initialNum)
        
        lst = sorted([a1, a2])
        name = str(lst[0]) + '_' + str(lst[1])
        MSpath = os.path.join(scriptPath, os.pardir) +  '/crd/' + name 
    #    if not os.path.exists(MSpath):
    #        os.makedirs(MSpath)
        
        if snapshot is not None:
            folderPath = MSpath + '/' + str(self.parameter.iteration) + "/" + str(snapshot)
    #        if parameter.iteration >= 1:
    #            get_initial_ms(parameter, folderPath)
            origColvar = scriptPath + "/colvar_free.conf"
            destColvar = folderPath + "/colvar_free.conf"
        elif initial is not None:
            pardir = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/crd/seek'
            origColvar = scriptPath + "/colvar_free.conf"
            destColvar = pardir + "/structure" + str(a1) + "/" + str(initialNum) + "/colvar_free.conf"
        else:
            origColvar = scriptPath + "/colvar.conf"
            destColvar = MSpath + "/colvar.conf"
        copy(origColvar, destColvar)    
             
        while True:
            out = subprocess.check_output([self.parameter.jobcheck,'-u', self.parameter.username]).decode("utf-8").split('\n')
            if len(out) -2 < 999999999:  # allowed number of jobs
                subprocess.run([self.parameter.jobsubmit,newScript])
                break
            else:
                time.sleep(60)

    def check(self, a1=None, a2=None, MSname=None, JobName=None):
        '''check queue to see if all jobs are finished'''
        out = subprocess.check_output([self.parameter.jobcheck,'-u', self.parameter.username]).decode("utf-8").split('\n')
        if a1 is not None and a2 is not None:
            name = 'MS' + str(a1) + '_' + str(a2)
        if MSname is not None:
            name = MSname
        if JobName is not None:
            name = JobName
        job = []
        if self.parameter.jobcheck == 'squeue' and len(out) > 2:
            job.append(list(filter(None, out[1].split(' '))))
        for i in range(2, len(out)-1):
            job.append(list(filter(None, out[i].split(' '))))
            
        for i in range(len(job)):
            if MSname is not None and job[i][2] == name:
                return False  # not finished
            if JobName is not None and job[i][2].split('_')[0] == name:
                return False
        return True # finished
    
    def __prepare_script(self, template, a1, a2, snapshot=None, initial=None, initialNum=None):
        '''mordify job submission file'''
        from fileinput import FileInput
        import os
        filePath = os.path.dirname(os.path.abspath(__file__)) 
        pardir = os.path.abspath(os.path.join(filePath, os.pardir))
        seekpath = pardir + '/crd/seek'
        lst = sorted([a1, a2])
        name = str(lst[0]) + '_' + str(lst[1])
        MSpath = pardir + '/crd/' + name 
    
        if snapshot is not None:
            newScriptPath = MSpath + '/' + str(self.parameter.iteration) + "/" + str(snapshot)
            newScript = newScriptPath + "/submit"
        elif initial is not None:
            newScriptPath = seekpath + '/structure' + str(a1) + "/" + str(initialNum)
            newScript = newScriptPath + '/submit'
        else:
            newScriptPath = MSpath
            newScript = newScriptPath + "/MS" + name
        if not os.path.exists(newScriptPath):
            os.makedirs(newScriptPath)
    
        copyfile(template, newScript)

        with FileInput(files=newScript, inplace=True) as f:
            for line in f:
                line = line.strip()
#                line = line.lower()
                info = line.split()
#                 info = line.split("#")[0].split()
                if not info:
                    continue
                                  
                if "source" in line:
                    if self.parameter.nodes:
                        import numpy as np
                        rand = np.random.uniform(0,len(self.parameter.nodes),1)
                        info[2] = 'hostname="' + self.parameter.nodes[int(rand)] + '"'
                    else:
                        info.insert(0, '#')
                        
                if "name" in line:
                    place = info.index('name')
                    if snapshot is not None:
                        info[place] = 'MILES' + '_' + str(a1) + '_' + str(a2) + '_' + str(snapshot)
                    elif initial is not None:
                        info[place] = 'a' + str(a1)
                    else:
                        info[place] = 'MS' + str(a1) + '_' + str(a2) 
                
                if snapshot is not None:
                    path = MSpath + '/' + str(self.parameter.iteration) + '/' + str(snapshot) 
                elif initial is not None:
                    path = seekpath + '/structure' + str(a1) + "/" + str(initialNum)
                else:
                    path = MSpath 
                    
                if "path" in line:
                    place = info.index('path')
                    info[place] = path
                if "namd" in line:
                    place = info.index('namd')
                    if snapshot is None and initial is None:
                        info[place] = './sample.namd'
                    else:
                        info[place] = './free.namd'
                line = " ".join(str(x) for x in info)
                print(line)
        return newScript     

    def __prepare_namd(self, template, a1=None, a2=None, snapshot=None,frame=None, initial=None, initialNum=None):
        '''modify namd configuration file'''
        from fileinput import FileInput
        from random import randrange as rand 
        import re
        
        inputdir = template
        
        if snapshot is not None:
            template = template + "/free.namd"   
        elif initial is not None:
            template = template + "/free.namd"  
        else:
            template = template + "/sample.namd" 
        
        filePath = os.path.dirname(os.path.abspath(__file__)) 
        pardir = os.path.abspath(os.path.join(filePath, os.pardir))
     
        lst = sorted([a1, a2])
        name = str(lst[0]) + '_' + str(lst[1])
        MSpath = pardir + '/crd/' + name if initial is None else pardir + '/crd/seek/structure' + str(a1)
    
        if snapshot is not None:
            filename = "/" + str(self.parameter.iteration) + "/" + str(snapshot) + "/free.namd"    ######### miles
        elif initial is not None:
            filename = "/" + str(initialNum) + "/free.namd"
        else:
            filename = "/sample.namd" 
        
        newNamd = MSpath + filename
        copyfile(template, newNamd)
        
        if snapshot is not None and os.path.isfile(MSpath + "/" + str(self.parameter.iteration) + "/" +
                                                   str(snapshot) + '/enhanced'):
            enhanced = 1
        else:
            enhanced = 0
            
        tmp = []
        colvar_commands = False
        with open(newNamd, 'r') as f:
            for line in f:
#                line = line.lower()
#                 info = line.split("#")[0].split()
                info = line.split()
                if info == []:
                    continue                
                if "colvars" in info and "on" in info:
                    colvar_commands = True
                if "colvarsConfig" in info and colvar_commands:
                    if initial is not None or snapshot is not None:
                        info[1] = 'colvar_free.conf'
                    else:
                        info[1] = 'colvar.conf'
                    l = " ".join(str(x) for x in info)+"\n"
                    tmp.append(l)
                    continue
                
                if "run" in info or 'minimize' in info:
#                    if info[0] == '#':
#                        continue
                    if not colvar_commands:
                        tmp.append('colvars on\n')
                        info[0] = 'colvarsConfig'
                        if initial is not None or snapshot is not None:
                            info[1] = 'colvar_free.conf\n\n'
                        else:
                            info[1] = 'colvar.conf\n\n'
                        l = " ".join(str(x) for x in info)
                        tmp.append(l)
                        colvar_commands = True
                    if initial is not None:
                        with open(file=filePath+'/tclScript_seek.txt') as f_tcl:
                            for l in f_tcl:
                                if "qsub" in l:
                                    kill = l.strip()
                                    killswitch = kill.split()
                                    if self.parameter.jobsubmit == "qsub":
                                        killswitch.pop(0)
                                    else:
                                        killswitch[0] = '#'
                                    a = " ".join(str(x) for x in killswitch)
                                    tmp.append(a +'\n')   
                                elif "sbatch" in l:
                                    kill = l.strip()
                                    killswitch = kill.split()
                                    if self.parameter.jobsubmit == "sbatch":
                                        killswitch.pop(0)
                                    else:
                                        killswitch[0] = '#'
                                    a = " ".join(str(x) for x in killswitch)
                                    tmp.append(a +'\n')      
                                else:
                                    tmp.append(l)
                        tmp.append('\n')
                    if snapshot is not None:
                        with open(file=filePath+'/tclScript_step2.txt') as f_tcl:
                            for l in f_tcl:
                                if "qsub" in l:
                                    kill = l.strip()
                                    killswitch = kill.split()
                                    if self.parameter.jobsubmit == "qsub":
                                        killswitch.pop(0)
                                    else:
                                        killswitch[0] = '#'
                                    a = " ".join(str(x) for x in killswitch)
                                    tmp.append(a +'\n')   
                                elif "sbatch" in l:
                                    kill = l.strip()
                                    killswitch = kill.split()
                                    if self.parameter.jobsubmit == "sbatch":
                                        killswitch.pop(0)
                                    else:
                                        killswitch[0] = '#'
                                    a = " ".join(str(x) for x in killswitch)
                                    tmp.append(a +'\n')      
                                else:
                                    tmp.append(l)
                        tmp.append('\n')
                tmp.append(line)     
                
        with open(newNamd, 'w') as f:
            for i in range(len(tmp)):
                f.write(tmp[i])
                    
        with FileInput(files=newNamd, inplace=True) as f:
            for line in f:
                line = line.strip()
#                line = line.lower()
                info = line.split()
                
                if "coordinates" in line:
                    info[1] = pardir + '/my_project_input/pdb/' + str(lst[0]) + ".pdb"
                    if snapshot is None and initial is None and self.parameter.milestone_search == 1:
                        info[1] = "./seek.ms.pdb" 
                        
                if "outputname" in line:
                    info[1] = self.parameter.outputname
                    
                if "seed" in line:
                    info[1] = rand(10000000, 99999999)
            
                if "bincoordinates" in line or "binCoordinates" in line:
                    if snapshot is not None:
                        info[0] = 'bincoordinates'
                        if self.parameter.iteration == 1:
                            info[1] = '../../restarts/' + self.parameter.outputname + '.' + \
                                      str(frame*self.parameter.sampling_interval) + '.coor'
                        else:
                            info[1] = self.parameter.outputname + '.coor'
                
                if "binvelocities" in line or "binVelocities" in line:
                    if snapshot is not None:
                        if self.parameter.iteration == 1:
                            info[1] = '../../restarts/' + self.parameter.outputname + '.' + \
                                      str(frame*self.parameter.sampling_interval) + '.vel'
                        else:
                            if enhanced == 0:
                                info[0] = 'binvelocities'
                            info[1] = self.parameter.outputname + '.vel'
            
                if "extendedSystem" in line or "extendedsystem" in line:
                    if snapshot is not None:
                        info[0] = 'extendedSystem'
                        if self.parameter.iteration == 1:
                            info[1] = '../../restarts/' + self.parameter.outputname + '.' + \
                                      str(frame * self.parameter.sampling_interval) + '.xsc'
                        else:
                            info[1] = self.parameter.outputname + '.xsc'
                                
                if "restartsave" in line:
                    if snapshot is not None or initial == 'yes':
                        info[1] = "off"
    
                if "binaryrestart" in line:
                    if initial == 'yes':
                        info[1] = "no"    
                                        
                if "temperature" in line and "pressure" not in line:
                    if self.parameter.iteration > 1:
                        info[0] = '#temperature'
                    if enhanced == 1:
                        info[0] = 'temperature'
    
                if "lreplace" in line:
#                    line = re.sub(r'[^\w]', ' ', line)
                    if self.parameter.colvarsNum == 0:
                        info[0] = '#set'
                    else:
                        if ']' in info[-1]:
                            info[-1] = str(self.parameter.colvarsNum - 1) 
                            info.append(']')
                        else:
                            info[-2] = str(self.parameter.colvarsNum - 1) 
                            
                if "a111" in line:
                    if snapshot is None:
                        info[2] = str(a1) 
                    else:# snapshot != None:
                        if self.parameter.iteration == 1:
                            info[2] = str(a1) 
                        else:
                            path_start = MSpath + '/' + str(self.parameter.iteration) + '/' + str(snapshot)
                            info[2] = str(get_initial_ms(path_start)[0]) 
                        
                if "a222" in line:
                    if snapshot is None:
                        info[2] = str(a2) 
                    else: # snapshot != None:
                        if self.parameter.iteration == 1:
                            info[2] = str(a2) 
                        else:
                            path_start = MSpath + '/' + str(self.parameter.iteration) + '/' + str(snapshot)
                            info[2] = str(get_initial_ms(path_start)[1]) 
                
                if initial is not None and "run" in info:
                    info[1] = str(self.parameter.initialTime * 1000)

                line = " ".join(str(x) for x in info)
                print(line)
        
#        print(filename, self.parameter.namd_conf)
#        if filename == "/sample.namd" and self.parameter.namd_conf == True:
#            namd_conf_mod(inputdir, newNamd, a1)
            
        
def get_initial_ms(path):
    '''get initial milestone for each free trajectory based on the folder name'''
    import re
    path_split = path.split("/")
    initial_ms = list(map(int,(re.findall('\d+', path_split[-3]))))
    with open(path + '/start.txt', 'w+') as f1:
        print(initial_ms[0], initial_ms[1], file=f1)    
    return initial_ms


if __name__ == '__main__':
    new = parameters()
    jobs = run(new)
    jobs._run__prepare_namd('./test.namd', a1=1, a2=2)

    
