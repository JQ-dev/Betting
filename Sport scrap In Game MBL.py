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
import datetime
import re
import numpy as np



def scrap_oddsportal_INGAME(total_odds,url):
    driver = webdriver.Chrome()

    driver.get('https://www.oddsportal.com/login/') 
    driver.find_element_by_id('login-username1').send_keys('quintero')
    driver.find_element_by_id ('login-password1').send_keys('Betting2020')
    driver.find_element_by_xpath('//*[@id="col-content"]/div[3]/div/form/div[3]/button/span/span').click()
    
    driver.get(url)                     
    soup = BeautifulSoup(driver.page_source, 'html.parser') 
    url2 = '^' + url.replace('https://www.oddsportal.com','')
    
    big_box = soup.find_all('a', attrs={'href': re.compile(url2) })
    urls = []
    for WW in big_box:
        if len(WW['href']) < 40:
            continue
        else:
            urls.append( 'https://www.oddsportal.com' + WW['href'] )
                       
    df = pd.DataFrame(columns=['urls'])
    df['urls'] = urls
    
    df = df[df.urls != url]
    df = df[df.urls != (url + 'outrights/' ) ]
    df = df[df.urls != (url + 'results/'   ) ]
    df = df[df.urls != (url + 'standings/' ) ]    
    
    
    for each_url in df['urls']:
        if 'inplay-odds' in each_url:
            to_remove = each_url.replace('inplay-odds/','')
            df[df.urls == to_remove] = each_url
    
    df = df.drop_duplicates()
    
    
    #tab_names
    for index in df.index:
        df.loc[index,'tab'] = 'tab_' + str(index)
    

    #open tabs
    for index in df.index:
        script = "window.open('about:blank', '" + df.loc[index,'tab'] + "');"
        driver.execute_script(script)
        driver.switch_to.window(df.loc[index,'tab'])
        driver.get(df.loc[index,'urls'])
  
        
