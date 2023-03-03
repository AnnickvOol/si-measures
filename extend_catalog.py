#Required environment: -

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

df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog_v2.xlsx',index_col=0)
df = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx',index_col=0).astype(str)

for row in df_catalog.index:
    pf = df_catalog.loc[row,'dc:creator']
    df_catalog.loc[row,'dc:number'] = df.loc[pf,'number']

df_catalog.to_excel(OUTPUT_DATA_PATH + 'df_catalog_v2.xlsx')

#OLD CODE

# list_docs = ['JV2019','JV2018','JV2017','JV2016']
# for doc in list_docs: 
#     for pf in df.index:
#         doc2 =df.loc[pf,doc].replace(".pdf","")
#         if os.path.exists(NAF_PATH+pf+'_'+doc2+'.naf.xml'):
#             naf = nafigator.NafDocument().open(NAF_PATH+pf+'_'+doc2+'.naf.xml')
#             lang = determine_language(naf.raw)
#             print(lang)
#             df_catalog = df_catalog.append(pd.DataFrame(columns = ['dc:identifier', 'dc:source', 'dc:relation','dc:creator','dc:format','dc:language','dc:type', 'dc:coverage', "naf:source", 'naf:status'], 
#                                                        data = [[pf + "_" + doc2, df.loc[pf,doc], "" , pf, '.pdf',lang, doc, doc[2:], NAF_PATH+pf+ "_"+doc2+'.naf.xml', 'OK']]), ignore_index=True)

# stopwords_en = stopwords.words('english')
# stopwords_nl = stopwords.words('dutch')
# stopwords_nl += ['rapport', 'notitie', 'bijlage', 'bijlagen', 'tabel', 'tabellen', 'rapportage', 'eindrapportage', 'pagina', 'figuur']
# stopwords_en += ['report', 'page', 'table']

# def determine_language(raw: str):
#     count_nl = 0
#     for stopword_nl in stopwords_nl:
#         regex = "\\s"+stopword_nl+"\\s"
#         count_nl += len(re.findall(regex, raw))
#     count_en = 0
#     for stopword_en in stopwords_en:
#         regex = "\\s"+stopword_en+"\\s"
#         count_en += len(re.findall(regex, raw))
#     if count_nl > count_en:
#         return "nl"
#     elif count_en >= count_nl:
#         return "en"