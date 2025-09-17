# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 22:25:07 2022

@author: Kwihoon
"""

import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
from eff_rainfall import nrcs_cn, interval_to_hr
import json

def design_rainfall (var, duration):
    idf_coef = pd.read_table('input/IDF_coef.txt')
    coef = idf_coef[var]
    x = math.log(duration)
    sum1 = coef[0] + coef[1]*x + coef[2]*math.pow(x,2)+ coef[3]*math.pow(x,3)\
        + coef[4]*math.pow(x,4)+ coef[5]*math.pow(x,5)+ coef[6]*math.pow(x,6)

    des_rain = math.exp(sum1) * duration
    return des_rain

def rainfall_duration(name):
    name = name 
    station = pd.read_table('input/station_code_RainfallDistribution.txt', sep = '	', thousands = ',')
    codes = list(station['code'])
    names = list(station['name'])
    index = names.index(name)
    code = codes[index]    
    
    freq = 20 # default value (20 year)
    
    metadata = np.loadtxt('input/rainfall_duration_RainfallDistribution.txt')

    data = []
    for i, array in enumerate(metadata):
        if str(code) == str(int(array[0])):
            data = metadata[i:i+14]
            break
        
    col = np.delete(data[0,:], 0)
    row = np.delete(data[:,0], 0)
    
    data = np.delete(data, 0, axis = 0)
    data = np.delete(data, 0, axis = 1)
    
    index = list(row).index(freq)
    rainfall = data[index]
    
# =============================================================================
#     rainfall_final = []
#     pre_hour = 1
#     for i in range(int(col[-1])):
#         i = i + 1
#         for j, hour in enumerate(col):
#             if i == hour:
#                 rain = rainfall[j] 
#                 rainfall_final.append(rain)
#                 pre_hour = hour
#                 print(i*10)
#             
#             elif (i - pre_hour) * (i - hour) < 0:
#                 print(i-pre_hour)
# =============================================================================

    result = np.vstack((col,rainfall))
    return result

def idf (duration, interval, var, r):
    '환경부 (2019) 홍수량 산정 표준지치 별첨_지역빈도해석: 창원 지역 자료 기준 (22번 지역)'
    idf_coef = pd.read_table('input/IDF_coef.txt')
    coef = idf_coef[var]
    x = math.log(duration)
    sum1 = coef[0] + coef[1]*x + coef[2]*math.pow(x,2)+ coef[3]*math.pow(x,3)\
        + coef[4]*math.pow(x,4)+ coef[5]*math.pow(x,5)+ coef[6]*math.pow(x,6)

    des_rain = math.exp(sum1) * duration
    
    unit_time_list = []
    probable_rainfalls = []
    
    for i in range(duration):
        hour = i + 1
        prob_rain = design_rainfall(var, hour)
        unit_time_list.append(hour)
        probable_rainfalls.append(prob_rain)
        
    probable_rainfalls = np.array(probable_rainfalls)
    probable_rainfalls = np.round(probable_rainfalls, 4)
    time_hr = np.array(unit_time_list)
    
    hour_rainfall = np.stack((time_hr, probable_rainfalls), axis=1)
    interval_rainfall = splitRainDist(hour_rainfall, interval)
    interval_rainfall_repos = reposition(interval_rainfall, r)
    return interval_rainfall_repos

def huff(duration, interval, var, quantile):
    idf_coef = pd.read_table('input/IDF_coef.txt')
    coef = idf_coef[var]
    x = math.log(duration)
    sum1 = coef[0] + coef[1]*x + coef[2]*math.pow(x,2)+ coef[3]*math.pow(x,3)\
        + coef[4]*math.pow(x,4)+ coef[5]*math.pow(x,5)+ coef[6]*math.pow(x,6)

    des_rain = math.exp(sum1) * duration
    num = int(duration / interval) + 1

       
    'var -> region값 불러오기'
    '========================================================================='    
    variable = pd.read_table('variable.txt', sep = '	', thousands = ',')
    target_site = variable[var]
    name, _, _, _, _, _, _, _, _, _, _, _, _ = target_site
        
    station_code = pd.read_table('input/station_code.txt')
    station_code = np.array(station_code) 
    row_num = np.where(station_code.T[0] == name)[0][0]
    region_num = station_code.T[1][row_num]
    r = 'region'+str(region_num) 
    '========================================================================='
    
    'region + quantile -> huff coefficient 불러오기'
    '========================================================================='
    if quantile == 1:
        q = 'quant1'
    elif quantile == 2:
        q = 'quant2'
    elif quantile == 3:
        q = 'quant3'
    elif quantile == 4:
        q = 'quant4' 
        
    with open ('input/huff_coef.json', 'r') as f:
        huff_coef = json.load(f)
        
    coefficient = huff_coef[q][0][r]
    a,b,c,d,e,f,g = coefficient
    '========================================================================='
    
    interval_percent = []
    for i in range(num):
        interval_percent.append(i * interval / duration * 100)
    interval_percent.append(100)
    
    huff_cum = []
    rain = 0
    for i in interval_percent:
        xa = a * math.pow(i,6)
        xb = b * math.pow(i,5)
        xc = c * math.pow(i,4)
        xd = d * math.pow(i,3)
        xe = e * math.pow(i,2)
        xf = f * math.pow(i,1)
        xg = g
        y = max(0, xa + xb + xc + xd + xe + xf + xg)
        y = y / 100 * des_rain
        y = round(y,1)
        rain_diff = max(0, y - rain)
        huff_cum.append(rain_diff)
        rain = y
    
    interval_time = []
    for i in range(num):
        interval_time.append(i * interval)
    interval_time.append(duration)
    
    interval_rainfall = np.stack((interval_time, huff_cum), axis=1)
    return interval_rainfall

def splitRainDist(hour_rainfall, intervalTime):
    rain_dist = []
    time_list = []
    i = 0
    duration = int(max(hour_rainfall.T[0]))
    
    while i*intervalTime <= duration:
        time_list.append(i*intervalTime)
        i += 1
    time_list = np.round(time_list,3)

    rainfall = []
    for time in time_list:
        diff = 0
        rain_cum = 0
        rain_diff = 0
        pre_time = 0
        pre_rain = 0
        for time_cum, rain in hour_rainfall:
            
            if (time - time_cum) * (time - pre_time) <= 0: 
                rain_cum = (rain - pre_rain)/(time_cum - pre_time) * (time - time_cum) + rain

            pre_rain = rain
            pre_time = time_cum    
    
        rain_diff = round(rain_cum,3)
        rainfall.append(rain_diff)
        
    x = 0
    rainfall_final = []
    for i in rainfall:
        if i - x >= 0:
            rain = i - x
            x = i
        else:
            rain = 0
        rainfall_final.append(rain)
        
    rainfall_final = np.array(rainfall_final)    
    time_list = np.array(time_list)
    rain_dist = np.stack((time_list, rainfall_final), axis = 1)
    
    rain_last = hour_rainfall.T[1][-1] - sum(rain_dist.T[1])
    last_component = np.array([duration, rain_last])

    final = np.vstack([rain_dist, last_component])
    return final

'''
Example (창원)

# Input 자료
rainfall_distribution: idf 혹은 huff 결과
duration: 48 (hr)
intervalTime: 0.185 (hr)

# Output 자료
구간강우량  누적시간
(mm)    (hr)
0	    0
28.573	0.185
14.449	0.37
10.986	0.555
8.923	0.74
7.562	0.925
6.324	1.11
5.812	1.295
5.812	1.48
4.772	1.665
4.645	1.85
4.465	2.035
3.699	2.22
3.698	2.405
3.698	2.59
3.698	2.775
3.698	2.96
3.124	3.145
2.966	3.33
2.966	3.515
2.965	3.7
2.966	3.885
2.735	4.07
2.355	4.255
2.355	4.44
2.355	4.625
    .
    .
    .
    .
0.388	46.62
0.387	46.805
0.388	46.99
0.388	47.175
0.387	47.36
0.388	47.545
0.387	47.73
0.388	47.915
'''

def reposition(split_rain, r):
    
    unit_r = round(1 / len(split_rain),6)
    r_coef = int(r / unit_r)
    
    rainfall_reposition_interval = []
    hydro_interval_diff = split_rain.T[1]
    hydro_interval_diff = np.delete(hydro_interval_diff, 0, axis = 0)
    
# =============================================================================
#     if r_coef > len(hydro_interval_diff):
#         r_coef = len(hydro_interval_diff)
#         print('Error (EffRainfall -> reposition): r is too big')
# =============================================================================
        
    odd_num = []
    even_num = []
    remnant = []
    
    r_coef_reverse = len(hydro_interval_diff) - r_coef
    r_refer = min(r_coef, r_coef_reverse) * 2   
    
    for i, rain in enumerate(hydro_interval_diff):
        if i < r_refer:
            if i % 2 == 0:
                even_num.append(round(rain,3))
        
            elif i % 2 == 1:
                odd_num.append(round(rain,3))
                
        elif i >= r_refer:
            remnant.append(rain)
            
    odd_num = np.array(odd_num)
    even_num = np.array(even_num)
    remnant = np.array(remnant)
    
    even_num = np.flip(even_num)

    if r_coef < r_coef_reverse:
        rainfall_interval_repos = np.hstack([even_num, odd_num, remnant])
        
    elif r_coef >= r_coef_reverse:
        remnant = np.flip(remnant)
        rainfall_interval_repos = np.hstack([remnant, even_num, odd_num])
        
    hydro_time = split_rain.T[0]
    hydro_time = np.delete(hydro_time, 0, axis = 0)

    rainfall_reposition_interval = np.stack((hydro_time, rainfall_interval_repos), axis = 1)
    rainfall_reposition_interval = np.insert(rainfall_reposition_interval, 0, 0, axis = 0)
    return rainfall_reposition_interval



    
    
    
    
    
    
    
    
    
    
    
    
    
    

