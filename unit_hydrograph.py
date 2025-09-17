# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 22:41:16 2022

@author: Kwihoon
"""

import numpy as np
import pandas as pd

def nrcs3(AREA,Tc):
    unithydropraph = pd.read_table('input/scs_unit_hydro_UnitHydropraph.txt', sep = '	', thousands = ',')
    unit_time_slope = list(unithydropraph['time'])
    unit_hydro_slope3 = list(unithydropraph['hydro3'])
    
# =============================================================================
#     # 유등2 1-1 참고
#     unit_hydro_slope3 = [0, 0.065, 0.262, 0.598, 0.941, 1.000, 0.982, 0.810, 0.553, 0.392, 0.281, 0.208, 0.146, 0.107, 0.077, 0.055,\
#                       0.040, 0.029, 0.021, 0.015, 0.011, 0.009, 0.006, 0.004, 0.002, 0]  
# =============================================================================
    
    unit_time = np.array(unit_time_slope)
    unit_hydro = np.array(unit_hydro_slope3)    
    A1 = AREA
    tc1 = Tc # hr
    tr1 = round(0.133*tc1,3)
    tp1 = 0.6*tc1
    Tp1 = 0.5*tr1+tp1
    Q = 1 
    Qp1 = round(Q*2.08*A1/100/Tp1/10,2)
    Qp1 = 2.32 # 유등2 1-1 참고
    interval = round(Tp1*0.2,3)

    time = np.round(unit_time*Tp1,3)
    hydro = np.round(unit_hydro*Qp1,2)
    return time, hydro    

'''
[Input data] 
AREA: 1033.5 / 유역면적 (ha)
Tc: 1.39 / time of concentration (hr)

[Output data] 
time    hydro
0	    0
0.185	0.15
0.371	0.61
0.556	1.39
0.741	2.18
0.926	2.32
1.112	2.28
1.297	1.88
1.482	1.28
1.668	0.91
1.853	0.65
2.038	0.48
2.224	0.34
2.409	0.25
2.594	0.18
2.78	0.13
2.965	0.09
3.15	0.07
3.335	0.05
3.521	0.03
3.706	0.03
3.891	0.02
4.077	0.01
4.262	0.01
4.447	0
4.632	0
'''
