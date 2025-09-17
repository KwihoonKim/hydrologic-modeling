# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 22:46:19 2024

@author: Kwihoon
"""

import math

def drainage_flow (depth, outside, baseline, channel_width, channel_height):
    
    diff_in = max(0, depth - baseline)
    diff_out = max(0, outside - baseline)
    
    # free flow (CMS)
    if diff_in <= channel_height:
        flow_out = 0.65 * channel_width * math.pow(diff_in, 1.5)
        flow_in = 0.65 * channel_width * math.pow(diff_out, 1.5)
        flow = max(0, flow_out - flow_in)
        
    # submerged flow (CMS)
    elif diff_in > channel_height:
        diff = max(0, diff_in - diff_out)
        flow = 1.928 * channel_width * channel_height * math.pow(diff, 0.5)
    
    if diff_out > diff_in:
        flow = 0
        
    return flow

def vol_to_level(hydro_vol, elev):
    
    height_prev = elev[0][0]
    volume_prev = elev[0][1]
    
    if hydro_vol > elev[-1][1]:
        return elev[-1][0]
    
    else:
        for height, volume in elev:
        
            kim = (hydro_vol - volume_prev) * (hydro_vol - volume)
            if  kim <= 0:
                height_inundation = height_prev
                break
        
            height_prev = height
            volume_prev = volume
    
        return height_inundation
    