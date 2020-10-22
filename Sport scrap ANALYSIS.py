"""
Created on Thu Aug  8 08:51:35 2019

BETS PROJECT !!!
SCRAPING BETS ONLINE
@author: admin
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


pd.options.mode.chained_assignment = None    
    
def get_results(filepath1):
    clean_bets = pd.read_csv(filepath1,sep=',')
    
    clean_bets['result1'] = clean_bets['result1'].replace('N/D',1).apply(float)
    clean_bets['result2'] = clean_bets['result2'].replace('N/D',1).apply(float)
    clean_bets['result3'] = clean_bets['result3'].replace('N/D',1).apply(float)
    
    clean_bets = clean_bets.drop(['dev_rst1','dev_rst2','dev_rst3'],axis=1) 

    clean_bets = clean_bets.dropna(subset=['arb']) 
    clean_bets = clean_bets.loc[ clean_bets.loc[:,'arb'] != 0 ,:]
    
    cond = clean_bets.loc[:,'booker'] == 'best deal'
    best = clean_bets.loc[cond,:]
    del cond
    

    best.loc[:,'game_time'] = pd.to_datetime( best.loc[:,'game_time'] )
    best.loc[:,'log']       = pd.to_datetime( best.loc[:,'log'] )
    
    best = best.drop_duplicates('name_team1',keep='last')    

#    last_arb = best.loc[:,'log'].max()
#    
#    clean_bets.loc[:,'log']       = pd.to_datetime( clean_bets.loc[:,'log'] )    
#    cond = ( clean_bets.loc[:,'log'] >= last_arb )
#    last_clean_bets = clean_bets.loc[cond,:]    

#    del cond, last_arb

    last_clean_bets = clean_bets.copy()
    last_clean_bets['unique'] = clean_bets['name_team1']+clean_bets['name_team2']+clean_bets['booker']
    last_clean_bets = last_clean_bets.drop_duplicates('unique',keep='last')    
    
#    last_clean_bets = clean_bets.loc[cond,:]    

    interesting = (best['arb'] < 0.99) 
    interesting.sum()

    int_results = best.loc[interesting,:]
    int_results = int_results.reset_index(drop=True)
    int_results['booker_R1'] = ''
    int_results['booker_R2'] = ''
    int_results['booker_R3'] = ''
    
    if int_results.shape[0] == 0:
        #print('there weren\'t arbitrage opportuities this time')
        final_result = []
        return clean_bets,final_result

    #i = 0 
    for i in range( int_results.shape[0] ) :
        
        cond1 = ( last_clean_bets['url'] == int_results.loc[:,'url'].iloc[i] )
        cond3 = (last_clean_bets['booker'] != 'best deal')
        
        cond4 = (last_clean_bets['result1'] == int_results.loc[:,'result1'].iloc[i])   
        int_results.loc[i,'booker_R1'] = last_clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')
    
        cond4 = (last_clean_bets['result2'] == int_results.loc[:,'result2'].iloc[i]) 
        int_results.loc[i,'booker_R2'] = last_clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')
    
        cond4 = last_clean_bets['result3'] == int_results.loc[:,'result3'].iloc[i]    
        int_results.loc[i,'booker_R3'] = last_clean_bets.loc[cond1 & cond1 & cond3 & cond4,'booker'].str.cat(sep='-')
    
    #last_clean_bets.loc[cond1 & cond3 & cond4,'booker'].values
    
    
    del cond1, cond3, cond4, i, interesting

    
    final_result = int_results.loc[:,('name_team1','name_team2','score','arb',
                                      'log','booker_R1','result1',
                                      'booker_R2','result2',
                                      'booker_R3','result3',
                                      'url')]
    
    return (clean_bets,final_result)



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


filepath1 = 'DENMARK_Futbol_total_odds.csv'


r2,r1 = get_results(filepath1)

playground = r2.copy()

del r1, r2, filepath1



playground['game'] = playground['name_team1'] + ' vs ' + playground['name_team2']
playground['game'] = playground['game'].str.strip()

playground['time_to_game'] = pd.to_datetime(playground['log']) - pd.to_datetime(playground['game_time'])

playground['time_to_game'] = playground['time_to_game'].apply(lambda x: round(x / np.timedelta64(60, 's') ))

playground = playground.drop(['log','game_time','url','arb','name_team1','name_team2','In-Play'],axis=1)

playground['score'] = (playground['score']  .replace('N/D','',regex=True)       
                                            .replace('Live','1\' 0:0',regex=True)
                                            .replace('\(','',regex=True)
                                            .replace('\)','',regex=True)
                                            .replace('Pause','PS',regex=True)
                                            .replace('Half-time','HT',regex=True)
                                            .replace('After Penalties','AP',regex=True)
                                            .replace('Finished','XX',regex=True)
                                            .replace('Penalties','XX',regex=True)
                                            .replace('\'','',regex=True) )
                                            
playground[['real_time','score','part_scores']] = playground['score'].str.split(pat=' ', n = 2, expand = True)


playground = playground.loc[ (playground.loc[:,'booker'] != 'best deal') ,: ]




# Time to game adjustment

games = playground['game'].drop_duplicates()

for game in games:
    
    test = playground.loc[playground.loc[:,'game'] == game , :].copy()
    
    min_15 = test.loc[ test.loc[:,'real_time'] == '15' ,'time_to_game'].mean()
    min_16 = test.loc[ test.loc[:,'real_time'] == '16' ,'time_to_game'].mean()
    

    if  min_15 is not np.nan:
        test.loc[ test.loc[:,'score'].notnull() ,'time_to_game'] += (15 - min_15)
    elif min_16 is not np.nan:
        test.loc[ test.loc[:,'score'].notnull() ,'time_to_game'] += (16 - min_16)
        
    test.loc[ ( (test.loc[:,'score'].isna()) & (test.loc[:,'time_to_game'] > 0) ) ,'time_to_game'] = 0
    
    playground.loc[playground.loc[:,'game'] == game , :] = test.copy()


del game, min_15, min_16, test


playground  = playground.loc[playground.loc[:,'real_time'] != 'XX' , :] 



# Selecting the median ODDS

df = ( playground   .groupby ( by=['game','time_to_game'])
                    .agg({'result1':'median', 'result2':'median', 'result3':'median', 
                          'score':'first','real_time':'first'})
                        [['result1','result2','result3','score','real_time']] 
                    .reset_index() )

# Goal difference
df[['s1','s2']] =  df.loc[:,'score'].str.split(pat=':',expand=True)

df[['s1','s2']] = df[['s1','s2']].astype(float)
    
df['dif'] = df.loc[:,'s1'] - df.loc[:,'s2']

df['goals'] = df.loc[:,'s1'] + df.loc[:,'s2']

df = df.drop(['s1','s2'],axis=1)



# Change in score

df.loc[:,'score'] = df.loc[:,'score'].fillna('0:0')

df.loc[:,'new_score'] = np.nan

for game in games:
    
    test = df.loc[df.loc[:,'game'] == game , :].copy()
    
    test['new_score'] = test.score.eq(test.score.shift())
    
    test['new_score'] = test['score'].where(test['new_score'] == False, np.nan)
    
    df.loc[df.loc[:,'game'] == game , 'new_score'] = test['new_score']


df['new_score'] = df['new_score'].replace('0:0',np.nan)

del game, test




# From Results to probabilities


df['arb']  = 1 / df.loc[: , 'result1'] + 1 / df.loc[: ,'result2'] + 1 / df.loc[:  ,'result3']
df['Win1'] = 1 / df.loc[ : ,'result1'] / df['arb'] 
df['Tie']  = 1 / df.loc[ : ,'result2'] / df['arb'] 
df['Win2'] = 1 / df.loc[ : ,'result3'] / df['arb'] 

df = df.drop(['result1','result2','result3','arb'],axis=1)


game = games.iloc[2]

plt.figure(figsize=(20,15))
plt.subplot(3,2,1)
j = 0
for game in games:
    
    j +=1
    cond1 = df.loc[:,'game'] == game
    cond2 = df.loc[:,'time_to_game'] > 0
    
    temp = df.loc[cond1 ,('time_to_game','new_score')].dropna()
    
    goal = 0.90 / (temp.shape[0]+1)
    goals = 0
    for i in range(temp.shape[0]):
        goals += goal 
        time  = temp.loc[:,'time_to_game'].iloc[i]
        score = temp.loc[:,'new_score'].iloc[i]
        plt.text(time, 0.0 + goals, str(score))

    Y1 = df.loc[cond1 & cond2 ,'Win1']
    Y2 = df.loc[cond1 & cond2,'Tie']
    Y3 = df.loc[cond1 & cond2,'Win2']
    X1 = df.loc[cond1 & cond2,'time_to_game']

    plt.subplot(3,2,j)
    plt.stackplot(X1,[Y1,Y2,Y3],labels=['Win1','Tie','Win2'])
    plt.xlim(0,110)
    plt.ylim(0,1)      
    
    # Not ticks everywhere
    if j in range(4) :
        plt.tick_params(labelbottom='off')
    if j not in [1,3,5] :
        plt.tick_params(labelleft='off')
 
    # Add title
    plt.title(game, loc='left', fontsize=14, fontweight=2 )


plt.legend(loc='lower right')
plt.show()

del X1,Y1,Y2,Y3,cond1,cond2,game,j, goals, goal


#variance = [1, 2, 4, 8, 16, 32, 64, 128, 256]
#bias_squared = [256, 128, 64, 32, 16, 8, 4, 2, 1]
#total_error = [x + y for x, y in zip(variance, bias_squared)]
#xs = [i for i, _ in enumerate(variance)]
## we can make multiple calls to plt.plot
## to show multiple series on the same chart
#plt.plot(xs, variance, 'g-', label='variance') # green solid line
#plt.plot(xs, bias_squared, 'r-.', label='bias^2') # red dot-dashed line
#plt.plot(xs, total_error, 'b:', label='total error') # blue dotted line
## because we've assigned labels to each series
## we can get a legend for free
## loc=9 means "top center"
#plt.legend(loc=9)
#plt.xlabel("model complexity")
#plt.title("The Bias-Variance Tradeoff")
#plt.show()
#
#
#
#





 