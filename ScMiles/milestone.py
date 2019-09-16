#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 10:42:22 2018

@author: Wei Wei

This subroutine stores all of the hitting events, and generates the kernel.

"""


class milestone:

#    __slots__ = ('anchors', 'reactants', 'products', '_counter')

    def __init__(self, anchors=None, known=None, new=None, ms_index=None,
                 k_count=None, kernel=None, t_hash=None, life_time=None) -> None:
        
        import numpy as np
        
        self.anchors = []
        
        self.known = known if known else set()
        
        self.new = new if new else set()
      
        self.ms_index = {} 
            
        self.kernel = kernel if kernel else []
        
        self.life_time = life_time if life_time else []
        
        self.k_count = [] #np.array([[]]).astype(int)
        
        self.t_hash = {}

    def __repr__(self) -> str:
        return ('Started from {} milestones. {} new milestone(s) '
                .format(len(self.known), len(self.new)))

    def read_anchors(self, path: str) -> None:
        import pandas as pd
        arr = pd.read_fwf(path, header=None).values
        self.anchors = arr
    
    def get_anchor(self, anchor1: int):
        return self.anchors[anchor1, :]

    def add_ms(self, anchor1: int, anchor2: int, orig_dest: str) -> None:
        lst = sorted([anchor1, anchor2])
        name = str(lst[0]) + '_' + str(lst[1])
        if orig_dest == 'orig':
            if name not in self.known and name not in self.new:
                self.expand()
                self.add_known_ms(lst[0], lst[1]) 
            elif name not in self.known:
                self.new_to_known(lst[0], lst[1])
        elif orig_dest == 'dest':       
            if name not in self.known and name not in self.new:
                self.expand()
                self.add_new_ms(lst[0], lst[1]) 

    def add_known_ms(self, anchor1: int, anchor2: int) -> None:
        lst = sorted([anchor1, anchor2])
        name = str(lst[0]) + '_' + str(lst[1])
        self.known.add(name)
        if name not in self.t_hash.keys():
            self.ms_index[len(self.ms_index)] =  lst
            self.t_hash[name] = None
        
    def add_new_ms(self, anchor1: int, anchor2: int) -> None:
        lst = sorted([anchor1, anchor2])
        name = str(lst[0]) + '_' + str(lst[1])
        self.new.add(name)
        if name not in self.t_hash.keys():
            self.ms_index[len(self.ms_index)] =  lst
            self.t_hash[name] = None
    
    def new_to_known(self, anchor1: int, anchor2: int) -> None:
        lst = sorted([anchor1, anchor2])
        name = str(lst[0]) + '_' + str(lst[1])
        if name not in self.new:
            return
        else:
            self.known.add(name)
            self.new.remove(name)
    
    def get_index(self, anchor1: int, anchor2: int) -> int:
        lst = sorted([anchor1, anchor2])
        return [k for k,v in self.ms_index.items() if v == lst][0]
    
    def expand(self):
        import numpy as np
        dim = len(self.k_count)
        if dim == 0:
            self.k_count = np.array([[0]], dtype=int)
        else:
            self.k_count = np.append(self.k_count, np.zeros((dim,1), dtype=int), 1)
            self.k_count = np.append(self.k_count, np.zeros((1,dim+1), dtype=int), 0)
    
        
if __name__ == '__main__':
    ms = milestones()
    ms.read_anchors('./anchors.txt')
    ms.add_new_ms(1,2)
    print(ms.known)
    print(ms.new)
    ms.new_to_known(2,1)
    print(ms.known)
    print(ms.new)
    print(ms.get_anchor(2))
    print(ms.ms_index)
    print(ms.get_index(2,1))