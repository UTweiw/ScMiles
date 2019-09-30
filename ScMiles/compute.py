#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 10:37:37 2018

@author: Wei Wei


This subroutine takes the k and t, and calculate flux, probability,
free energy, committor, and MFPT.
"""

import os
import pandas as pd
import numpy as np
from network_check import pathway
#yfrom voronoi_plot import voronoi_plot

__all__ = ['k_average','compute']

def find_ms_index(ms,ms_index):
    ms = sorted(ms)
    return(int(list(ms_index.keys())[list(ms_index.values()).index(ms)]))


def get_ms_of_cell(cell, ms_index):
    ms_of_cell = []
    for item in ms_index.values():
        if int(cell) in item:
            ms_of_cell.append(int(list(ms_index.keys())[list(ms_index.values()).index(item)]))
    return ms_of_cell


def k_average(k_count):
    dim = len(k_count)
    k_ave = np.zeros((dim, dim))
    for i in range(dim):
        for j in range(dim):
            if i != j:
                if np.sum(k_count[i, :]) != 0.0:
                    k_ave[i, j] = k_count[i, j] / np.sum(k_count[i, :]) 
    return k_ave


def k_error(k_count):
    dim = len(k_count)
    k = np.zeros((dim, dim))
    for i in range(dim):
        total = np.sum(k_count[i]) 
        for j in range(dim):
            a = k_count[i,j]
            if i == j or a == 0:
                continue
            if total == a:
                k[i, j] = 1.0
#            print(total,a)
            b = total - a
            if b > 0: 
                k[i, j] = np.random.beta(a, b)
        if sum(k[i, :]) != 0:
            k[i, :] = k[i, :] / sum(k[i, :])
#    for i in range(len(k)):
#        print(i, k[i])
    return k

 
def t_error(t, t_std):
#    print(np.abs(np.random.normal(t, t_std, len(t))).tolist())
    return np.abs(np.random.normal(t, t_std, len(t))).tolist()


def committor(parameter, k):
    kk = k.copy()
    for i in parameter.reactant_milestone:
        kk[i] = [0 for j in k[i]]
    for i in parameter.product_milestone:
        kk[i] = [0 for j in k[i]]
        kk[i][i] = 1.0
#    print(kk)
    c = np.linalg.matrix_power(kk,1000000000)
    A = np.ones((len(c),1))
#    print(A)
#    print(np.matmul(c,A))
    return np.matmul(c,A)


def flux(k):
    kk = k.copy()
    kk_trans = np.transpose(kk)
    e_v, e_f = np.linalg.eig(kk_trans)
#    print(e_v)
#    print(e_f[:,0])
    idx = np.abs(e_v - 1).argmin()  
    q = [i.real for i in e_f[:, idx]]
    q = np.array(q)
    if np.all(q < 0):
        q = -1 * q
        
#    print(idx, q)
    return q


def prob(q,t):
    p = np.transpose(q) * np.squeeze(t)
    p_norm = p / np.sum(p)
#    print(p_norm)
    return p_norm


def free_energy(p):
    return -1.0 * np.log(p)
    

def get_boundary(parameter, ms_index):
    if len(parameter.reactant) == 2:
        bc1 = sorted(parameter.reactant)
        if bc1 in ms_index.values():
            parameter.reactant_milestone.append(int(list(ms_index.keys())[list(ms_index.values()).index(bc1)]))
        else:
            parameter.reactant_milestone.append(-1)
    else:
        for item in ms_index.values():
            if int(parameter.reactant[0]) in item and int(list(ms_index.keys())[list(ms_index.values()).index(item)]) not in parameter.reactant_milestone:
                parameter.reactant_milestone.append(int(list(ms_index.keys())[list(ms_index.values()).index(item)]))
            
    if len(parameter.product) == 2:
        bc2 = sorted(parameter.product)
        if bc2 in ms_index.values():   
            parameter.product_milestone.append(int(list(ms_index.keys())[list(ms_index.values()).index(bc2)]))
        else:
            parameter.product_milestone.append(-1)
    else:
        for item in ms_index.values():
#            print(item)
            if int(parameter.product[0]) in item and int(list(ms_index.keys())[list(ms_index.values()).index(item)]) not in parameter.product_milestone:
                parameter.product_milestone.append(int(list(ms_index.keys())[list(ms_index.values()).index(item)]))            


def MFPT(parameter, kk, t):
    k = kk.copy()
    for i in parameter.product_milestone:
        k[i] = [0 for j in k[i]]
        for j in parameter.reactant_milestone:
            k[i][j] = 1.0 / len(parameter.reactant_milestone)   
    q = flux(k)
    qf = 0
    for i in parameter.product_milestone:
        qf += q[i]
    tau = np.dot(q, t) / qf
    return float(tau)
    

def MFPT2(parameter, k, t):
    dim = len(k)
    I = np.identity(dim)
    k2 = k.copy()
    for i in parameter.product_milestone:
        if i == -1:
            return -1
        k2[i] = [0 for i in k2[i]]
    
    p0 = np.zeros(dim)
    for i in parameter.reactant_milestone:
        if i == -1:
            return -1
        p0[i] = 1 / (len(parameter.reactant_milestone))
        
    if np.linalg.det(np.mat(I) - np.mat(k2)) == 0.0:
        parameter.sing = True
        return -1
    else:
        parameter.sing = False
        tau = p0 * np.linalg.inv(I - np.mat(k2)) * np.transpose(np.mat(t))
#    print(np.linalg.inv(I - np.mat(k2)) * np.transpose(np.mat(t)))
    return float(tau)


def compute(parameter):
    filePath = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(filePath, os.pardir)) + '/my_project_output'
    path = path + '/current'
    filepath_t = path + '/life_time.txt'
    t_raw = pd.read_fwf(filepath_t, header=1).values
#    t = (t_raw[0, :]/parameter.timeFactor).tolist()
#    t_std = (t_raw[1, :]/parameter.timeFactor).tolist()
#    print(t_raw)
    t = (t_raw[0, :]).tolist()
    t_std = (t_raw[1, :]).tolist()
    dimension = len(t_raw[0])

    kc_raw = pd.read_fwf(path + '/k.txt', header=1).values
    kc = [[float(j) for j in i] for i in kc_raw[0:dimension,0:dimension].tolist()]
    k = k_average(np.array(kc))
######################
    ms_list = np.load(path + '/ms_index.npy').item()
    
    kk = k.copy()
    tt = t.copy()
    parameter.reactant_milestone = []
    parameter.product_milestone = []
    get_boundary(parameter, ms_list)
    
    kk = k_average(np.array(kk))
    
    kk_cyc = k.copy()
    for i in parameter.product_milestone:
        kk_cyc[i] = [0 for j in k[i]]
        for j in parameter.reactant_milestone:
            kk_cyc[i][j] = 1.0 / len(parameter.reactant_milestone)   
    q_cyc = flux(kk_cyc)
    
    q = flux(kk)
#    parameter.flux = q.copy()
    p = prob(q,tt)
    energy = free_energy(p)
    tau1 = MFPT(parameter, kk, tt)
    tau2 = MFPT2(parameter, kk, tt)

    energy_samples = []
    MFPT_samples = []
    MFPT2_samples = []
    energy_err = []
    MFPT_err = []
    MFPT_err2 = []
    
    for i in range(parameter.err_sampling):
        k_err = k_error(np.mat(kc))
        if not isinstance(t_std,float):
            t_std = tt
        t_err = t_error(tt, t_std)
        q_temp = flux(k_err)
        p_temp = prob(q_temp,tt)
        energy_samples.append(free_energy(p_temp))
        MFPT_er = MFPT(parameter, k_err, t_err)
        MFPT_samples.append(MFPT_er)
        MFPT_er2 = MFPT2(parameter, k_err, t_err)
        MFPT2_samples.append(MFPT_er2)
        
    for i in range(dimension):        
        energy_err.append(np.std(np.array(energy_samples)[:,i], ddof=1))
    MFPT_err = float(np.std(MFPT_samples, ddof=1))
    MFPT_err2 = float(np.std(MFPT2_samples, ddof=1))
        
    with open(path + '/results.txt', 'w+') as f1:
        print('{:>4} {:>4} {:>10} {:>8} {:>10} {:>10}'.format('a1','a2','q','p','freeE','freeE_err'),file=f1)
        keyIndex = 0
        for i in range(len(q)):
            while True:
                if keyIndex not in ms_list:
                    keyIndex += 1
                else:
                    break
            print('{:4d} {:4d} {:10.5f} {:8.5f} {:10.5f} {:10.5f}'.format(ms_list[keyIndex][0], ms_list[keyIndex][1], 
                  q_cyc[i], p[i], energy[i], energy_err[i]), file=f1)
            keyIndex += 1  
        print('\n\n',file=f1)
        print("MFPT is {:15.8e}, with an error of {:15.8e}, from eigenvalue method.".format(tau1, MFPT_err),file=f1)  
        print("MFPT is {:15.8e}, with an error of {:15.8e}, from inverse method.".format(tau2, MFPT_err2),file=f1) 
        
    c = committor(parameter, kk)
    m = []
    for ms in ms_list.values():
        m.append(ms)
    with open(path + '/committor.txt', 'w+') as f1:
        print('\n'.join([''.join(['{:>15}'.format(str(item)) for item in m])]),file=f1)
        print('\n'.join([''.join(['{:15.8f}'.format(item) for item in np.squeeze(c)])]),file=f1)
       
    if parameter.sing == False:
        parameter.MFPT = tau1
    else:
        parameter.MFPT = 0
        
#    voronoi_plot(parameter, m, c, energy, ms_list)
    index = []
    for i in range(len(ms_list)):
        index.append(ms_list[i])

    return k, index, q_cyc

if __name__ == '__main__':
    from parameters import *
    new = parameters()
    new.initialize()
    new.iteration = 1
    from milestones import milestones
    compute(new)
    print('{:e}'.format(new.MFPT))
