# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 15:13:20 2022

@author: Kwihoon
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import math
from drainage import drainage_flow

def flooding(hydrograph_final, hydrograph_time, pump, site, level_flood):
    interval = hydrograph_time[1] - hydrograph_time[0]
    final_result = []
    
    if site == 1:
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
        print(site)
        
    elif site == 2:
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
        print(site)
    
    elif site == 3:
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
        print(site)
    
    elif site == 4:
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')
        print(site)
    
    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)
    hydro_vol = 3600 * interval * hydrograph_final

    cum = 0
    hydro_cum = []
    for i in hydro_vol:
        cum += i
        hydro_cum.append(cum)

    pump_max = pump # CMS
    pump_max_vol = pump_max * 3600 * interval
    
    level0 = 194.2

    xx = np.stack((hydro_vol, hydro_cum), axis = 1)
    
    volume = 0
    pump_test = []
    hydro_with_pump = []
    for hydro, cum in xx:
        
        if volume + hydro <= level0:
            pump = 0
            pump_test.append(pump)    
            volume = level0
        
        elif volume + hydro <= pump_max_vol + level0 and volume + hydro > level0:
            pump = (volume + hydro - level0) / 3600 / interval
            pump_test.append(pump)
            volume = level0
        
        elif volume + hydro > pump_max_vol + level0:
            pump = pump_max_vol / 3600 / interval
            pump_test.append(pump)    
            volume = volume + hydro - pump_max_vol

        hydro_with_pump.append(volume)

    inundation_list = []
    for hydro in hydro_with_pump:
        pre_height = 0
        pre_volume = 0
    
        for height, volume in elevation_volume:
            if (hydro - volume) * (hydro - pre_volume) <= 0:
                inundation_height = height
            pre_height = height
            pre_volume = volume
        
        inundation_list.append(inundation_height)

    inun_limit = []

    for i in range(len(hydrograph_final)):
        inun_limit.append(level_flood)
    
    
    elev, volume = elevation_volume.T
    min_elev = int(min(elev))    
    max_elev = int(max(elev)) + 1

    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_xlabel('hour')
    ax1.set_ylabel('Level (m)')
    ax1.plot(hydrograph_time, inundation_list, '.', color='red')
    ax1.plot(hydrograph_time, inun_limit, color='black')
    ax1.set_ylim(min_elev, max_elev)

    ax2 = ax1.twinx()
    ax2.set_ylabel('CMS')
    ax2.bar(hydrograph_time, pump_test, color = 'None', edgecolor = 'green', linewidth = 0.5) #color='blue', fill = False, edgecolor = 'black'
    ax2.set_ylim(0,400)

    plt.show()   
    final_result = np.stack((hydrograph_time, hydrograph_final, inundation_list, inun_limit, pump_test, hydro_with_pump), axis = 1)
    return final_result

