# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 22:18:01 2024

@author: Kwihoon
"""

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
from rainfall_distribution import idf, huff, splitRainDist, rainfall_duration, design_rainfall 
from unit_hydrograph import nrcs3
from eff_rainfall import nrcs_cn, reposition, interval_to_hr
from matplotlib import pyplot as plt
import pandas as pd
from drainage import drainage_flow, vol_to_level
import itertools
from hydrograph import synthesize, detention_idf

# =============================================================================
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
# =============================================================================
def design_rainfall (var, duration):
    idf_coef = pd.read_table('input/IDF_coef.txt')
    coef = idf_coef[var]
    x = math.log(duration)
    sum1 = coef[0] + coef[1]*x + coef[2]*math.pow(x,2)+ coef[3]*math.pow(x,3)\
        + coef[4]*math.pow(x,4)+ coef[5]*math.pow(x,5)+ coef[6]*math.pow(x,6)

    des_rain = math.exp(sum1) * duration
    return des_rain

'0. parameter decide'
var = 'a'
r = 0.875
quant = 4
pump = 40
freq = 20

final_result1 = []
final_result2 = []
duration = 48

for i in range(48):
    duration = i + 1
    
    '1. variable'
    '==================================================================================='
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
    '==================================================================================='

    '2. Hyetograph'
    '==================================================================================='
    '2.1. Design rainfall'
    design_rain = design_rainfall (var, duration)
    
    '2.2. Unit hydrograph'
    unit_time, unit_hydro = nrcs3(area, tc)
    interval = unit_time[1] - unit_time[0]
    
    '2.3. Time distribution'
# =============================================================================
#     rainfall_list = huff(duration, interval, var, quant)
# =============================================================================
    rainfall_list = idf(duration,  interval, var, r)

    '2.4. Effective rainfall'
    rainfall_eff = nrcs_cn(rainfall_list, cn)
    '==================================================================================='

    '3. Hydrograph derive'
    hydrograph_time, hydrograph_final = synthesize(rainfall_eff, unit_hydro)
    
# =============================================================================
#     peak = max(hydrograph_final)
#     results = (duration, peak)
#     final_result.append(results)
# =============================================================================
    runoff_volume = (hydrograph_final*interval*3600)    
    runoff_volume_cum = list(itertools.accumulate(hydrograph_final*interval*3600))

    '4. inundation'
    
    'case 1: sil_elev가 외수위'
    inun_results1 = []
    inun_results2 = []
    storage = 0
    level = vol_to_level(storage, elevation_volume)
    
    for j in range(pump):
        pump_drainage = j
        
        results = []

        for k, time in enumerate(hydrograph_time):
            outflow1 = 0
            outflow2 = 0
        
            inflow = runoff_volume[k]
            outflow1 = drainage_flow(level, sill_elev1, sill_elev1, width1, height1) * interval * 3600
    
            if level > sill_elev1:
                outflow2 = pump_drainage * interval * 3600
                outflow2 = min(outflow2, storage)
            
            storage = max(0, storage + inflow - outflow1 - outflow2)
            level = vol_to_level(storage, elevation_volume)    
    
            result = (storage, level, sill_elev1, outflow1, outflow2, inflow)
            results.append(result)
        
        results = np.array(results)
        x1 = max(results.T[0]) # 최대 저류량
        x2 = max(results.T[1]) # 최대 침수위
        x3 = sum(results.T[3]) # 총 자연배제량
        x4 = sum(results.T[4]) # 총 기계배수량
        x5 = sum(results.T[5]) # 총 유입량1
        
        inun_results1.append(round(x1,0))
        inun_results2.append(round(x5,0))

    
# =============================================================================
#     final_result.append(max(hydrograph_final))
# =============================================================================
    final_result1.append(inun_results1)
    final_result2.append(inun_results2)

    
# =============================================================================
#     'case 2: 30년 빈도 관측수위가 외수위'
#     metadata = pd.read_table('input/water_level_outside.txt', sep = '	', thousands = ',')
#     inun_time = np.array(metadata['시간'])
#     level_outside = np.array(metadata['관측수위'])
# 
#     levels = outside_level(hydrograph_time, inun_time, level_outside)
# 
# 
#     results = []
#     storage = 0
#     level = vol_to_level(storage, elevation_volume)
# 
#     for i, time in enumerate(hydrograph_time):
#         outflow1 = 0
#         outflow2 = 0
#         
#         inflow = runoff_volume[i]
#         outside = levels[i]
#         outflow1 = drainage_flow(level, outside, sill_elev1, width1, height1) * interval * 3600
#     
#         if level > 1.8:
#             outflow2 = pump_drainage * interval * 3600
#             outflow2 = min(outflow2, storage)
#             
#         storage = max(0, storage + inflow - outflow1 - outflow2)
#         level = vol_to_level(storage, elevation_volume)    
#     
#         result = (storage, level, outside, outflow1, outflow2, inflow)
#         results.append(result)
#         
#     results = np.array(results)
#     tmp = (i, max(results.T[0]), max(results.T[1]), sum(results.T[3]), sum(results.T[4]), sum(results.T[5]), max(results.T[5]))
#     final_result.append(tmp)
# =============================================================================

# =============================================================================
# plt.plot(hydrograph_time, np.array(results).T[1])
# plt.plot(inun_time, level_outside)
# =============================================================================
    
























