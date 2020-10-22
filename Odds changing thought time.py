# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 08:42:46 2019

@author: admin
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_csv('Football_odds.csv')

dfsample = df.head(100)


###############################################################################
# Get the time until the game start

# Transforming to date format
df.loc[:,'log'] = pd.to_datetime( df.loc[:,'log'] )


# Splitting intagame and before game data
cond = df.loc[:,'game_time'].str.contains(':')
df.loc[:,'game_schedule'] = df.loc[:,'game_time'].where(cond,'N/D') 


df.loc[:,'game_info'] = df.loc[:,'day_game'].apply(str) + df.loc[:,'teams']
matches = {}
for index in range(df.shape[0]):
    if df.loc[ index ,'game_schedule'] != 'N/D':
        matches[df.loc[ index ,'game_info']] = df.loc[ index ,'game_schedule']
    
df.loc[:,'game_schedule'] = df.loc[:,'game_info'].map(matches)    
    
    

# Combining day and hour - and calculating time to game
df.loc[:,'day_game'] = df.loc[:,'day_game'].apply(str) + " " +  df.loc[:,'game_schedule']
df.loc[:,'day_game']       = pd.to_datetime( df.loc[:,'day_game'] )
df = df.drop('game_schedule',axis=1)

#cond = ( df.loc[:,'day_game'] > df.loc[:,'log']  )
df.loc[:,'time_to_game'] = (df.loc[:,'day_game'] - df.loc[:,'log'] ) #.where(cond,'N/D') 

del cond,index,matches

###############################################################################
# Get the probabilities

df.loc[:,('Win1')] = df.loc[:,('Win1')].replace('-',np.nan).apply(float) 
df.loc[:,('Win2')] = df.loc[:,('Win2')].replace('-',np.nan).apply(float) 
df.loc[:,('Tie')] = df.loc[:,('Tie')].replace('-',np.nan).apply(float) 

df.loc[:,'bet_fairness'] = 1/df.loc[:,('Win1')]  + 1/df.loc[:,('Tie')]  + 1/df.loc[:,('Win2')] 


df.loc[:,('Win1')] = 1/df.loc[:,('Win1')] / df.loc[:,'bet_fairness']
df.loc[:,('Win2')] = 1/df.loc[:,('Win2')] / df.loc[:,'bet_fairness']
df.loc[:,('Tie')] = 1/df.loc[:,('Tie')] / df.loc[:,'bet_fairness']



###############################################################################
# Odds before the game 

cond = df.loc[:,'game_time'].apply(lambda x : ':' in x )
dfbefore = df.loc[cond,:]

cond = dfbefore.loc[:,'time_to_game'].apply(lambda x : (x / np.timedelta64(1, 's')) > 0 )
dfbefore = dfbefore.loc[cond,:]


dfbefore.loc[:,'time_to_game15'] = dfbefore.loc[:,'time_to_game'].apply(lambda x : pd.Timedelta.round( x , '60min' ) )

dfbefore.loc[:,'time_to_game'] = dfbefore.loc[:,'time_to_game'] / np.timedelta64(60*60, 's')


################################################################################
x = dfbefore.loc[:,'time_to_game']
y = dfbefore.loc[:,'bet_fairness']

plt.scatter(-x,y)
plt.xlabel('Days to the Game')
plt.ylabel('Avg Fairness')
plt.title('Bookmaker profits before the game')
plt.show()
################################################################################




# Analisys 1: How the tie odds moves...


df48before = dfbefore.loc[dfbefore.loc[:,'time_to_game'] < 48,:]




odd_changes = df48before.loc[:,('game_info','Tie')]

aggregations = {
    'changes':'count',
    'stdev':'std'  ,
    'max':'max'  ,
    'min':'min'  ,
    'range': lambda x: max(x) - min(x)
}

odd_changes2 = odd_changes.groupby(['game_info'])['Tie'].agg(aggregations)







#df = df.drop('game_schedule',axis=1)


df.loc[:,'game_schedule'] = df.loc[:,'game_time'] 




df.loc[:,'game_time'] = df.loc[:,'day_game'].apply(str) + df.loc[:,'game_time'] 


df.loc[:,'game_time'] = pd.to_datetime( df.loc[:,'game_time'] )



df['time_to_game'] = pd.to_datetime( clean_bets.loc[:,'log'] )    
