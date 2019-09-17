#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 16:27:08 2019

@author: weiw

Customized modification of namd configuration
Read pdb for cellbasisvector and cellorigin
"""

__all__ = ['namd_conf_mod']

from fileinput import FileInput

def namd_conf_mod(inputdir, newNamd, anchor):
    vector, origin = namd_conf_read(inputdir, anchor)
    with FileInput(files=newNamd, inplace=True) as f:
        for line in f:
            line = line.strip()
            info = line.split()
            if "cellbasisvector1" in line:
                info[1] = vector[0]
            if "cellbasisvector2" in line:
                info[2] = vector[1]
            if "cellbasisvector3" in line:
                info[3] = vector[2]
            if "cellorigin" in line:
                info[1:4] = origin
            line = " ".join(str(x) for x in info)
            print(line)
                
                
def namd_conf_read(inputdir,anchor):
    pdb = inputdir + '/pdb/' + str(anchor) + '.pdb'
#    pdb = inputdir + '/1.pdb'
    with open(pdb, 'r') as f:
        for line in f:
            info = line.split()
            if "CRYST1" in info:
#                print(info)
                vector = [float(info[1]), float(info[2]), float(info[3])]
#                print(vector)
                origin = [x / 2.0 for x in vector]
#                print(origin)
                break
    return vector, origin


if __name__ == '__main__':
    namd_conf_read('.',1)