# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 11:32:07 2019

@author: admin
"""

# pip install beautifulsoup4
# pip install requests
# pip install selenium

from bs4 import BeautifulSoup
#import requests   
from selenium import webdriver
import pandas as pd  
from datetime import datetime
import time
import numpy as np
import re
import sys


def a_to_d(odd):
    if 'even' in odd.lower():
        clean_odd = 2    
    elif '-' in odd:
        clean_odd = odd.replace('-','')
        clean_odd = (int(clean_odd)+100) / int(clean_odd)
    elif '+' in odd:
        clean_odd = odd.replace('\+','')
        clean_odd = 1 + int(clean_odd) / 100 
    else:
        return np.nan
    
    clean_odd = round(1/ clean_odd,2)
    #clean_odd = round(clean_odd,2)
    return clean_odd



def open_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5) 
    return driver        


def read_site(driver):
    
    odds_table = pd.DataFrame()    

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Bets                                   
    container1 = soup.find("div", {"class": "ui-widget-content-body shown market-board-group-content target"})
    # Score
    container2 = soup.find("div", {"class": "gameTemplate"})

    players = container2.find_all("span", {"class": "participantName name"})
    player = container2.find("span", {"class": "participantName name"})
    names = []
    for player in players:
        names.append( player.text.strip() )

    set_serve = container2.find('div', {'class': "setGameCol rightAlign"}).find_all('span', attrs={'class': re.compile('^serve') })  
    serve = []
    for order in set_serve:
        serve.append (order['class']) 
        
    score1_game = container2.find('span', {'ng-bind': "vm.event.scoreboard.client.score.points.player1"}).text.strip()
    score2_game = container2.find('span', {'ng-bind': "vm.event.scoreboard.client.score.points.player2"}).text.strip()  
    
    
    the_sets = container2.find_all('div', {'ng-repeat': 'set in vm.event.scoreboard.client.score.sets track by set.title'})

    score_sets = []
    for each_set in the_sets:
        player1 = each_set.find('span', {'ng-bind': 'set.player1'}).text.strip()
        player2 = each_set.find('span', {'ng-bind': 'set.player2'}).text.strip()
        score_sets.append( [player1,player2]  )

    bet_options = {}
    
    bets = container1.find_all('div', {'class' : 'markets'})

    for bet in bets:
        X = bet.find('div', {'class' : 'title'}).text.strip()
        bet_options[X] = []
        temp_odds = []
        for odds in bet.find_all('span', {'class' : 'value'}):
            temp_odds.append( odds.text.strip() )
        bet_options[X] = temp_odds
            
            
    # ALL TOGETHER
    odds_table.loc[0,'log'] = now
    
    odds_table.loc[0,'player1'] = names[0]
    odds_table.loc[0,'player2'] = names[1]
    
    try: 
        if serve[0][1] == 'on':
            odds_table.loc[0,'service'] = 'player1'
    except: 
        try:
            if serve[1][1] == 'on':
                odds_table.loc[0,'service'] = 'player2'
        except:
            odds_table.loc[0,'service'] = 'N/D'

    odds_table.loc[0,'game1'] = score1_game
    odds_table.loc[0,'game2'] = score2_game   
    
    str_score = ''
    for set_score in score_sets:
        str_score += str(set_score)
        
    odds_table.loc[0,'score'] = str_score.replace('\'','')
         
    odds_table.loc[0,'odds1'] = a_to_d(bet_options['Match Winner'][0])
    odds_table.loc[0,'odds2'] = a_to_d(bet_options['Match Winner'][1])

    return(odds_table)


def combine_df(df_base,df_new):
    df_base = df_base.append(df_new)
    cols = list(df_base.columns)
    cols.remove('log')
    df_base = df_base.drop_duplicates(subset=cols, keep='first', inplace=False)
    return df_base

Tennis_live = pd.DataFrame()


url = 'https://livebetting.bwin.com/en/live#/9040670'
file_name = 'Tennis_BWin_live3.csv'

time.sleep(60*12)

driver = open_url(url)

while True:
    count = 0
    try:
        odds_table = read_site(driver)
        Tennis_live = combine_df(Tennis_live,odds_table)  
        Tennis_live.to_csv(  file_name  ,sep=',',na_rep='N/D',index=False)
        count = 0
        time.sleep(5)
        print('ok')
    except:
        print ("Unexpected error:", sys.exc_info()[0] )
        count += 1
        if count > 360:
            driver.close()
            driver = open_url(url)  
        else:
            time.sleep(5)






  
    