'''
Example (창원)

# Input 자료
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
* hydrograph_time
    누적시간
    (hr)
    0
    0.185
    0.37
    0.555
    0.74
    0.925
    .
    .
    .
    .
    47.36
    47.545
    47.73
    47.915
    
* intervalTime: 0.185 (hr)
* pump: 40 CMS

# Output 자료
* final_result
time(hr) Q(CMS) depth(m) pump (CMS) inundation volume (m3)
0	    0	    2.6	5	0	        194.2
0.185	0	    2.6	5	0	        194.2
0.37	0	    2.6	5	0	        194.2
0.555	0.1815	2.6	5	0.1815	    194.2
0.74	1.3726	2.6	5	1.3726	    194.2
0.925	5.7487	2.6	5	5.7487	    194.2
1.11	18.1701	2.6	5	18.1701	    194.2
1.295	41.9665	2.7	5	40	        1503.89
1.48	74.7222	3.3	5	40	        24628.9
1.665	106.241	3.8	5	40	        68745.2
1.85	123.263	4.2	5	40	        124199
2.035	129.204	4.5	5	40	        183609
2.22	122.763	4.8	5	40	        238729
2.405	109.29	4.9	5	40	        284876
2.59	97.4817	5.1	5	40	        323159
                .
                .
                .
                .
47.545	5.9146	2.6	5	5.9146	194.2
47.73	5.919	2.6	5	5.919	194.2
47.915	5.9204	2.6	5	5.9204	194.2
'''
def flooding_weir (hydrograph_final, hydrograph_time, pump, site):
    
    final_result = []
    site = int(site)
    if site == 1:
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
        var = 'a'
        print(site)
        
    elif site == 2:
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
        var = 'b'
        print(site)
    
    elif site == 3:
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
        var = 'c'
        print(site)
    
    elif site == 4:
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')
        var = 'd'
        print(site)
        
    interval = hydrograph_time[1] - hydrograph_time[0]
    
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    _, _, _, _, _, _, level_flood, width1, width2, height1, height2, _, _ = target_site
    
    level_flood = float(level_flood)
    gate_width1 = float(width1)
    gate_width2 = float(width2)
    gate_height1 = float(height1)
    gate_height2 = float(height2)
    
    k_coef = 0.58
    pump_max = pump # CMS
    
    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)
    
    pump_list = []    
    drainage_list = []
    volume_list = []
    height_inundation_list = []

    volume = 0
    for hydro in hydrograph_final:
        # height_inundation 값 결정 (volume이 특정 survey 구간 사이에 위치할때 더 아랫값을 적용)
        # * 펌프 개시하는 조건을 초기값으로 결정해야함 (일단 level_flood + 0.3으로 결정)
        # * 외수위 값을 결정해야하는데 level_flood로 할 경우 그 밑으로 안떨어지는 문제가 발생
        # * 외수위 값은 elevation_volume 자료의 최저수위 값으로 하였음
        
        # 1. volume으로 height_inundation 결정
        # 2. height_inundation으로 drainage, pump 결정
        # 3. volume에서 유입량 더하고, drainage, pump 빼준 후 △t 후의 volume 결정 
        
        level_out = elevation_volume.T[0][0]
        volume_survey_prev = elevation_volume[0][1]
        height_survey_prev = elevation_volume[0][0]
        
        for height_survey, volume_survey in elevation_volume:
            
            kim = int((volume - volume_survey) * (volume - volume_survey_prev))
            
            if  kim <= 0:
                height_inundation = height_survey_prev
                height_diff = height_inundation - level_out
                break
            
            volume_survey_prev = volume_survey
            height_survey_prev = height_survey
            
     
        volume_rate = volume / 3600 / interval
        volume_after = hydro + volume_rate
        
        height_diff1 = min(height_diff, gate_height1)
        height_diff2 = min(height_diff, gate_height2)
        drainage1 = k_coef * gate_width1 * math.pow(height_diff1, 1.5)
        drainage2 = k_coef * gate_width2 * math.pow(height_diff2, 1.5)
        drainage = min(volume_after, drainage1 + drainage2)
        drainage_list.append(drainage)            
            
            
        
        volume_after = volume_after - drainage
        pump = min (volume_after, pump_max)
        volume_after = volume_after - pump
        volume = volume_after * 3600 * interval
        
        pump_list.append(pump)
        height_inundation_list.append(height_inundation)
        volume_list.append(volume)
        
    inun_limit = []
    hydrograph_time = []
    for i in range(len(hydrograph_final)):
        inun_limit.append(level_flood)
        hydrograph_time.append(round(interval * i,3))
    
    elev, volume = elevation_volume.T
    min_elev = int(min(elev))    
    max_elev = int(max(elev)) + 1

    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_xlabel('hour')
    ax1.set_ylabel('Level (m)')
    ax1.plot(hydrograph_time, height_inundation_list, '.', color='red')
    ax1.plot(hydrograph_time, inun_limit, color='black')
    ax1.set_ylim(min_elev, max_elev)

    ax2 = ax1.twinx()
    ax2.set_ylabel('CMS')
    ax2.bar(hydrograph_time, pump_list, color = 'None', edgecolor = 'green', linewidth = 0.5) #color='blue', fill = False, edgecolor = 'black'
    ax2.set_ylim(0,400)
    plt.show()  
    
    final_result = np.stack((hydrograph_time, hydrograph_final, height_inundation_list, inun_limit, volume_list, drainage_list, pump_list), axis = 1)
    return final_result

