# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 16:43:36 2022

@author: Kwihoon
"""
import math
import numpy as np

def nrcs_cn(hyetograph, cn):
    eff_rainfall_distribution = []
    rainfall_distribution = list(hyetograph.T[1])
    time_hr = hyetograph.T[0]
        
    '단위도 26개 자료로 만들기 때문 (RMS 기준)'
    unit = []
    for i in range(26):
        unit.append(0)
    
    S = 25400/cn-254

    rainfall_cum = []
    eff_rainfall_cum = []
    k = 0
    
    for i in rainfall_distribution:
        k += i
        rainfall_cum.append(k)
        
        if k < 0.2*S:
            eff_rainfall_cum.append(0)       
            
        elif k >= 0.2*S:        
            cum_effective_rain = math.pow(k-0.2*S,2)/(k+0.8*S)
            eff_rainfall_cum.append(cum_effective_rain)        
            
    eff_rainfall_distribution = []
    pre_cum = 0
    for i in eff_rainfall_cum:
        eff_rainfall_distribution.append(round(i - pre_cum,3))
        pre_cum = i
    
    eff_rainfall_distribution = np.stack((time_hr, eff_rainfall_distribution), axis=1)

    return eff_rainfall_distribution

'''
Example (창원)

# Input 자료
* cn: 90 (무차원)
* hydro2
    구간강우량  누적시간
    (mm)    (hr)
    0	0
    5.812	0.185
    6.324	0.37
    8.923	0.555
    14.449	0.74
    28.573	0.925
    10.986	1.11
    7.562	1.295
    5.812	1.48
    4.772	1.665
    4.645	1.85
    4.465	2.035
    3.699	2.22
    3.698	2.405
    3.698	2.59
        .
        .
        .
        .
    0.387	45.51
    0.388	45.695
    0.388	45.88
    0.387	46.065
    0.388	46.25
    0.387	46.435
    0.388	46.62
    0.387	46.805
    0.388	46.99
    0.388	47.175
    0.387	47.36
    0.388	47.545
    0.387	47.73
    0.388	47.915

# Output 자료
* eff_rainfall_distribution

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
'''

def interval_to_hr(hydro2, cn, duration):
    hydro_hr = []
    rainfall_dist = hydro2.T[0]
    time_interval_cum = hydro2.T[1]
    
    rainfall_cum = []
    k = 0
    for i in rainfall_dist:
        k += i
        rainfall_cum.append(k)

    time_hr = []
    k = 0
    for i in range(duration):
        k += 1
        time_hr.append(k)
        
    rainfall_distribution = np.stack((rainfall_cum, time_interval_cum), axis = 1)
    
    rainfall = []
    for time in time_hr:
        diff = 0
        rain_cum = 0
        rain_diff = 0
        pre_time = 0
        pre_rain = 0
        for rain, time_cum in rainfall_distribution:
            
            if (time - time_cum) * (time - pre_time) <= 0: 
                rain_cum = (rain - pre_rain)/(time_cum - pre_time) * (time - time_cum) + rain
            elif time == len(time_hr):
                rain_cum = rain
            pre_rain = rain
            pre_time = time_cum  
            
        rainfall.append(rain_cum)
        
    rainfall_hr_final = []
    diff = 0
    pre_rain = 0
    for i in rainfall:
        diff = i - pre_rain
        rainfall_hr_final.append(diff)
        pre_rain = i
        
    hydro_hr = np.stack((rainfall, time_hr), axis = 1)
  
    return hydro_hr       
    

def reposition(split_rain, r):
    
    unit_r = round(1 / len(split_rain),6)
    r_coef = int(r / unit_r)
    
    rainfall_reposition_interval = []
    hydro_interval_diff = split_rain.T[0]
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
        
    hydro_time = split_rain.T[1]
    hydro_time = np.delete(hydro_time, 0, axis = 0)

    rainfall_reposition_interval = np.stack((hydro_time, rainfall_interval_repos), axis = 1)
    rainfall_reposition_interval = np.insert(rainfall_reposition_interval, 0, 0, axis = 0)
    return rainfall_reposition_interval

'''
Example (창원)

# Input 자료
* r: 3 (호우전진계수) 
    => 실제로는 0 < r < 1 인데 3을 전체 개수 260으로 나눠주면 0.0625가 나옴 
    => 김귀훈 등 (2023), 농지배수 수문설계 기준과 임계지속기간을 고려한 농업 소유역 침수분석 참조
* split_rain
    =>
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

# Output 자료
* rainfall_reposition_interval
    구간강우량  누적시간
    (mm)    (hr)
    0	0
    5.812	0.185
    6.324	0.37
    8.923	0.555
    14.449	0.74
    28.573	0.925
    10.986	1.11
    7.562	1.295
    5.812	1.48
    4.772	1.665
    4.645	1.85
    4.465	2.035
    3.699	2.22
    3.698	2.405
    3.698	2.59
        .
        .
        .
        .
    0.387	45.51
    0.388	45.695
    0.388	45.88
    0.387	46.065
    0.388	46.25
    0.387	46.435
    0.388	46.62
    0.387	46.805
    0.388	46.99
    0.388	47.175
    0.387	47.36
    0.388	47.545
    0.387	47.73
    0.388	47.915
'''
