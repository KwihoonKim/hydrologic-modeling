# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 22:37:36 2023

@author: Kwihoon
"""


import numpy as np
import pandas as pd

def damage(final, site):
    interval = final.T[0][1] - final.T[0][0]
    
    inun_level = final.T[2]
    inun_level = pd.DataFrame(inun_level)
    inun_level.columns = ['level']
    
    site = int(site)
    
    if site == 1:
        elevation = pd.read_table('input/elevation_ratio_DamageEstimation_A.txt', sep = '	', thousands = ',')
    
    elif site== 2:
        elevation = pd.read_table('input/elevation_ratio_DamageEstimation_B.txt', sep = '	', thousands = ',')

    elif site== 3:
        elevation = pd.read_table('input/elevation_ratio_DamageEstimation_C.txt', sep = '	', thousands = ',')

    elif site== 4:
        elevation = pd.read_table('input/elevation_ratio_DamageEstimation_D.txt', sep = '	', thousands = ',')
    
    num = len(elevation)
    elevation = elevation[0:num]
        
    elevation = elevation.reset_index()
    # Transform Cumulative volume into Area for each elevation
    num = elevation.shape[0]
    elev_init = float(elevation['표고'][0])
    vol_init = float(elevation['누가내용적(m3)'][0])
    area_init = 0
    elevation['area'] = 0
    elevation['area_increase'] = 0

    for i in range(num):
        vol_diff = float(elevation['누가내용적(m3)'][i]) - vol_init
        vol_init = float(elevation['누가내용적(m3)'][i])
        
        area_sum = vol_diff / 0.1 * 2 # upper area (A + 0.1m) + lower area (A m) 
        area = area_sum - area_init
        elevation['area'][i] = area    
        elevation['area_increase'][i] = max(0, int(area - area_init))
        
        area_init = area
        
    # Calculate inundation duration for area of each elevation
    elevation['inun_time'] = 0
    num = elevation.shape[0]
    for i in range(num):
        elev = float(elevation['표고'][i])
        aa = inun_level.loc[inun_level['level'] > elev].shape[0]
        inun_time = aa * interval
        elevation['inun_time'][i] = inun_time
        
    # import crop data from crop_income.txt file
    crop_data = pd.read_table('input/crop_income_DamageEstimation.txt', sep = '	', thousands = ',',  index_col='index')
    
    # Calculate damage rate for each crop and area of elevation
    elevation['콩_피해율'] = 0
    elevation['고추_피해율'] = 0
    elevation['벼_피해율'] = 0
    elevation['수박_피해율'] = 0

    for i in range(num):
        inun_time  = elevation['inun_time'][i]
        
        # 콩
        if inun_time == 0:
            elevation['콩_피해율'][i] == 0
            
        elif inun_time <= crop_data['콩']['point']:
            elevation['콩_피해율'][i] = inun_time * crop_data['콩']['slope1'] + crop_data['콩']['coef1']
        
        elif inun_time > crop_data['콩']['point']:
            elevation['콩_피해율'][i] = inun_time * crop_data['콩']['slope2'] + crop_data['콩']['coef2']
            
        # 고추
        if inun_time == 0:
            elevation['고추_피해율'][i] == 0
        
        elif inun_time <= crop_data['고추']['point']:
            elevation['고추_피해율'][i] = inun_time * crop_data['고추']['slope1'] + crop_data['고추']['coef1']
        
        elif inun_time > crop_data['고추']['point']:
            elevation['고추_피해율'][i] = inun_time * crop_data['고추']['slope2'] + crop_data['고추']['coef2']
        
        # 벼
        if inun_time == 0:
            elevation['벼_피해율'][i] == 0
            
        elif inun_time <= crop_data['벼']['point']:
            elevation['벼_피해율'][i] = inun_time * crop_data['벼']['slope1'] + crop_data['벼']['coef1']
        
        elif inun_time > crop_data['벼']['point']:
            elevation['벼_피해율'][i] = inun_time * crop_data['벼']['slope2'] + crop_data['벼']['coef2']
            
        # 수박
        if inun_time == 0:
            elevation['수박_피해율'][i] == 0
            
        elif inun_time <= crop_data['수박']['point']:
            elevation['수박_피해율'][i] = inun_time * crop_data['수박']['slope1'] + crop_data['수박']['coef1']
        
        elif inun_time > crop_data['수박']['point']:
            elevation['수박_피해율'][i] = inun_time * crop_data['수박']['slope2'] + crop_data['수박']['coef2']        
            
    # Allocate area percentage for each crop
    
    # Calculate area for each crop
    elevation['콩면적'] = 0    
    elevation['고추면적'] = 0    
    elevation['벼면적'] = 0    
    elevation['수박면적'] = 0    
        
    for i in range(num):
        elevation['콩면적'][i] = float(elevation['콩면적비율'][i]) * float(elevation['area_increase'][i]) / 100
        elevation['고추면적'][i] = float(elevation['고추면적비율'][i]) * float(elevation['area_increase'][i]) / 100
        elevation['벼면적'][i] = float(elevation['벼면적비율'][i]) * float(elevation['area_increase'][i]) / 100
        elevation['수박면적'][i] = float(elevation['수박면적비율'][i]) * float(elevation['area_increase'][i]) / 100

    # Calculate sales for each crop and area of elevation
    elevation['콩수익'] = 0
    elevation['고추수익'] = 0
    elevation['벼수익'] = 0
    elevation['수박수익'] = 0
    
    for i in range(num):
        elevation['콩수익'][i] = elevation['콩면적'][i] * crop_data['콩']['income']/1000
        elevation['고추수익'][i] = elevation['고추면적'][i] * crop_data['고추']['income']/1000
        elevation['벼수익'][i] = elevation['벼면적'][i] * crop_data['벼']['income']/1000
        elevation['수박수익'][i] = elevation['수박면적'][i] * crop_data['수박']['income']/1000
        
    # Calculate damage cost for each crop and area of elevation
    elevation['콩피해액'] = 0
    elevation['고추피해액'] = 0
    elevation['벼피해액'] = 0   
    elevation['수박피해액'] = 0   
    
    for i in range(num):
        elevation['콩피해액'][i] = elevation['콩수익'][i] * elevation['콩_피해율'][i] / 100
        elevation['고추피해액'][i] = elevation['고추수익'][i] * elevation['고추_피해율'][i] / 100
        elevation['벼피해액'][i] = elevation['벼수익'][i] * elevation['벼_피해율'][i] / 100
        elevation['수박피해액'][i] = elevation['수박수익'][i] * elevation['수박_피해율'][i] / 100
        
    
    damage_cost = int(elevation['콩피해액'].sum() + elevation['고추피해액'].sum() + elevation['벼피해액'].sum() + elevation['수박피해액'].sum())
    return damage_cost
    



