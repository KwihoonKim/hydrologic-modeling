# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 2022
revised on Wed Nov 22 2023
revised on Fri Sep 27 2024
주요내용
1. 
@author: Kwihoon
"""
import math
import numpy as np
from rainfall_distribution import idf, idf_rms, huff, splitRainDist, rainfall_duration
from unit_hydrograph import nrcs3
from eff_rainfall import nrcs_cn, reposition, interval_to_hr
from matplotlib import pyplot as plt
import pandas as pd
from drainage import drainage_flow, vol_to_level
import itertools
from hydrograph import synthesize, detention_idf

'0. parameter decide'
var = 'b'
duration = 48
r = 0

hydrograph_time, hydrograph_final, runoff_volume = detention_idf (48, var, r)


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


'idf'
r = 1
rainfall_list = idf(duration, rain_dur,  interval, r)

'huff'
rainfall_list = huff(duration, design_rainfall, interval, 4)

'2. Hydrograph derive'
rainfall_eff = nrcs_cn(rainfall_list, cn)
hydrograph_time, hydrograph_final = synthesize(rainfall_eff, unit_hydro)

runoff_volume = list(itertools.accumulate(hydrograph_final*interval*3600))
runoff_volume = (hydrograph_final*interval*3600)

plt.plot(hydrograph_time, hydrograph_final)

'3. flood level estimation'
level = vol_to_level(0, elevation_volume)

'4. drainage calculation'
# =============================================================================
# gate_drainage = drainage_flow(level, sill_elev1, width1, height1)
# =============================================================================
pump_drainage = 20

'5. water balance'
'case 1: sill_elev가 외수위'

results = []
storage = 0
level = vol_to_level(storage, elevation_volume)

for i, time in enumerate(hydrograph_time):
    outflow1 = 0
    outflow2 = 0
    
    inflow = runoff_volume[i]
    outflow1 = drainage_flow(level, sill_elev1, sill_elev1, width1, height1) * interval * 3600
    
    if level > 4.2:
        outflow2 = pump_drainage * interval * 3600
            
    storage = storage + inflow - outflow1 - outflow2
    level = vol_to_level(storage, elevation_volume)    
    
    result = (storage, level)
    results.append(result)
    
plt.plot(hydrograph_time, np.array(results).T[1])

    
# =============================================================================
# 'case 2: 30년 빈도 관측수위가 외수위'
# metadata = pd.read_table('input/water_level_outside.txt', sep = '	', thousands = ',')
# inun_time = np.array(metadata['시간'])
# level_outside = np.array(metadata['관측수위'])
# 
# def outside_level(hydrograph_time, inun_time, level_outside):
#     
#     levels = []
#     pre_time = 0
#     level = level_outside[0]
#     
#     for i in hydrograph_time:
#         if i == 0:
#             pass
#         
#         for j, time in enumerate(inun_time):
#             if (time - i) * (pre_time - i) < 0:
#                 level = level_outside[j]
#                 
#             pre_time = time
#             
#         levels.append(level)
#         
#     return levels
# 
# 
# levels = outside_level(hydrograph_time, inun_time, level_outside)
# 
# 
# results = []
# storage = 0
# level = vol_to_level(storage, elevation_volume)
# 
# for i, time in enumerate(hydrograph_time):
#     outflow1 = 0
#     outflow2 = 0
#     
#     inflow = runoff_volume[i]
#     outside = levels[i]
#     outflow1 = drainage_flow(level, outside, sill_elev1, width1, height1) * interval * 3600
#     
#     if level > 1.8:
#         outflow2 = pump_drainage * interval * 3600
#         outflow2 = min(outflow2, storage)
#             
#     storage = storage + inflow - outflow1 - outflow2
#     level = vol_to_level(storage, elevation_volume)    
#     
#     result = (storage, level, outflow1, outflow2, inflow)
#     results.append(result)
#     
# plt.plot(hydrograph_time, np.array(results).T[1])
# plt.plot(inun_time, level_outside)
# =============================================================================
















