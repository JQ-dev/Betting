# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:40:37 2019

@author: admin
"""
import pandas as pd
import numpy as np

clean_bets = pd.read_csv('Odds_Baseball.csv',sep=',')

clean_bets['team1'] = clean_bets['team1'].replace('N/D',np.nan).apply(float)
clean_bets['team2'] = clean_bets['team2'].replace('N/D',np.nan).apply(float)

clean_bets.loc[:,'log'] = pd.to_datetime(clean_bets['log']) 


cond = clean_bets.loc[:,'booker'] == 'best deal'
best = clean_bets.loc[cond,:]
del cond
best = best.replace(' Betting Odds','',regex=True)
#best = clean_bets.copy()

best[['teams','sport']] = best["game_teams"].str.split(',', n = 2, expand = True) 

best[['name_team1','name_team2']] = best["teams"].str.split(' - ', n = 2, expand = True) 

best[['day','date','time']] = best["game_time"].str.split(',', n = 3, expand = True) 

best['game_time'] = pd.to_datetime(best['date'] + best['time'])

best['game_info'] = best['game_teams']

best= best.drop(['booker','game_teams','day','teams','url','sport','date','time'],axis=1)

best['fairness'] = (1  / best['team1']) + (1  / best['team2'])

best['prob_1'] = 1  / best['team1']
best['prob_2'] = 1  / best['team2']


cond = (best['log'] - best['game_time']).apply(lambda x : x.total_seconds() ) < (60*10)

best = best[cond,:]




cond = (
       (clean_bets['game_teams'] == 'Kansas City Royals - St.Louis Cardinals Betting Odds, Baseball - MLB') 
#        & 
#         (clean_bets['booker']    == 'Marathonbet'  )
        )
check = clean_bets.loc[cond,:].copy()

del cond


#check = check.replace('N/D','0')

check.loc[:,'fairness'] = (1  / check.loc[:,'team1']) + (1  / check.loc[:,'team2'])



# Combining files
#
#file1 = pd.read_csv('Odds_Baseball.csv',sep=',')
#file2 = pd.read_csv('Odds_Baseball_temp.csv',sep=',')
#
#file3 = file1.append(file2)
#
#file3.to_csv('Odds_Baseball.csv',sep=',',na_rep='N/D',index=False)




