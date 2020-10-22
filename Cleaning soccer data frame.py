# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 13:32:18 2019

@author: admin
"""

import pandas as pd

soccer01 = pd.read_csv('soccer.csv')

soccer01[['Team_1', 'Team_2']] = soccer01['teams'].str.split(',', expand=True)

soccer01[['R1', 'R2', 'R3']] = soccer01['odds'].str.split(',', expand=True)



soccer01 = soccer01.loc[ soccer01.loc[:,'odds'].notna() ,:]
soccer01 = soccer01.loc[ soccer01.iloc[:,0] != 'log_time' ,:]
soccer01 = soccer01.loc[ soccer01.loc[:,'log_time'] != 'N/D' ,:]

soccer01 = soccer01.drop(['odds'], axis = 1)


soccer01 = (soccer01.replace('\[','',regex=True).replace('\]','',regex=True)
            .replace('\)','',regex=True).replace('\(','',regex=True)
            .replace('\'','',regex=True).replace('EVEN','100',regex=True) 
            .replace('\+','',regex=True))

soccer01 = soccer01.rename(columns={"Unnamed: 0": "Log_ID"})

soccer01.loc[:,('R1','R2','R3')] = soccer01.loc[:,('R1','R2','R3')].astype(int)

cond = soccer01.loc[:,'R1'] > 0

soccer01['D1'] = soccer01.loc[:,'R1'].apply(lambda x: (x+100)/100 if x>0 else  (x-100)/x )
soccer01['D2'] = soccer01.loc[:,'R2'].apply(lambda x: (x+100)/100 if x>0 else  (x-100)/x )
soccer01['D3'] = soccer01.loc[:,'R3'].apply(lambda x: (x+100)/100 if x>0 else  (x-100)/x )

soccer01['P1'] = (1/soccer01.loc[:,'D1'])+(1/soccer01.loc[:,'D2'])+(1/soccer01.loc[:,'D3'])


games = soccer01.loc[:,'teams'].drop_duplicates()

to_print = soccer01.loc[soccer01.loc[:,'teams'] == 'Once Caldas, Alianza Petrolera',:]