def flooding_drainage (hydrograph_final, hydrograph_time, pump, site):
    
    final_result = []
    site = int(site)
    if site == 1:
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
        var = 'a'
        print(site)
        
    elif site == 2:
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
        var = 'b'
        print(site)
    
    elif site == 3:
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
        var = 'c'
        print(site)
    
    elif site == 4:
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')
        var = 'd'
        print(site)
        
    interval = hydrograph_time[1] - hydrograph_time[0]
    
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    _, _, _, _, _, _, level_flood, width1, height1, sill_elev1, width2, height2, sill_elev2, width3, height3, sill_elev3, _, channel_baseline = target_site
    level_flood = float(level_flood)
    gate_width_1 = float(width1)
    gate_height_1 = float(height1)
    gate_sill_1 = float(sill_elev1)
    
    gate_width_2 = float(width2)
    gate_height_2 = float(height2)
    gate_sill_2 = float(sill_elev2)

    gate_width_3 = float(width3)
    gate_height_3 = float(height3)
    gate_sill_3 = float(sill_elev3)
    
    channel_baseline = float(channel_baseline)
    
    pump_max = pump # CMS
    
    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)
    
    pump_list = []    
    drainage_list = []
    volume_list = []
    height_inundation_list = []

    volume = 0
    for hydro in hydrograph_final:
        # height_inundation 값 결정 (volume이 특정 survey 구간 사이에 위치할때 더 아랫값을 적용)
        # * 펌프 개시하는 조건을 초기값으로 결정해야함 (일단 level_flood + 0.3으로 결정)
        # * 외수위 값을 결정해야하는데 level_flood로 할 경우 그 밑으로 안떨어지는 문제가 발생
        # * 외수위 값은 elevation_volume 자료의 최저수위 값으로 하였음
        
        # 1. volume으로 height_inundation 결정
        # 2. height_inundation으로 drainage, pump 결정
        # 3. volume에서 유입량 더하고, drainage, pump 빼준 후 △t 후의 volume 결정 
        
        level_out = elevation_volume.T[0][0]
        volume_survey_prev = elevation_volume[0][1]
        height_survey_prev = elevation_volume[0][0]
        
        for height_survey, volume_survey in elevation_volume:
            
            kim = int((volume - volume_survey) * (volume - volume_survey_prev))
            
            if  kim <= 0:
                height_inundation = height_survey_prev
                height_diff = height_inundation - level_out
                break
            
            volume_survey_prev = volume_survey
            height_survey_prev = height_survey
            
     
        volume_rate = volume / 3600 / interval
        volume_after = hydro + volume_rate
        
        gate_drainage_1 = drainage_flow(height_inundation, gate_sill_1, gate_width_1, gate_height_1)
        gate_drainage_2 = drainage_flow(height_inundation, gate_sill_2, gate_width_2, gate_height_2)
        gate_drainage_3 = drainage_flow(height_inundation, gate_sill_3, gate_width_3, gate_height_3)

        gate_drainage = min(volume_after, gate_drainage_1 + gate_drainage_2 + gate_drainage_3)
        drainage_list.append(gate_drainage)            
            
            
        
        volume_after = volume_after - gate_drainage
        pump = min (volume_after, pump_max)
        volume_after = volume_after - pump
        volume = volume_after * 3600 * interval
        
        pump_list.append(pump)
        height_inundation_list.append(height_inundation)
        volume_list.append(volume)
        
    inun_limit = []
    hydrograph_time = []
    for i in range(len(hydrograph_final)):
        inun_limit.append(level_flood)
        hydrograph_time.append(round(interval * i,3))
    
    elev, volume = elevation_volume.T
    min_elev = int(min(elev))    
    max_elev = int(max(elev)) + 1

    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_xlabel('hour')
    ax1.set_ylabel('Level (m)')
    ax1.plot(hydrograph_time, height_inundation_list, '.', color='red')
    ax1.plot(hydrograph_time, inun_limit, color='black')
    ax1.set_ylim(min_elev, max_elev)

    ax2 = ax1.twinx()
    ax2.set_ylabel('CMS')
    ax2.bar(hydrograph_time, pump_list, color = 'None', edgecolor = 'green', linewidth = 0.5) #color='blue', fill = False, edgecolor = 'black'
    ax2.set_ylim(0,400)
    plt.show()  
    
    final_result = np.stack((hydrograph_time, hydrograph_final, height_inundation_list, inun_limit, volume_list, drainage_list, pump_list), axis = 1)
    return final_result


