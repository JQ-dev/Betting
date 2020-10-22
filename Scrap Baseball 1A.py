# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 08:51:35 2019

BETS PROJECT !!!
SCRAPING BETS ONLINE
@author: admin
"""


from bs4 import BeautifulSoup 
import pandas as pd
from selenium import webdriver
import time
import requests
import re



total_odds = pd.DataFrame(columns=['log','booker','team1','team2','url','game_teams','game_time'])

def scrap_oddsportal_MBL(total_odds):
    url = 'https://www.oddsportal.com/baseball/usa/mlb/'
    driver = webdriver.Chrome()
    driver.get(url)                     
    soup = BeautifulSoup(driver.page_source, 'html.parser')    
    big_box = soup.find_all('a', attrs={'href': re.compile('^/baseball/usa/mlb/') })
    urls = []
    for WW in big_box:
        if len(WW['href']) < 40:
            continue
        else:
            urls.append( 'https://www.oddsportal.com' + WW['href'] )
    df = pd.DataFrame(columns=['urls'])
    df['urls'] = urls
    for url in df['urls']:
        driver.get(url)
        soupX = BeautifulSoup(driver.page_source, 'html.parser')
        game_teams = soupX.find('title').text.strip()        
        game_time = soupX.find('p', attrs={'class': re.compile('^date datet ') } ).text.strip()
        odds = pd.DataFrame(columns=['booker','team1','team2'])
        # box 1 contains the table with the odds from different bookers
        box1 = soupX.find_all('tr', attrs={'class': re.compile('^lo ') } )
        i,j = 0,1
        for box2 in box1:
            #print( box2.find('a', attrs={'class': 'name' }).text.strip()   )
            odds.loc[i,'booker'] = box2.find('a', attrs={'class': 'name' }).text.strip()
            #box 3 contains the two odds 
            box3 = box2.find_all('td', attrs={'class': re.compile('^right odds') } )
            for odd in box3:
                #print( odd.text.strip() )
                odds.iloc[i,j] = odd.text.strip()
                j += 1    
            i += 1
            j = 1
        max1 = odds['team1'].max()
        max2 = odds['team2'].max()
        odds = odds.append({'booker' : 'best deal' , 'team1' : max1 , 'team2' : max2 } , ignore_index=True)  
        odds['url'] = url
        odds['game_teams'] = game_teams
        odds['game_time'] = game_time
        odds['log'] = time.strftime("%m/%d/%y %I:%M %p") 
        total_odds = total_odds.append(odds)  
    driver.quit()   
    return total_odds
    


###################################################################################################################
    

total_odds = pd.DataFrame(columns=['log','booker','team1','team2','url','game_teams','game_time'])

while True:
    try:
        prev_data = pd.read_csv('Odds_Baseball.csv')
        total_odds = scrap_oddsportal_MBL(prev_data)         
        total_odds.to_csv('Odds_Baseball.csv',sep=',',na_rep='N/D',index=False)        
        time.sleep(60*5)
        
    except:
        
        try:
            prev_data = pd.read_csv('Odds_Baseball_temp.csv')
            total_odds = scrap_oddsportal_MBL(prev_data)     
            total_odds.to_csv('Odds_Baseball_temp.csv',sep=',',na_rep='N/D',index=False)
            time.sleep(60*5)           
        
        except:
            prev_data = total_odds.copy()
            total_odds =  scrap_oddsportal_MBL(prev_data)  
            total_odds.to_csv('Odds_Baseball_temp.csv',sep=',',na_rep='N/D',index=False)
            time.sleep(60*5)
    




 