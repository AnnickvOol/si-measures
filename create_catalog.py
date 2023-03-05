import numpy as np
import pandas as pd
import os
from os.path import join
from os import walk
import nafigator
import nltk
from nltk.corpus import stopwords 
import warnings
import re
warnings.filterwarnings("ignore")

DATA_PATH = join('data','input','')
DOWN_PATH = join('data','downloads','')
OUTPUT_DATA_PATH = join('data','output','')
NAF_PATH = join('data','naf_files','')

df = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx',index_col=0).astype(str)

try:
    df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog.xlsx',index_col=0)
    print('catalog already present')
except:
    df_catalog = pd.DataFrame(columns=['dc:identifier','dc:source','dc:creator','dc:format','dc:language','dc:type','dc:coverage','naf:status','dc:relation','naf:source','naf:status','dc:number','dc_language'])
    print('catalog not present --> create new file')

num=0
for row in df.index:
    pf = row
    for doc in ['JV2021','JV2020','JV2019','JV2018','JV2017','JV2016']:
        if df.loc[pf,doc]!='nan':
            df_catalog.loc[num,'dc:creator'] = pf
            df_catalog.loc[num,'dc:type'] = doc
            df_catalog.loc[num,'dc:source'] = df.loc[pf,doc]
            df_catalog.loc[num,'dc:identifier'] = pf + df.loc[pf,doc][:-4]
            df_catalog.loc[num,'dc:coverage'] = re.findall(r'\d\d\d\d',df.loc[pf,doc])[0]
            df_catalog.loc[num,'dc:format'] = df.loc[pf,doc][:-4]
            num=num+1

df_catalog.to_excel(OUTPUT_DATA_PATH + 'df_catalog.xlsx')