def flooding_weir2 (hydrograph_final, hydrograph_time, pump, site):
    
    final_result = []
    site = int(site)
    if site == 1:
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
        var = 'a'
        print(site)
        
    elif site == 2:
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
        var = 'b'
        print(site)
    
    elif site == 3:
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
        var = 'c'
        print(site)
    
    elif site == 4:
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')
        var = 'd'
        print(site)
        
    interval = hydrograph_time[1] - hydrograph_time[0]
    
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    _, _, _, _, _, _, level_flood, width1, width2, height1, height2 = target_site
    
    level_flood = float(level_flood)
    gate_width1 = float(width1)
    gate_width2 = float(width2)
    gate_height1 = float(height1)
    gate_height2 = float(height2)
    
    k_coef = 1.58
    pump_max = pump # CMS
    
    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)
    hydro_vol = 3600 * interval * hydrograph_final


    cum = 0
    hydro_cum = []
    for i in hydro_vol:
        cum += i
        hydro_cum.append(cum)
    
    hydrograph_default = np.stack((hydro_vol, hydro_cum), axis = 1)
    
    pump_list = []    
    drainage_list = []
    volume_list = []
    height_inundation_list = []

    volume = 0
    for hydro, cum in hydrograph_default:
        # height_inundation 값 결정 (volume이 특정 survey 구간 사이에 위치할때 더 아랫값을 적용)
        # * 펌프 개시하는 조건을 초기값으로 결정해야함 (일단 level_flood + 0.3으로 결정)
        # * 외수위 값을 결정해야하는데 level_flood로 할 경우 그 밑으로 안떨어지는 문제가 발생
        # * 외수위 값은 elevation_volume 자료의 최저수위 값으로 하였음
        
        # 1. volume으로 height_inundation 결정
        # 2. height_inundation으로 drainage, pump 결정
        # 3. volume에서 유입량 더하고, drainage, pump 빼준 후 △t 후의 volume 결정 
        
        level_out = elevation_volume.T[0][0]
        volume_survey_prev = elevation_volume[0][1]
        height_survey_prev = elevation_volume[0][0]
        
        for height_survey, volume_survey in elevation_volume:
            
            kim = int((volume - volume_survey) * (volume - volume_survey_prev))
            
            if  kim <= 0:
                height_inundation = height_survey_prev
                height_diff = height_inundation - level_out
                break
            
            volume_survey_prev = volume_survey
            height_survey_prev = height_survey
            
        
        if height_inundation < level_flood + 0.3:
            drainage1 = k_coef * gate_width1 * math.pow(height_diff, 1.5)
            drainage2 = k_coef * gate_width2 * math.pow(height_diff, 1.5)
            drainage = min(volume/3600/interval, drainage1 + drainage2)
            pump = 0
            pump_volume = min(volume, pump_max * 3600 * interval)
            pump = pump_volume / 3600 / interval            
            drainage_list.append(drainage)
            pump_list.append(pump)
        
        elif height_inundation >= level_flood + 0.3:
            height_diff1 = min(height_diff, gate_height1)
            height_diff2 = min(height_diff, gate_height2)
            
            drainage1 = k_coef * gate_width1 * math.pow(height_diff1, 1.5)
            drainage2 = k_coef * gate_width2 * math.pow(height_diff2, 1.5)
            drainage = min(hydro, drainage1 + drainage2)
            
            pump_volume = min(volume, pump_max * 3600 * interval)
            pump = pump_volume / 3600 / interval
            drainage_list.append(drainage)
            pump_list.append(pump)

        drainage_volume = interval * 3600 * drainage
        pump_volume = interval * 3600 * pump
        volume = max(0, volume + hydro - drainage_volume - pump_volume) 

        height_inundation_list.append(height_inundation)
        volume_list.append(volume)

    inun_limit = []
    for i in range(len(hydrograph_final)):
        inun_limit.append(level_flood)
    
    elev, volume = elevation_volume.T
    min_elev = int(min(elev))    
    max_elev = int(max(elev)) + 1

    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_xlabel('hour')
    ax1.set_ylabel('Level (m)')
    ax1.plot(hydrograph_time, height_inundation_list, '.', color='red')
    ax1.plot(hydrograph_time, inun_limit, color='black')
    ax1.set_ylim(min_elev, max_elev)

    ax2 = ax1.twinx()
    ax2.set_ylabel('CMS')
    ax2.bar(hydrograph_time, pump_list, color = 'None', edgecolor = 'green', linewidth = 0.5) #color='blue', fill = False, edgecolor = 'black'
    ax2.set_ylim(0,400)
    plt.show()  
    
    final_result = np.stack((hydrograph_time, hydrograph_final, height_inundation_list, inun_limit, volume_list, drainage_list, pump_list), axis = 1)
    return final_result
    
