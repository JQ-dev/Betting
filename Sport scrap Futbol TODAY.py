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



def open_urls():
    success = False
    wait = 5
    while success == False:
        success = True
        success_tries = 0
        
        try:
            driver = webdriver.Chrome()
            driver.get('https://www.oddsportal.com/matches/tennis/')   
            driver.find_element_by_id('user-header-timezone-expander').click()
            time.sleep(wait) 
            driver.find_element_by_partial_link_text('Eastern Time (US & Canada)').click() 
            #driver.find_element_by_id('main-next-games_7').click()
            #driver.find_element_by_link_text('Soccer').click()      
        
            df_tabs = pd.DataFrame()
            #tab_names
            for i in range(7):
                link = 'https://www.oddsportal.com/matches/tennis/' + str( int( time.strftime('%Y%m%d') )+i ) + '/'
                tab = 'tab_' + str(i)
                day = str( datetime.date.today() + datetime.timedelta(days=i) ).replace('-','')
                df0 = pd.DataFrame( data = {'link': [link], 'tab': [tab], 'game_day' : [day] } )
                df_tabs = df_tabs.append(df0)
            df_tabs = df_tabs.reset_index(drop=True)
        
            #open tabs
            tabs = 0
            for index in df_tabs.index:
                try:
                    script = "window.open('about:blank', '" + df_tabs.loc[index,'tab'] + "');"
                    driver.execute_script(script)
                    driver.switch_to.window(df_tabs.loc[index,'tab'])
                    driver.get(df_tabs.loc[index,'link'])
                    tabs += 1
                except:
                    continue
            
            success_tries += 1
            if tabs == 7 :
                success = True
            elif (tabs > 0) and (success_tries > 2):
                print('I wasn\'t allowed to open 7 windows. I"ll try with the',str(tabs),' tabs avaibable.' )
                success = True
                
            else:
                success = False
                driver.close()
                print('I wasn\'t allowed to open de windows properly. I"ll try again in one minute.' )
                success_tries = 0
                time.sleep(60)
                
        except:
            success = False
            driver.close()
            wait *= 2
            wait = max(wait,30)
            print('I wasn\'t allowed to open de windows properly. I"ll try again in one minute.' )
            time.sleep(60)
    
    return driver, df_tabs




def scrap_once(driver, df_tabs):
    
    df2 = pd.DataFrame()
    
    # index = 6
    for index in df_tabs.index:
        
        driver.switch_to.window(df_tabs.loc[index,'tab'])   
    
        count = 0
        df1 = pd.DataFrame()
        while df1.shape[0] == 0 or count > 5: 
            count += 1
            soup = BeautifulSoup(driver.page_source, 'html.parser')    
            big_box = soup.find_all('tr', attrs={'class': re.compile('^odd') })
            #small_box = soup.find('tr', attrs={'class': re.compile('^odd') })
            #A = small_box.prettify()
            for small_box in big_box:
                odds_dict = {}
                try:
                    odds_dict['game_time'] = small_box.find('td', attrs={'class': re.compile('^table-time datet') }).text.strip()
                except:
                    odds_dict['game_time'] = 'N/D'     
    #            try:            
    #                odds_dict['url'] = small_box.find('td', attrs={'class': 'name table-participant' }).find('a')['href']
    #            except:
    #                odds_dict['url'] = 'N/D'     
                try:            
                    odds_dict['teams'] = small_box.find('td', attrs={'class': 'name table-participant' }).text.strip()
                except:
                    odds_dict['teams'] = 'N/D'     
                try:            
                    odds_dict['score'] = small_box.find('td', attrs={'class': 'center bold table-odds table-score' }).text.strip()
                except:
                    odds_dict['score'] = 'N/D'     
                       
                odds = small_box.find_all('td', attrs={'class': 'odds-nowrp' })
                count = 0
                reg_odds = ['Win1','Tie','Win2']
                for odd in odds:
                    try:  
                        odds_dict[reg_odds[count]] = odd.text.strip()
                    except:
                        odds_dict[reg_odds[count]] = 'N/D'
                    count += 1
                try:   
                    odds_dict['odds_base'] = small_box.find('td', attrs={'class': 'center info-value' }).text.strip()
                except:
                    odds_dict['odds_base'] = 'N/D'
                    
                df1 = df1.append ( pd.DataFrame.from_dict(odds_dict,orient='index').T ) 
            
                not_empty = df1.loc[:,'teams'] != 'N/D'    
                df1 = df1.loc[not_empty,:]    
                                
            df1['log'] = time.strftime("%Y-%m-%d %H:%M:%S") 
            df1['day_game'] = df_tabs.loc[index,'game_day']
        
        df2 = df2.append(df1) 
    return df2



def combine_df(df_base,df_new):
    df_base = df_base.append(df_new)
    cols = df_base.columns.to_list()
    cols.remove('log')
    cols.remove('odds_base') 
    df_base = df_base.drop_duplicates(subset=cols, keep='first', inplace=False)
    return df_base
    
    
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
    
    
file_name = 'Football_odds'
driver, df_tabs = open_urls()
df_base = pd.DataFrame()
today = datetime.date.today()
count = 0
consec  = 0
while True:
    count += 1
    try:
        df_new = scrap_once(driver, df_tabs)    
    except:
        driver, df_tabs = open_urls()
        df_new = scrap_once(driver, df_tabs) 
        
    df_base = combine_df(df_base,df_new)    
    
    right_now = datetime.date.today()
    
    if right_now != today:
        today = right_now
        driver.quit()
        driver, df_tabs = open_urls()  

    print('Today is: ',today, 'iteration: ',count)
    #print('Right now is: ', right_now)
    
    df_base.to_csv(  file_name + '.csv'  ,sep=',',na_rep='N/D',index=False) 
     
    if count%200 == 0:
        consec += 1
        df_base.to_csv( file_name + str(consec) +'.csv',sep=',',na_rep='N/D',index=False)   



    
    

###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################

#
#total_odds = pd.DataFrame(columns=['booker', 'result1', 'result2', 'result3',
#                                     'dev_rst1', 'dev_rst2', 'dev_rst3', 'url',
#                                     'score', 'game_time', 'log', 'name_team1',
#                                     'name_team2', 'In-Play', 'arb'])
#
#url = 'https://www.oddsportal.com/matches/soccer/'
#
#total_odds = scrap_oddsportal_INGAME(total_odds,url) 











 







 