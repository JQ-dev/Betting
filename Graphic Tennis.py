# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 08:39:55 2019

@author: admin
"""

import pandas as pd  
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import os


game_files = []
for file in os.listdir():
    if file.endswith(".txt"):
        game_files.append(file)




file_name = game_files[11]
print(file_name)

df = pd.read_csv(file_name,sep=',')


# Points to win the set (player 1)

df['ptw'] = 0
df['ptl'] = 0

for index in df.index:
    if df.loc[index,'game1'] == '0' and df.loc[index,'game2'] == '0':
        df.loc[index,'ptw'] = 4
        df.loc[index,'ptl'] = 4
    elif df.loc[index,'game1'] == '15' and df.loc[index,'game2'] == '0':
        df.loc[index,'ptw'] = 3
        df.loc[index,'ptl'] = 4
    elif df.loc[index,'game1'] == '30' and df.loc[index,'game2'] == '0':
        df.loc[index,'ptw'] = 2
        df.loc[index,'ptl'] = 4
    elif df.loc[index,'game1'] == '40' and df.loc[index,'game2'] == '0':
        df.loc[index,'ptw'] = 1
        df.loc[index,'ptl'] = 5
    elif df.loc[index,'game1'] == '15' and df.loc[index,'game2'] == '15':
        df.loc[index,'ptw'] = 3
        df.loc[index,'ptl'] = 3
    elif df.loc[index,'game1'] == '30' and df.loc[index,'game2'] == '15':
        df.loc[index,'ptw'] = 2
        df.loc[index,'ptl'] = 3
    elif df.loc[index,'game1'] == '40' and df.loc[index,'game2'] == '15':
        df.loc[index,'ptw'] = 1
        df.loc[index,'ptl'] = 4
    elif df.loc[index,'game1'] == '15' and df.loc[index,'game2'] == '30':
        df.loc[index,'ptw'] = 3
        df.loc[index,'ptl'] = 2
    elif (df.loc[index,'game1'] == '30' and df.loc[index,'game2'] == '30') or \
         (df.loc[index,'game1'] == '40' and df.loc[index,'game2'] == '40'):
        df.loc[index,'ptw'] = 2
        df.loc[index,'ptl'] = 2
    elif (df.loc[index,'game1'] == '40' and df.loc[index,'game2'] == '30') or \
         (df.loc[index,'game1'] == 'ADV' and df.loc[index,'game2'] == '40'):
        df.loc[index,'ptw'] = 1
        df.loc[index,'ptl'] = 3
    elif (df.loc[index,'game1'] == '30' and df.loc[index,'game2'] == '40') or \
         (df.loc[index,'game1'] == '40' and df.loc[index,'game2'] == 'ADV'):
        df.loc[index,'ptw'] = 3
        df.loc[index,'ptl'] = 1
    elif df.loc[index,'game1'] == '0' and df.loc[index,'game2'] == '15':
        df.loc[index,'ptw'] = 4
        df.loc[index,'ptl'] = 3
    elif df.loc[index,'game1'] == '0' and df.loc[index,'game2'] == '30':
        df.loc[index,'ptw'] = 4
        df.loc[index,'ptl'] = 2
    elif df.loc[index,'game1'] == '0' and df.loc[index,'game2'] == '40':
        df.loc[index,'ptw'] = 5
        df.loc[index,'ptl'] = 1
    elif df.loc[index,'game1'] == '15' and df.loc[index,'game2'] == '40':
        df.loc[index,'ptw'] = 4
        df.loc[index,'ptl'] = 1
    else:
        df.loc[index,'ptw'] = 0
        df.loc[index,'ptl'] = 0


# Just points
df1 = df.copy()  
      
df1.loc[:,'game'] = df1.loc[:,'game1'] + '-' + df1.loc[:,'game2']        
#df1 = df1.drop_duplicates(subset=['game1','game2','score'],keep='last')
cond = df1.loc[:,'game'].shift(-1) != df1.loc[:,'game']
df1 = df1.loc[cond,:]


df1[['score']] = df1[['score']].replace(' ','',regex=True )

df1[['set1','set2','set3','set4','set5']] = df1['score'].str.split(pat='\]\[',expand = True)
df1[['set1']] = df1[['set1']].replace('\[','',regex=True )
df1[['set5']] = df1[['set5']].replace('\]','',regex=True )
df1[['set1','set2','set3','set4','set5']] = df1[['set1','set2','set3','set4','set5']].replace('-,-',np.nan)

df1['set'] = df1.loc[:,'score'].apply(lambda x : int( 5 - x.count('-')/2) )



df1.loc[:,'game_score'] = df1.loc[:,'game']

df1['set_score'] = np.nan

df1.loc[:,'set_score'] = df1.loc[:,'set5']

cond = df1.loc[:,'set_score'].isna()
df1.loc[:,'set_score'] = df1.loc[:,'set4'].where(cond,df1.loc[:,'set_score'])

cond = df1.loc[:,'set_score'].isna()
df1.loc[:,'set_score'] = df1.loc[:,'set3'].where(cond,df1.loc[:,'set_score'])

cond = df1.loc[:,'set_score'].isna()
df1.loc[:,'set_score'] = df1.loc[:,'set2'].where(cond,df1.loc[:,'set_score'])

cond = df1.loc[:,'set_score'].isna()
df1.loc[:,'set_score'] = df1.loc[:,'set1'].where(cond,df1.loc[:,'set_score'])

df1 = df1.drop(['set1','set2','set3','set4','set5'],axis=1)
df1 = df1.drop(['game1','game2'],axis=1)


df1[['setscore1','setscore2']] = df1['set_score'].str.split(pat=',',expand = True)
df1.loc[:,'setscore1'] = df1.loc[:,'setscore1'].apply(int)
df1.loc[:,'setscore2'] = df1.loc[:,'setscore2'].apply(int)

df1.loc[:,'btw'] = np.nan
#df1.loc[:,'setscore1'] - df1.loc[:,'setscore2']

condS = df1.loc[:,'service'] == 'player1'
condR = df1.loc[:,'service'] == 'player2'
condT = ( df1.loc[:,'setscore1'] + df1.loc[:,'setscore2'] ) == 12
cond0 = (df1.loc[:,'setscore1'] == df1.loc[:,'setscore2'])
condP1 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == 1
condN1 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == -1
condP2 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == 2
condN2 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == -2
condP3 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == 3
condN3 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == -3
condP4 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == 4
condN4 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == -4
condP5 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == 5
condN5 = ( df1.loc[:,'setscore1'] - df1.loc[:,'setscore2'] ) == -5

cond = cond0 | (condS & condN1) | ( condR & condP1)
df1.loc[cond,'btw'] = 0

cond = (condS & condP1) | ( condR & condP2)
df1.loc[cond,'btw'] = 1

cond = (condR & condN2) | ( condS & condN3)
df1.loc[cond,'btw'] = -1

cond = (condS & condP2) | ( condR & condP3)
df1.loc[cond,'btw'] = 2

cond = (condR & condN3) | ( condS & condN4)
df1.loc[cond,'btw'] = -2

cond = (condS & condP3) | ( condR & condP4)
df1.loc[cond,'btw'] = 3

cond = (condR & condN4) | ( condS & condN5)
df1.loc[cond,'btw'] = -3



df1.loc[:,'stw'] = 



cond2 = 




round(-3.5)
round(-2.5)
round(-1.5)
round(-0.5)


prev_set = 0
prev_ptw = 8
df1.loc[df1.index[0],'game'] = 1
game = 0 
for index in df1.index[1:]: 
    
    act_set = df1.loc[index,'set']
    #print(prev_set, act_set)
    if act_set > prev_set:
       game = 0
       prev_set = act_set
    
    act_ptw = df1.loc[index,'ptw'] +df1.loc[index,'ptl']
    #print(prev_ptw, act_ptw)
    if act_ptw > prev_ptw:
        game += 1
    
    prev_ptw = act_ptw        
    
    df1.loc[index,'game'] = game   




# Grouping scores
df2 = df1.loc[ df1.loc[:,'scores'] != '0-0' , :]



# Score statistics
score_stats = df2.loc[:,('game1','game2')].groupby(['game1','game2']).count()


x = df.loc[:,'log']
y1 = df.loc[:,'odds1']
y2 = df.loc[:,'odds2']

plt.plot(x,y1)
plt.plot(x,y2)
#    for i in range(df.shape[0]):
#        goals += goal 
#        time  = temp.loc[:,'time_to_game'].iloc[i]
#        score = temp.loc[:,'new_score'].iloc[i]
#        plt.text(time, 0.0 + goals, str(score))



plt.show()



# Compute pie slices
plt.figure(figsize=(10,10))
N = 20
theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
radii = 10 * np.random.rand(N)
width = np.pi / 4 * np.random.rand(N)
colors = plt.cm.viridis(radii / 10.)

ax = plt.subplot(111, projection='polar')
ax.bar(theta, radii, width=width, bottom=0.0, color=colors, alpha=0.5)

plt.show()


#plt.figure(figsize=(30,15))
#
#graph_rows = int(np.ceil(games.count()/4))
#
#plt.subplot(graph_rows,4,1)
#j = 0
#for game in games: 
#    j +=1
#    cond1 = df.loc[:,'game'] == game
#    cond2 = df.loc[:,'time_to_game'] > 0
#
#    Y1 = df.loc[cond1 & cond2 ,'Win1']
#    Y2 = df.loc[cond1 & cond2,'Tie']
#    Y3 = df.loc[cond1 & cond2,'Win2']
#    X1 = df.loc[cond1 & cond2,'time_to_game']
#
#    plt.subplot(graph_rows,4,j)
#    plt.stackplot(X1,[Y1,Y2,Y3],labels=['Win1','Tie','Win2'])
#    
#    temp = df.loc[cond1 ,('time_to_game','new_score')].dropna()
#    goal = 0.90 / (temp.shape[0]+1)
#    goals = 0
#    for i in range(temp.shape[0]):
#        goals += goal 
#        time  = temp.loc[:,'time_to_game'].iloc[i]
#        score = temp.loc[:,'new_score'].iloc[i]
#        plt.text(time, 0.0 + goals, str(score))
#        
#    plt.xlim(0,110)
#    plt.ylim(0,1)      
#    
#    # Not ticks everywhere
#    if j not in range(1,40,4) :
#        plt.tick_params(labelleft='off')
#    if j not in range(graph_rows*4-4,graph_rows*4+1) :
#        plt.tick_params(labelbottom='off')
#
# 
#    plt.title(game, loc='left', fontsize=14, fontweight=2 )
#
#plt.legend(loc='lower right')
#plt.show()
