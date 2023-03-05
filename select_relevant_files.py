import click
import numpy as np
import pandas as pd
import os
from os.path import join
from os import walk
import nafigator
import nltk
from nltk.corpus import stopwords 
import warnings
warnings.filterwarnings("ignore")

DATA_PATH = join('data','input','')
DOWN_PATH = join('data','downloads','')
OUTPUT_DATA_PATH = join('data','output','')

dictt = {} 
dictt['JV2021'] = [['jaarverslag','2021'],['jaar rapport','2021'],['jaarrapport','2021'],['annual report','2021']]
dictt['JV2020'] = [['jaarverslag','2020'],['jaar rapport','2020'],['jaarrapport','2020'],['annual report','2020']]
dictt['JV2019'] = [['jaarverslag','2019'],['jaar rapport','2019'],['jaarrapport','2019'],['annual report','2019']]
dictt['JV2018'] = [['jaarverslag','2018'],['jaar rapport','2018'],['jaarrapport','2018'],['annual report','2018']]
dictt['JV2017'] = [['jaarverslag','2017'],['jaar rapport','2017'],['jaarrapport','2017'],['annual report','2017']]
dictt['JV2016'] = [['jaarverslag','2016'],['jaar rapport','2016'],['jaarrapport','2016'],['annual report','2016']]

try:
    dfc = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx',index_col=0)
    print('file with relevant files already present; add to existing file')
except:
    dfc = pd.DataFrame(columns=['final','duplicate']+list(dictt.keys()))
    print('file with relevant files not present --> create new file')
pf_final = list(dfc[dfc['final']=='x'].index.unique())

for pf in os.listdir(DOWN_PATH):
    if pf not in pf_final:
        dfc.loc[pf,:] = float("nan")
        folder = join(DOWN_PATH,pf,'')
        for file in os.listdir(folder):
            for term in dictt.keys():
                count = 0
                for sublist in dictt[term]:
                    if all(x in file.lower() for x in sublist):
                        count = 1
                if count == 1:
                    if pd.isna(dfc.loc[pf,term])==True:
                        dfc.loc[pf,term] = file
                    else:
                        dfc.loc[pf,term] = dfc.loc[pf,term] + " + " + file
                        dfc.loc[pf,'duplicate'] = 'yes'
    else:
        print(pf + " already final")

dfc.to_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx')
        






