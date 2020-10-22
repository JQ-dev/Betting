# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 10:49:48 2019

@author: admin
"""

from bs4 import BeautifulSoup
#import requests   
from selenium import webdriver
import pandas as pd  
from datetime import datetime
import time
import numpy as np
import re
import sys




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
    containers1 = soup.find_all("div", {"class": "_2tNTa"})
    # Score
    container1 = soup.find("div", {"class": "_2tNTa"}).find("div", {"class": "_1ntak"}).text.strip()

    
    bet_T = pd.DataFrame()
    for container1 in containers1:
        
        title = container1.find("div", {"class": "_1ntak"}).text.strip()
        #print(title)
        bet_class = []
        bet_value = []
        count = 0
        for player in container1.find_all("span", {"class": "label"}):
            subtitle = player.text.strip()
            #print(subtitle)
            bet_class.append(title + ' : '  + subtitle)
            count +=1
        count = 0
        for player in container1.find_all("span", {"class": "price"}):    
            price    = player.text.strip()
            #print(price)
            bet_value.append(price)
            count +=1

        bet_T = bet_T.append(pd.DataFrame(bet_value,bet_class))
      
        
    bet_T['bet'] = bet_T.index    
    cond =  bet_T.loc[:,'bet'].apply(lambda x : 'Moneyline – Match : ' in x)
    bet_T = bet_T.loc[cond,:]
    cond =  bet_T.loc[:,'bet'].apply(lambda x : ('Set' not in x) and ('Game' not in x) )
    bet_T = bet_T.loc[cond,:]  
    bet_T.loc[:,'bet'] = bet_T.loc[:,'bet'] .replace('Moneyline – Match : ','',regex=True)\
                                            .replace('Moneyline – ','',regex=True)
    bet_T.index = bet_T.loc[:,'bet']
    bet_T = bet_T[[0]].T


    odds_table.loc[0,'log'] = now
    odds_table.loc[0,'player1'] = bet_T.columns[0]
    odds_table.loc[0,'player2'] = bet_T.columns[1]
    odds_table.loc[0,'odds1'] = round(1/  float(bet_T.iloc[0,0]) ,3)
    odds_table.loc[0,'odds2'] = round(1/  float(bet_T.iloc[0,1]) ,3)

    return(odds_table)



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


def combine_df(df_base,df_new):
    df_base = df_base.append(df_new)
    cols = list(df_base.columns)
    cols.remove('log')
    df_base = df_base.drop_duplicates(subset=cols, keep='first', inplace=False)
    return df_base



###################3
    

Tennis_live = pd.DataFrame()

url = 'https://www.pinnacle.com/en/tennis/atp-us-open-final/daniil-medvedev-vs-rafael-nadal/1032592851'


file_name = 'Tennis_Pinnacle_live2.csv'

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





