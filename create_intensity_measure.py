import pandas as pd
import nafigator
import os
from os.path import join
from dnbnlp_genfun import dnbnlp_utils as dnu
from dnbnlp_genfun import find_signals
import time
import stanza

DATA_PATH = join('data','input','')
OUTPUT_DATA_PATH = join('data','output','')
STANZA_DATA_PATH = join('data','naf_files','')

start_time = time.time()

#Import catalog
df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog.xlsx',index_col=0)
#Import sentences
df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_mvb_big_prediction.xlsx',index_col=0)
df = df[df.prediction==1]

dfr = pd.DataFrame()
for pf in df_catalog['dc:creator'].unique():
    for year in df_catalog['dc:coverage'].unique():
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)])>0:
            file = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)]['naf:source'].iloc[0]
            try:
                naf = nafigator.NafDocument().open(file)
                print(file)
                nsen = len(naf.sentences)
                nrelsen = len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)])
                dfr.loc[pf,year] = nrelsen/nsen
            except:
                pass
        else:
            dfr.loc[pf,year] = 0

print("--- %s seconds ---" % (time.time() - start_time))

dfr.to_excel(OUTPUT_DATA_PATH + 'intensity_measure.xlsx')