def flooding_weir3 (hydrograph_final, hydrograph_time, pump, site):

    final_result = []
    site = int(site)
    if site == 1:
        vol = pd.read_table('input/volume_Flooding_A.txt', sep = '	', thousands = ',')
        var = 'a'
        print(site)
        
    elif site == 2:
        vol = pd.read_table('input/volume_Flooding_B.txt', sep = '	', thousands = ',')
        var = 'b'
        print(site)
    
    elif site == 3:
        vol = pd.read_table('input/volume_Flooding_C.txt', sep = '	', thousands = ',')
        var = 'c'
        print(site)
    
    elif site == 4:
        vol = pd.read_table('input/volume_Flooding_D.txt', sep = '	', thousands = ',')
        var = 'd'
        print(site)
        
    interval = hydrograph_time[1] - hydrograph_time[0]
    
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    _, _, _, _, _, _, level_flood, width1, width2, height1, height2 = target_site
    
    level_flood = float(level_flood)
    gate_width1 = float(width1)
    gate_width2 = float(width2)
    gate_height1 = float(height1)
    gate_height2 = float(height2)
    
    k_coef = 1.58
    pump_max = pump # CMS
    
    vol = vol.drop(['번호'], axis = 1)
    elevation_volume = np.array(vol)
    hydro_vol = 3600 * interval * hydrograph_final


    cum = 0
    hydro_cum = []
    for i in hydro_vol:
        cum += i
        hydro_cum.append(cum)
    
    
    pump_list = []    
    volume_list = []
    height_inundation_list = []

    volume = 0
    for hydro in hydrograph_final:
        # height_inundation 값 결정 (volume이 특정 survey 구간 사이에 위치할때 더 아랫값을 적용)
        # * 펌프 개시하는 조건을 초기값으로 결정해야함 (일단 level_flood + 0.3으로 결정)
        # * 외수위 값을 결정해야하는데 level_flood로 할 경우 그 밑으로 안떨어지는 문제가 발생
        # * 외수위 값은 elevation_volume 자료의 최저수위 값으로 하였음
        
        # 1. volume으로 height_inundation 결정
        # 2. height_inundation으로 drainage, pump 결정
        # 3. volume에서 유입량 더하고, drainage, pump 빼준 후 △t 후의 volume 결정 
        
        level_out = elevation_volume.T[0][0]
        volume_survey_prev = elevation_volume[0][1]
        height_survey_prev = elevation_volume[0][0]
        
        for height_survey, volume_survey in elevation_volume:
            
            kim = int((volume - volume_survey) * (volume - volume_survey_prev))
            
            if  kim <= 0:
                height_inundation = height_survey_prev
                height_diff = height_inundation - level_out
                break
            
            volume_survey_prev = volume_survey
            height_survey_prev = height_survey
            
        
        hydro_volume = hydro * 3600 * interval
# =============================================================================
#         if height_inundation < level_flood + 0.3:
#             drainage1 = k_coef * gate_width1 * math.pow(height_diff, 1.5)
#             drainage2 = k_coef * gate_width2 * math.pow(height_diff, 1.5)
#             drainage = min(volume / 3600 / interval, drainage1 + drainage2)
# # =============================================================================
# #             pump = 0
# #             pump_volume = min(volume, pump_max * 3600 * interval)
# #             pump = pump_volume / 3600 / interval            
# #             pump_list.append(pump)
# # =============================================================================
#             drainage_list.append(drainage)
#         
#         elif height_inundation >= level_flood + 0.3:
#             height_diff1 = min(height_diff, gate_height1)
#             height_diff2 = min(height_diff, gate_height2)
#             
#             drainage1 = k_coef * gate_width1 * math.pow(height_diff1, 1.5)
#             drainage2 = k_coef * gate_width2 * math.pow(height_diff2, 1.5)
#             drainage = min(hydro, drainage1 + drainage2)
#             
# # =============================================================================
# #             pump_volume = min(volume, pump_max * 3600 * interval)
# #             pump = pump_volume / 3600 / interval
# #             pump_list.append(pump)
# # =============================================================================
#             drainage_list.append(drainage)
# =============================================================================
            
        volume_rate = volume / 3600 / interval
        volume_after = hydro + volume_rate
        pump = min (pump_max, volume_after)
        volume_after = volume_after - pump
        volume = volume_after * 3600 * interval
        
        pump_list.append(pump)
        pump_volume = interval * 3600 * pump
        volume = max(0, volume + hydro_volume - pump_volume) 

        height_inundation_list.append(height_inundation)
        volume_list.append(volume)

    inun_limit = []
    for i in range(len(hydrograph_final)):
        inun_limit.append(level_flood)
    
    elev, volume = elevation_volume.T
    min_elev = int(min(elev))    
    max_elev = int(max(elev)) + 1

    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_xlabel('hour')
    ax1.set_ylabel('Level (m)')
    ax1.plot(hydrograph_time, height_inundation_list, '.', color='red')
    ax1.plot(hydrograph_time, inun_limit, color='black')
    ax1.set_ylim(min_elev, max_elev)

    ax2 = ax1.twinx()
    ax2.set_ylabel('CMS')
    ax2.bar(hydrograph_time, pump_list, color = 'None', edgecolor = 'green', linewidth = 0.5) #color='blue', fill = False, edgecolor = 'black'
    ax2.set_ylim(0,400)
    plt.show()  
    
    final_result = np.stack((hydrograph_time, hydrograph_final, height_inundation_list, inun_limit, volume_list, pump_list), axis = 1)
    return final_result    
    