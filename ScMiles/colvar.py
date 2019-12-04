#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 14:44:51 2018

@author: Wei Wei

This code generates the colvar configuration file that required by NAMD.

Two constraints will be considered:
    1. RMSD(x, anchor_a) = RMSD(x, anchor_b).
    2. RMSD(x, any_anchors_besides_a_or_b) > RMSD(x, anchor_a) &&
       RMSD(x, any_anchors_besides_a_or_b) > RMSD(x, anchor_b).
       
Note:        
    RMSD(x, anchor_a): the root mean square displacement from anchor_a to x
"""

from log import log
import os


class colvar:
    def __init__(self, parameter, anchor1=None, anchor2=None, 
                 var1=None, var2=None, free=None, initial=None, 
                 config_path=None):
        self.parameter = parameter
        self.anchor1 = anchor1
        self.anchor2 = anchor2
        self.var1 = var1
        self.var2 = var2
        self.free = free
        self.initial = initial
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.input_dir = self.parent_path + '/my_project_input'
        self.config_path = self.path + "/colvar_free.conf" if self.free == 'yes' else self.path + "/colvar.conf"

    def __exit__(self, exc_type, exc_value, traceback):
        return 

    def __repr__(self) -> str:
        return ('Colvar generator')             

#    def __collective_vari_1(self, name=None, coeff=None, space=0):
#        '''
#        Change this function for different 1D case.
#        Follow the format in Colvars to define a collective variable.
#        For the commands below, it generates the following.
#        
#          dihedral {
#            name psi
#            group1 atomNumbers 7
#            group2 atomNumbers 9
#            group3 atomNumbers 15
#            group4 atomNumbers 17
#          }
#          
#        '''
#        fconf = open(self.config_path, 'a')
#        print("  " * space + "  dihedral {", file=fconf)
#        if name:
#            print("  " * space + "    name {}".format(name), file=fconf) 
#        if coeff:
#            print("  " * space + "    componentCoeff {}".format(coeff), file=fconf) 
#        print("  " * space + "    group1 atomNumbers 7", file=fconf)
#        print("  " * space + "    group2 atomNumbers 9", file=fconf)
#        print("  " * space + "    group3 atomNumbers 15", file=fconf)
#        print("  " * space + "    group4 atomNumbers 17", file=fconf)
#        print("  " * space + "  }", file=fconf)
#        fconf.close()

    def __get_colvar_names(self):
        count = 0
        section = 1
        with open(file=self.input_dir + '/colvar.txt') as f:
            for line in f:
                if '{' in line:
                    count += 1
                if '}' in line:
                    count -= 1
                    if count == 0:
                        section += 1
                        if section > 2:
                            break
                        else:
                            continue
                if section == 1:
                    if "name" in line:
                        info = line.split("#")[0].split()
                        if len(info) >= 2 and info[0] == "name":
                            self.var1 = str(info[1])
                if section == 2:
                    if "name" in line:
                        info = line.split("#")[0].split()
                        if len(info) >= 2 and info[0] == "name":
                            self.var2 = str(info[1])

    def __collective_vari_1(self, name=None, coeff=None, space=0):
        tmp = []
        count = 0
        with open(file=self.input_dir+'/colvar.txt') as f:
            for line in f:
                if '{' in line:
                    count += 1
                if '}' in line:
                    count -= 1
                if "name" in line:
                    info = line.split("#")[0].split()
                    if len(info) >= 2 and info[0] == "name":
                        self.var1 = str(info[1])
                tmp.append(line + '\n')
                if count == 0:
                    break
        fconf = open(self.config_path, 'a')
        for line in tmp:
            print("  " * space + "  " + line, file=fconf)
        fconf.close()
        if not self.var1:
            log("Colvar Error. Please name your colvars.")

    def __collective_vari_2(self, name=None, coeff=None, space=0):
        # scriptPath = os.path.dirname(os.path.abspath(__file__))
        # inputdir = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_input'
        tmp = []
        count = 0
        section = 1
        with open(file=self.input_dir+'/colvar.txt') as f:
            for line in f:
                if '{' in line:
                    count += 1
                if '}' in line:
                    count -= 1
                    if count == 0:
                        if section == len(self.parameter.anchors[0]): 
                            tmp.append(line + '\n')
                        section += 1
                        continue
                if section == 2:
                    if "name" in line:
                        info = line.split("#")[0].split()
                        if len(info) >= 2 and info[0] == "name":
                            self.var2 = str(info[1])
                    tmp.append(line + '\n')   
        fconf = open(self.config_path, 'a')
        for line in tmp:
            print("  " * space + "  " + line, file=fconf)
        fconf.close()
        if not self.var2:
            log("Colvar Error. Please name your colvars.")

    def __rmsd_to_anchor(self, anchor, coeff=None, space=0):
        # scriptPath = os.path.dirname(os.path.abspath(__file__))
        # inputdir = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_input'
        tmp = []
        count = 0
        first = True
        section = 1
        name_get = False
        with open(file=self.input_dir+'/colvar.txt') as f:
            for line in f:
                if '{' in line:
                    first = False
                    count += 1
                if '}' in line:
                    count -= 1
                    if count == 0 and first == False:
                        if section == len(self.parameter.anchors[anchor-1]) + 1: 
                            tmp.append(line + '\n')
                        section += 1
                        continue
                if section == len(self.parameter.anchors[anchor-1]) + 1: 
                    if 'name' in line and name_get == False:
                        line = "  name rmsd" + str(anchor)
                        name_get = True
#                    if 'anchor' in line:
#                        line = line.replace("anchor", '('+str(self.parameter.anchors[anchor-1][0])+')')
                    if 'anchor.x' in line:
                        line = line.replace("anchor.x", '('+str(self.parameter.anchors[anchor-1][0])+')')
                    if 'anchor.y' in line:
                        line = line.replace("anchor.y", '('+str(self.parameter.anchors[anchor-1][1])+')')
                    tmp.append(line + '\n')
                
        fconf = open(self.config_path, 'a')
        for line in tmp:
            print("  " * space + "  " + line, file=fconf)
        fconf.close()
        
#    def __rmsd_to_anchor(self, anchor, coeff=None, space=0):
#        '''
#        Change this function for different 1D case.
#        Follow the format in Colvars to define the distance measurement.
#        For the commands below, it generates the following.
#        
#        colvar {
#          name rmsd1
#          customFunction abs(psi - (-165.0))
#          dihedral {
#            name psi
#            group1 atomNumbers 7
#            group2 atomNumbers 9
#            group3 atomNumbers 15
#            group4 atomNumbers 17
#          }
#        }
#          
#        '''
#        fconf = open(self.config_path, 'a')
#        name = "rmsd" + str(anchor)
#        print("\n" + "  " * space + "colvar {", file=fconf)
#        print("  " * space + "  name {:5}".format(name), file=fconf)
#        func = "abs(psi - (" + str(self.parameter.anchors[anchor-1][0]) + "))"
#        print("  " * space + "  customFunction {}".format(func), file=fconf)
#        fconf.close()
#        self.__collective_vari_1()
#        fconf = open(self.config_path, 'a')
#        print("  " * space + "}", file=fconf)
#        fconf.close()

    def generate(self):    
        # scriptPath = os.path.dirname(os.path.abspath(__file__))
        config_path = self.path + "/colvar_free.conf" if self.free == 'yes' else self.path + "/colvar.conf"
        
        colvarsTrajFrequency = self.parameter.colvarsTrajFrequency
        colvarsRestartFrequency = self.parameter.colvarsRestartFrequency
        
        if self.initial == 'yes': 
            outputFrequency = 1 
        elif self.free == 'yes':
            outputFrequency = colvarsTrajFrequency
        else:
            outputFrequency = colvarsTrajFrequency
            
        self.__frequency(outputFrequency, colvarsRestartFrequency)
        
        if self.free == 'yes':
            fconf = open(config_path, 'a')
            print("scriptedColvarForces on", file=fconf)
            fconf.close()
        
        if self.parameter.customColvars == 1:
            self.__append_customColvars()
        
        if self.free != 'yes':
            if len(self.parameter.anchors[0]) == 1:
                self.__constraint1D1()
                self.__harmonic1D()
            else:
                self.__get_colvar_names()
                self.__constraint2D1()
                colvarList, centers = self.__constraint2D2()
                self.__harmonic2D()
                self.__harmonicWalls(colvarList, centers)
        else:
            for i in range(self.parameter.AnchorNum):
                self.__rmsd_to_anchor(i+1)

    def __frequency(self, colvarsTrajFrequency, colvarsRestartFrequency):
        fconf = open(self.config_path, 'w+')
        print("colvarsTrajFrequency      {}".format(colvarsTrajFrequency), file=fconf)
        print("colvarsRestartFrequency	 {}".format(colvarsRestartFrequency), file=fconf)
        fconf.close()

    def __append_customColvars(self):
        # scriptPath = os.path.dirname(os.path.abspath(__file__))
        # inputdir = os.path.abspath(os.path.join(scriptPath, os.pardir)) + '/my_project_input'
        custom_file = self.input_dir + '/custom.colvar'
        fconf = open(self.config_path, 'a')
        print("", file=fconf)
        with open(file=custom_file) as f_custom:
            for line in f_custom:
                print(line, file=fconf)
        fconf.close()

    def __constraint1D1(self):
        fconf = open(self.config_path, 'a')
        print("\ncolvar {", file=fconf)
        print("  name colv", file=fconf)
        fconf.close()
        self.__collective_vari_1()
        fconf = open(self.config_path, 'a')
        print("}\n\n", file=fconf)
        fconf.close()

    def __harmonic1D(self):
        fconf = open(self.config_path, 'a')
        print("\nharmonic {", file=fconf)
        print("  colvars colv", file=fconf)
        center = (self.parameter.anchors[self.anchor1-1][0] + self.parameter.anchors[self.anchor2-1][0]) / 2
        if self.parameter.pbc != [] and abs(self.anchor1 - self.anchor2) > 1:
            center = 180
        print("  centers {}".format(center), file=fconf)
        print("  forceConstant {}".format(self.parameter.forceConst), file=fconf)
        print("}", file=fconf)
        fconf.close()

    def __constraint2D1(self):
        fconf = open(self.config_path, 'a')
        print("\ncolvar {", file=fconf)
        print("  name neighbor", file=fconf)
        # print(self.var1, self.var2)
        customFunc = "  customFunction sqrt((" + self.var1 + "-(" + \
            str(self.parameter.anchors[self.anchor1-1][0]) + "))^2 + (" + \
            self.var2 + "-(" + str(self.parameter.anchors[self.anchor1-1][1]) + \
            "))^2) - sqrt((" + self.var1 + "-(" + str(self.parameter.anchors[self.anchor2-1][0]) \
            + "))^2 + (" + self.var2 + "-(" + str(self.parameter.anchors[self.anchor2-1][1]) + "))^2)"
        print(customFunc, file=fconf)
        fconf.close()
    
        self.__collective_vari_1(space=1)
        self.__collective_vari_2(space=1)
    
        fconf = open(self.config_path, 'a')
        print("}\n\n", file=fconf)
        fconf.close()

    def __constraint2D2(self):
        colvarList = ""
        centers = ""
        for i in range(self.parameter.AnchorNum):
            if i + 1 != self.anchor1 and i + 1 != self.anchor2:
                fconf = open(self.config_path, 'a')
                print("colvar {", file=fconf)
                print("  name {}_{}".format(i + 1, self.anchor1), file=fconf)
                customFunc = "  customFunction sqrt((" + self.var1 + "-(" + \
                    str(self.parameter.anchors[i][0]) + "))^2 + (" + self.var2 + \
                    "-(" + str(self.parameter.anchors[i][1]) + "))^2) - sqrt((" + \
                    self.var1+ "-(" + str(self.parameter.anchors[self.anchor1-1][0]) + \
                    "))^2 + (" + self.var2 + "-(" + \
                    str(self.parameter.anchors[self.anchor1-1][1]) + "))^2)"
                print(customFunc, file=fconf)
                colvarList += str(i + 1) + "_" + str(self.anchor1) + " "
                centers += "0 "
                fconf.close()
                self.__collective_vari_1(space=2)
                self.__collective_vari_2(space=2)
                fconf = open(self.config_path, 'a')
                print("}\n", file=fconf)       
    
                print("colvar {", file=fconf)
                print("  name {}_{}".format(i + 1, self.anchor2), file=fconf)
                customFunc = "  customFunction sqrt((" + self.var1 + "-(" + \
                    str(self.parameter.anchors[i][0]) + "))^2 + (" + self.var2 + \
                    "-(" + str(self.parameter.anchors[i][1]) + "))^2) - sqrt((" + \
                    self.var1+ "-(" + str(self.parameter.anchors[self.anchor2-1][0]) + \
                    "))^2 + (" + self.var2 + "-(" + \
                    str(self.parameter.anchors[self.anchor2-1][1]) + "))^2)"
                print(customFunc, file=fconf)
    
                colvarList += str(i + 1) + "_" + str(self.anchor2) + " "
                centers += "0 "
                fconf.close()
                self.__collective_vari_1(space=2)
                self.__collective_vari_2(space=2)
                fconf = open(self.config_path, 'a')
                print("}\n", file=fconf)
                fconf.close()
        return colvarList, centers
    
    def __harmonic2D(self):
        fconf = open(self.config_path, 'a')
        print("harmonic {", file=fconf)
        print("  colvars neighbor", file=fconf)
        center = 0
        print("  centers {}".format(str(center)), file=fconf)
        print("  forceConstant {}".format(self.parameter.forceConst), file=fconf)
        print("}", file=fconf)
        fconf.close()

    def __harmonicWalls(self, colvarList, centers):
        fconf = open(self.config_path, 'a')
        print("\n", file=fconf)
        print("harmonicWalls {", file=fconf)
        print("  colvars {}".format(colvarList), file=fconf)
        print("  lowerWalls {}".format(centers), file=fconf)
        print("  lowerWallConstant {}".format(self.parameter.forceConst), file=fconf)
        print("}", file=fconf)
        fconf.close()


if __name__ == '__main__':
    from parameters import *
    new = parameters()
    new.initialize()
    print(new.anchors)
    colvar(new, anchor1=1, anchor2=2).generate()

    