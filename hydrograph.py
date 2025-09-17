# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 20:06:30 2025

@author: Kwihoon
"""

import math
import numpy as np
from rainfall_distribution import idf, huff, splitRainDist, rainfall_duration
from unit_hydrograph import nrcs3
from eff_rainfall import nrcs_cn, reposition, interval_to_hr
from matplotlib import pyplot as plt
import pandas as pd
from drainage import drainage_flow, vol_to_level
import itertools

def synthesize(hyetograph, unit_hydro):    
    hydrograph_final = []
    unit_time = hyetograph[1][0]
    
    duration = hyetograph.T[0][-1]
    num = int((72 - duration) / unit_time)

    hyetograph = hyetograph.T[1]
    
    for i in range(num):
        hyetograph = np.append(hyetograph, 0)
    
    for i, rain in enumerate(hyetograph):
        hydro = 0
        if i < len(unit_hydro):
            cum_hydro = 0
            for j in range(i):
                hydro += unit_hydro[j] * hyetograph[i-j]                                 
        elif i >= len(unit_hydro):
            for k, unit in enumerate(unit_hydro):
                hydro += unit * hyetograph[i-k]     
            
        hydrograph_final.append(hydro)
    hydrograph_final = np.array(hydrograph_final)
    
    hydrograph_time = []
    for i in range(len(hydrograph_final)):
        hydrograph_time.append(round(i*unit_time,3))
        
    hydrograph_time = np.array(hydrograph_time)
    return hydrograph_time, hydrograph_final

'''
Example (창원)

# Input 자료
* rainfall
    구간강우량  누적시간
    (mm)    (hr)
    0	    0
    0	    0.185
    1.21	0.37
    4.23	0.555
    9.91	0.74
    24.05	0.925
    9.95	1.11
    6.98	1.295
    5.42	1.48
    4.48	1.665
    4.38	1.85
    4.23	2.035
    3.52	2.22
    3.52	2.405
    3.53	2.59
        .
        .
        .
        .
    0.39	44.77
    0.39	44.955
    0.38	45.14
    0.39	45.325
    0.38	45.51
    0.39	45.695
    0.39	45.88
    0.38	46.065
    0.39	46.25
    0.38	46.435
    0.39	46.62
    0.38	46.805
    0.39	46.99
    0.39	47.175
    0.38	47.36
    0.39	47.545
    0.38	47.73
    0.39	47.915
    
* unit_hydro
    0
    0.15
    0.61
    1.39
    2.18
    2.32
    2.28
    1.88
    1.28
    0.91
    0.65
    0.48
    0.34
    0.25
    0.18
    0.13
    0.09
    0.07
    0.05
    0.03
    0.03
    0.02
    0.01
    0.01
    0
    0

# Output 자료
* hydrograph_final

    Q (CMS)
    0
    0
    0
    0.1815
    1.3726
    5.7487
    18.1701
    41.9665
    74.7222
    106.241
    123.263
    129.204
    122.763
    109.29
    97.4817
    87.4754
    79.4187
    72.8702
        .
        .
        .
        .
    3.3546
    2.4757
    1.7493
    1.2552
    0.9035
    0.6527
    0.4672
    0.336
    0.2394
    0.1699
    0.1198
    0.0849
    0.058
    0.0386
    0.027
    0.0155
    0.0077
    0.0039
    0
    0
    0
'''

def detention_idf (dur, site, r):
    duration = dur
    var = site
    
    'default values'
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    name, cn, area, tc, site, width1, height1, sill_elev1, width2, height2, sill_elev2,\
    elevation, channel_baseline = target_site

    if var == 'a':
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
    elif var == 'b':
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
    elif var == 'c':
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
    elif var == 'd':
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')

    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)

    duration = int(duration)
    cn = float(cn)
    area = float(area)
    tc = float(tc)
    site = int(site)
    width1 = float(width1)
    width2 = float(width2)
    height1 = float(height1)
    height2 = float(height2)
    sill_elev1 = float(sill_elev1)


    '1. rainfall time distribution'
    rain_dur = rainfall_duration(name)
    rainfalls = list(rain_dur[0])
    durations = list(rain_dur[1])
    index = rainfalls.index(duration)
    design_rainfall = durations[index]

    unit_time, unit_hydro = nrcs3(area, tc)
    interval = unit_time[1] - unit_time[0]
    
    rainfall_list = idf(duration, rain_dur,  interval, r)
    
    '2. Hydrograph derive'
    rainfall_eff = nrcs_cn(rainfall_list, cn)
    hydrograph_time, hydrograph_final = synthesize(rainfall_eff, unit_hydro)
    runoff_volume = list(itertools.accumulate(hydrograph_final*interval*3600))
    runoff_volume = (hydrograph_final*interval*3600)
    
    plt.plot(hydrograph_time, hydrograph_final)
    
    results = (hydrograph_time, hydrograph_final, runoff_volume)
    return results
    

def detention_idf (dur, site, q):
    duration = dur
    var = site
    
    'default values'
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    name, cn, area, tc, site, width1, height1, sill_elev1, width2, height2, sill_elev2,\
    elevation, channel_baseline = target_site

    if var == 'a':
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
    elif var == 'b':
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
    elif var == 'c':
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
    elif var == 'd':
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')

    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)

    duration = int(duration)
    cn = float(cn)
    area = float(area)
    tc = float(tc)
    site = int(site)
    width1 = float(width1)
    width2 = float(width2)
    height1 = float(height1)
    height2 = float(height2)
    sill_elev1 = float(sill_elev1)


    '1. rainfall time distribution'
    rain_dur = rainfall_duration(name)
    rainfalls = list(rain_dur[0])
    durations = list(rain_dur[1])
    index = rainfalls.index(duration)
    design_rainfall = durations[index]

    unit_time, unit_hydro = nrcs3(area, tc)
    interval = unit_time[1] - unit_time[0]
    
    rainfall_list = huff(duration, rain_dur,  interval, q)
    
    '2. Hydrograph derive'
    rainfall_eff = nrcs_cn(rainfall_list, cn)
    hydrograph_time, hydrograph_final = synthesize(rainfall_eff, unit_hydro)
    runoff_volume = list(itertools.accumulate(hydrograph_final*interval*3600))
    runoff_volume = (hydrograph_final*interval*3600)
    
    plt.plot(hydrograph_time, hydrograph_final)
    
    results = (hydrograph_time, hydrograph_final, runoff_volume)
    return results    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
