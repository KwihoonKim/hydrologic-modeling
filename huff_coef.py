# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 18:32:58 2025

@author: Kwihoon Kim
"""
import pandas as pd
import json
vol = pd.read_table('huff_test.txt', sep = '	', thousands = ',')
vol = pd.read_table('huff_coef.txt', sep = '	', thousands = ',')

num = 10 # region number
coef = []
for i in vol:
    coef.append(vol[i][num])
    
del coef[0] # delete region number


quant = {}
for k in range(4):
    vol = pd.read_table('huff' + str(k+1) + '.txt', sep = '	', thousands = ',') 
    reg = {}
    for j in range(26):    
        coef = []
        for i in vol:
            coef.append(vol[i][j])
        
        del coef[0]
    
        reg_num = j + 1
        reg['region' + str(reg_num)] = coef
    
    quant['quant'+str(k+1)] = []
    quant['quant'+str(k+1)].append(reg)


with open ('huff_coef.json', 'w') as f:
    json.dump(quant, f)
    
with open ('huff_coef.json', 'r') as f:
    test = json.load(f)
    
    
    
    
    
