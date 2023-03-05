import pandas as pd
import nafigator
import ast
import os
from os.path import join
from typing import Union
from dnbnlp_genfun import dnbnlp_utils as dnu
from dnbnlp_genfun import find_signals
import time
import stanza

DATA_PATH = join('data','input','')
OUTPUT_DATA_PATH = join('data','output','')
STANZA_DATA_PATH = join('data','naf_files','')

start_time = time.time()

#Import sentences
df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_mvb_big_prediction.xlsx',index_col=0)
df = df[df.prediction==1]

#Import asset categories
dfc = pd.read_excel(DATA_PATH + 'signal_definitions_categories.xlsx',index_col=0)

def list_to_string(words):
    words_string = words[0]
    if len(words)>1:
        for word in words[1:]:
            words_string = words_string + "|" + word
    return words_string

words_neg = 'niet|geen|uitgesloten'

cats = ['aandelen','vastrentende waarden','staatsobligaties','bedrijfsobligaties','vastgoed', 'infrastructuur', 'private equity','hypotheken'] 
years = [2016,2017,2018,2019,2020,2021]


dfr = pd.DataFrame()
for cat in dfc.index.unique():
    words = eval(dfc.loc[cat,'synoniemen'])
    words_string = list_to_string(words)
    words_lists = eval(dfc.loc[cat,'synoniemen_combi'])
    for pf in df['dc:creator'].unique():
        for year in years:
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)]
            tempf = temp[temp['dnb_nlp:sentence'].str.contains(words_string,case=False)] #filter sentences with category in sentence
            if len(words_lists)>1:
                for listcombi in words_lists:
                    extra = temp[(temp['dnb_nlp:sentence'].str.contains(listcombi[0],case=False))&(temp['dnb_nlp:sentence'].str.contains(listcombi[1],case=False))] #filter sentences with category in sentence
                    if len(extra)>0:
                        tempf = tempf.append(extra)
            tempf = tempf[(tempf['dnb_nlp:sentence'].str.count(' . ')<3)&(tempf['dnb_nlp:sentence'].str.count(r'\d')<10)]#filter out very longe sentences and sentences with much numbers/headers
            if len(tempf)>0:
                dfr.loc[pf + '_' + str(year),cat] = 1
                dfr.loc[pf + '_' + str(year),cat + '_sentences'] = str(list(tempf['dnb_nlp:sentence']))               
            else:
                dfr.loc[pf + '_' + str(year),cat] = 0
dfr.fillna(0,inplace=True)

dfn = pd.DataFrame()
for pf in df['dc:creator'].unique():
    for year in df['dc:coverage'].unique():
        try:
            dfn.loc[pf,year] = dfr.loc[pf + '_' + str(year),cats].sum()
        except:
            dfn.loc[pf,year] = 0
dfn.to_excel(OUTPUT_DATA_PATH + 'scope_measure.xlsx')
