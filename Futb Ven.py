# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 14:22:15 2019

@author: admin
"""

# LAST MINUTE OPPORTUNITIES


# SOCCER


import pandas as pd
import numpy as np




last_bets = pd.read_csv('Odds_Fulbol_Venez.csv',sep=',')

last_bets.loc[:,'log'] = pd.to_datetime(last_bets['log']) 

last_filter = list( last_bets['log'].drop_duplicates().sort_values() )[-3]
  
cond = (last_bets['log'] > last_filter)

last_bets = last_bets.loc[cond,:].copy()


last_bets['team1'] = last_bets['team1'].replace('N/D',np.nan).apply(float)
last_bets['team2'] = last_bets['team2'].replace('N/D',np.nan).apply(float)
last_bets['tie'] = last_bets['tie'].replace('N/D',np.nan).apply(float)

last_bets['fairness'] = (1  / last_bets['team1']) + (1  / last_bets['team2']) + (1  / last_bets['tie'])

#last_bets['prob_1'] = 1  / last_bets['team1']
#last_bets['prob_2'] = 1  / last_bets['team2']
#last_bets['prob_3'] = 1  / last_bets['tie']


interesting = (last_bets['fairness'] < 0.98) 
interesting.sum()


int_results = last_bets.loc[interesting,:]
int_results = int_results.reset_index(drop=True)
int_results['booker_R1'] = ''
int_results['booker_R2'] = ''
int_results['booker_R3'] = ''




for i in range( int_results.shape[0] ):
    
    cond1 = ( last_bets['game_teams'] == int_results.loc[:,'game_teams'].iloc[i] )
#    cond2 = (last_bets['log'] == int_results.loc[:,'log'].iloc[i])
    cond3 = (last_bets['booker'] != 'best deal')
    
    cond4 = (last_bets['team1'] == int_results.loc[:,'team1'].iloc[i])   
    int_results.loc[i,'booker_R1'] = last_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')

    cond4 = (last_bets['team2'] == int_results.loc[:,'team2'].iloc[i]) 
    int_results.loc[i,'booker_R2'] = last_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')

    cond4 = last_bets['tie'] == int_results.loc[:,'tie'].iloc[i]    
    int_results.loc[i,'booker_R3'] = last_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')

last_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].values


del cond, cond1, cond3, cond4, i, interesting, last_filter








