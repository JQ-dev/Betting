# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:40:37 2019

@author: admin
"""
import pandas as pd
import numpy as np
import time
import datetime

def get_results(filepath):
    clean_bets = pd.read_csv(filepath,sep=',')
    
    clean_bets['result1'] = clean_bets['result1'].replace('N/D',np.nan).apply(float)
    clean_bets['result2'] = clean_bets['result2'].replace('N/D',np.nan).apply(float)
    clean_bets['result3'] = clean_bets['result3'].replace('N/D',np.nan).apply(float)
    
    clean_bets['dev_rst1'] = clean_bets['dev_rst1'].replace('N/D',np.nan).apply(float)
    clean_bets['dev_rst2'] = clean_bets['dev_rst2'].replace('N/D',np.nan).apply(float)
    clean_bets['dev_rst3'] = clean_bets['dev_rst3'].replace('N/D',np.nan).apply(float)
    
    clean_bets['arb'] = clean_bets['arb'].replace('N/D',np.nan).apply(float)
    
    cond = clean_bets.loc[:,'booker'] == 'best deal'
    best = clean_bets.loc[cond,:]
    del cond
    

    best.loc[:,'game_time'] = pd.to_datetime( best.loc[:,'game_time'] )
    best.loc[:,'log']       = pd.to_datetime( best.loc[:,'log'] )
    
    
    last_arb = list(best['log'].drop_duplicates().sort_values())[-1] - datetime.timedelta(0,360)
    cond = ( best.loc[:,'log'] > last_arb )
    
    best = best.loc[cond,:]
    
    del cond, last_arb


    interesting = (best['arb'] < 0.99) 
    interesting.sum()

    int_results = best.loc[interesting,:]
    int_results = int_results.reset_index(drop=True)
    int_results['booker_R1'] = ''
    int_results['booker_R2'] = ''
    int_results['booker_R3'] = ''
    

    for i in range( int_results.shape[0] ):
        
        cond1 = ( clean_bets['url'] == int_results.loc[:,'url'].iloc[i] )
    #    cond2 = (clean_bets['log'] == int_results.loc[:,'log'].iloc[i])
        cond3 = (clean_bets['booker'] != 'best deal')
        
        cond4 = (clean_bets['result1'] == int_results.loc[:,'result1'].iloc[i])   
        int_results.loc[i,'booker_R1'] = clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')
    
        cond4 = (clean_bets['result2'] == int_results.loc[:,'result2'].iloc[i]) 
        int_results.loc[i,'booker_R2'] = clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')
    
        cond4 = clean_bets['result3'] == int_results.loc[:,'result3'].iloc[i]    
        int_results.loc[i,'booker_R3'] = clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')
    
    clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].values
    
    
    del cond1, cond3, cond4, i, interesting
    int_results.columns.to_list()
    
    final_result = int_results.loc[:,('name_team1','name_team2','score','arb',
                                      'booker_R1','result1','dev_rst1',
                                      'booker_R2','result2','dev_rst2',
                                      'booker_R3','result3','dev_rst3',
                                      'url')]
    
    return (clean_bets,final_result)

########################################################3
    



clean_bets,final_result = get_results()