#    while game is still playing reapeat every minute...

    while df.shape[0] > 0:
        
        print(df.shape[0],' games to watch so far...')
        
        for index in df.index:
    #index = 5            
            try:
                
                driver.switch_to.window(df.loc[index,'tab'])
                
                soupX = BeautifulSoup(driver.page_source, 'html.parser')
                
                info = soupX.find('div', attrs={'id': 'breadcrumb' }).text.strip()   
                game_teams = info.replace('You are here\nHome','').replace('\t','').replace('\n','').split(sep='»')[-1]
                
                game_time = soupX.find('p', attrs={'class': re.compile('^date datet ') } ).text.strip()
                try:
                    #live_score = soupX.find('span', attrs={'class': 'live-score' } ).text.strip() 
                    live_score = soupX.find('p', attrs={'class': 'result-live' } ).text.strip() 
                except:
                    live_score = 'N/D'
                odds = pd.DataFrame(columns=['booker','result1','result2','result3'])
    
                box1 = soupX.find_all('tr', attrs={'class': re.compile('^lo ') } )
                  
                i,j = 0,1
                
                
                for box2 in box1:
                    try:
                        #print( box2.find('a', attrs={'class': 'name' }).text.strip()   )
                        odds.loc[i,'booker'] = box2.find('a', attrs={'class': 'name' }).text.strip()
                    except:
                        odds.loc[i,'booker'] = np.nan
                    #box 3 contains the two odds 
                    box3 = box2.find_all('td', attrs={'class': re.compile('^right odds') } )
                    # box3 = box2.find('td', attrs={'class': re.compile('^right odds') } )
                    # B =  box3.prettify()
                    for odd in box3:
                        #print( odd.text.strip() )
                        try:
                            if 'deactivateOdd' in odd.find('div')['class']:
                                odds.iloc[i,j] = np.nan
                        except:
                            try:
                                odds.iloc[i,j] = odd.text.strip()
                            except:
                                odds.iloc[i,j] = np.nan
                        j += 1    
                    i += 1
                    j = 1
        
                #odds = odds.dropna(subset=['result1','result2','result3'])
                odds = odds.dropna(subset=['booker'])                 
                
                odds = odds.replace('',1)
        
                odds.loc[:,('result1','result2','result3')] = odds.loc[:,('result1','result2','result3')].astype(float)

                max1 = odds['result1'].max()
                max2 = odds['result2'].max()
                max3 = odds['result3'].max()
                
                odds = odds.append({'booker':'best deal','result1':max1,'result2':max2,'result3':max3} , ignore_index=True)
                                   
                
                odds.loc[:,('result1','result2','result3')] = odds.loc[:,('result1','result2','result3')].astype(float)
                
                odds['url'] = url
                odds['score'] = live_score
                odds['game_teams'] = game_teams
                odds['game_time'] = game_time
                odds['log'] = time.strftime("%Y-%m-%d %H:%M:%S") 
                
                try:
                    odds[['day','date','time']] = odds.loc[:,"game_time"].str.split(',', n = 3, expand = True) 
                except:
                    odds['day'] = 'Never'
                    odds['date'] = '31 Dec 2100'
                    odds['time'] = '12:00'
                    
                    
                
                odds.loc[:,'game_time'] = pd.to_datetime(odds.loc[:,'date'] + odds.loc[:,'time'])
                odds = odds.drop(['day','date','time'],axis=1)
                
                
                odds["game_teams"] = odds["game_teams"].replace('In-Play','In Play',regex=True)
                odds["game_teams"] = odds["game_teams"].replace(' - ',' XXX ',regex=True)
                
                if len ( odds.loc[0,"game_teams"].split(sep='XXX') ) == 3:
                    odds[['name_team1','name_team2','In-Play']] = odds["game_teams"].str.split('XXX', expand = True) 
                elif len ( odds.loc[0,"game_teams"].split(sep='XXX') ) == 2:
                    odds[['name_team1','name_team2']] = odds["game_teams"].str.split('XXX', expand = True) 
                    odds['In-Play'] = 'NO'
                else:
                    odds[['name_team1','name_team2']] = odds[['game_teams','game_teams']]
                    odds['In-Play'] = 'NO'
                odds = odds.drop(['game_teams'],axis=1)
                
                               
                #np.nansum( [ (1/odds['result1']) , (1/odds['result2']) , (1/odds['result3']) ] )
                
                
                try:
                    odds['arb'] = (1/odds['result1']).fillna(0)+(1/odds['result2']).fillna(0)+(1/odds['result3']).fillna(0)
                except:
                    odds['arb'] = 'N/D'
    
                
                game_live = (odds.loc[0,'game_time'] + datetime.timedelta(0,60*60) )
                start_recording = (odds.loc[0,'game_time'] - datetime.timedelta(0,60*5) )
                close_url = (odds.loc[0,'game_time'] - datetime.timedelta(0,60*60*4) )
                
                now = pd.to_datetime( odds.loc[0,'log'] )
                
                # Game too far away in the past to record the odds - Game will start in more than 4 hours
                if close_url > now:
                    print('Game droped (It won\'t start soon): ',odds.iloc[-1,8],'vs',odds.iloc[-1,9])
                    driver.close()
                    df = df.drop(index,axis=0)
                    del odds
                    continue  
                
                # Game already started and is not LIVE anymore
                elif (game_live < now) & (live_score == 'N/D') :
                    print('Game dropped (ended) : ',odds.iloc[-1,8],'vs',odds.iloc[-1,9])
                    driver.close()
                    df = df.drop(index,axis=0)
                    del odds
                    continue                  
                
                # Game close to start but not enough...so ignore "LIVE" until 5 min before the game start
                elif start_recording > now :
                    print('Game not live (It will start soon): ',odds.iloc[-1,8],'vs',odds.iloc[-1,9])
                    total_odds = total_odds.append(odds) 
                    total_odds.to_csv("MBL_total_odds.csv",sep=',',na_rep='N/D',index=False)                                         
                    #odds = odds.iloc[0:0]                                  
                
                else: 
                    total_odds = total_odds.append(odds) 
                    total_odds.to_csv("MBL_total_odds.csv",sep=',',na_rep='N/D',index=False)  
                    
                    
                    if soupX.find('span', attrs={'class': 'active' }).text.strip() == 'PRE-MATCH ODDS':
                        df.loc[index,'urls'] = ('https://www.oddsportal.com' + soupX.find('span', attrs={'class': 'inactive' }).find('a')['href'] )
                        driver.get( df.loc[index,'urls'] )       
        
    
    
                print('Game: ',odds.iloc[-1,8],' vs ',odds.iloc[-1,9], odds.iloc[-1,5])
                print('Arbitrage: ',odds.iloc[-1,-1],
                      'Best odds: ',odds.iloc[-1,1],' ',odds.iloc[-1,2],' ',odds.iloc[-1,3] )       
                print('') 
            
            except:
                  
                try:
                    driver.switch_to.window(df.loc[index,'tab'])
                    # Change to IN PLAY URL
                    soupX = BeautifulSoup(driver.page_source, 'html.parser')
#                    if soupX.find('span', attrs={'class': 'active' }).text.strip() == 'PRE-MATCH ODDS':
#                        df.loc[index,'urls'] = ('https://www.oddsportal.com' + soupX.find('span', attrs={'class': 'inactive' }).find('a')['href'] )
#                        driver.get( df.loc[index,'urls'] )
#                    continue
                    
                except:
                    script = "window.open('about:blank', '" + df.loc[index,'tab'] + "');"
                    driver.execute_script(script)
                    driver.switch_to.window(df.loc[index,'tab'])
                    driver.get(df.loc[index,'urls'])
                    print('Something happened')
                    
            

        time.sleep(60)            
          
            
    return total_odds
  
   




###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


total_odds = pd.DataFrame(columns=['booker', 'result1', 'result2', 'result3',
                                     'dev_rst1', 'dev_rst2', 'dev_rst3', 'url',
                                     'score', 'game_time', 'log', 'name_team1',
                                     'name_team2', 'In-Play', 'arb'])

url = 'https://www.oddsportal.com/baseball/usa/mlb/'

total_odds = scrap_oddsportal_INGAME(total_odds,url) 











 