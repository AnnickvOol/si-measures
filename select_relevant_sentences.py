#Required environment: nlpold

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

stanza.download('nl')
nlp_nl = stanza.Pipeline(lang="nl", processors='tokenize,pos,lemma')
stanza.download('en')
nlp_en = stanza.Pipeline(lang="en", processors='tokenize,pos,lemma')
nlp = {'en': nlp_en, "nl": nlp_nl}

# import spacy
# nlp_en = spacy.load("en_core_web_sm")
# nlp_nl = spacy.load("nl_core_news_sm")
# nlp = {'en': nlp_en, "nl": nlp_nl}

DATA_PATH = join('data','input','')
OUTPUT_DATA_PATH = join('data','output','')

start_time = time.time()

# #Import catalog
# df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog_v2.xlsx',index_col=0)

# #Select documents
# #docs = ['MVR','MVB','BB']
# #docs = df_catalog['dc:type'].unique()
# docs = ['JV2016','JV2017','JV2018','JV2019','JV2020']
# #docs = ['JV2018','JV2019','JV2020']

# #Import signals
# df_signal_defs = pd.read_excel(DATA_PATH + "signal_definitions_mvb.xlsx")

# df_catalog = df_catalog[df_catalog['dc_type'].isin(docs)]
# df_catalog = df_catalog.iloc[:5,:]
# #df_catalog = df_catalog[(df_catalog['dc:type']=='JV2018')&((df_catalog['dc:creator']=='Detailhandel')|(df_catalog['dc:creator']=='Bakkersbedrijf BPF'))]

# # # necessary datatype conversion for dataiku (lists and dicts)
# df_signal_defs['sig_def_aliases'] = df_signal_defs['sig_def_aliases'].apply(lambda x: ast.literal_eval(str(x)) if not pd.isna(x) else dict())
# df_signal_defs['sig_def_case_sensitive'] = df_signal_defs['sig_def_case_sensitive'].apply(lambda x: ast.literal_eval(str(x)) if not pd.isna(x) else False)

# # lemmatize and lowercase 
# cols_to_adjust = ["sig_def_mandatory_terms","sig_def_avoid_terms", "sig_def_aliases"]
# #df_signal_defs = dnu.lemmatize_dataframe2(df_signal_defs, nlp, cols_to_adjust)
# df_signal_defs = dnu.SignalDataframeFormatter(signal_df=df_signal_defs,nlp_engine=nlp,use_case='research').lemmatize_dataframe(cols_to_adjust)
# df_signal_defs = dnu.SignalDataframeFormatter(signal_df=df_signal_defs,nlp_engine=nlp,use_case='research').lowercase_dataframe(cols_to_adjust)

# df_output = find_signals.SignalFinder(df_signal_defs=df_signal_defs,use_case='research',params = {'print_progress':True, 'unpivot':True},rw_sql=False).search_naf_files_for_signals(df_catalog)

# df_output.to_excel(OUTPUT_DATA_PATH + 'df_results_mvb.xlsx')

# print("--- %s seconds ---" % (time.time() - start_time))

#OLD CODE

#Import catalog
df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog_v2.xlsx',index_col=0)

#Select documents
#docs = ['VBB']
#docs = df_catalog['dc:type'].unique()
docs = ['JV2016','JV2017','JV2018','JV2019','JV2020','JV2021']
#pfs = ['ABP','Achmea','PGB']
#docs = ['JV2017']

#Import signals
#df_signal_defs = pd.read_excel(DATA_PATH + "signal_definitions_mvb_big.xlsx")
df_signal_defs = pd.read_excel(DATA_PATH + "signal_definitions_methods.xlsx")

df_catalog = df_catalog[df_catalog['dc:type'].isin(docs)]
#df_catalog = df_catalog[df_catalog['dc:creator'].isin(pfs)]
#df_catalog = df_catalog.iloc[:2,:]
#df_catalog = df_catalog[(df_catalog['dc:creator']=='PepsiCo Nederland')]

# # necessary datatype conversion for dataiku (lists and dicts)
df_signal_defs['sig_def:aliases'] = df_signal_defs['sig_def:aliases'].apply(lambda x: ast.literal_eval(str(x)) if not pd.isna(x) else dict())
df_signal_defs['sig_def:case_sensitive'] = df_signal_defs['sig_def:case_sensitive'].apply(lambda x: ast.literal_eval(str(x)) if not pd.isna(x) else False)

# lemmatize and lowercase 
cols_to_adjust = ["sig_def:mandatory_terms","sig_def:avoid_terms", "sig_def:aliases"]
df_signal_defs = dnu.lemmatize_dataframe(df_signal_defs, nlp, cols_to_adjust)
df_signal_defs = dnu.lowercase_dataframe(df_signal_defs, cols_to_adjust)

#df_output = find_signals.search_naf_files_for_signals(df_catalog, df_signal_defs, params = {'print_progress':True,'add_context':True})
df_output = find_signals.search_naf_files_for_signals(df_catalog, df_signal_defs, params = {'print_progress':True, 'unpivot':True})

df_output.to_excel(OUTPUT_DATA_PATH + 'df_results_methods.xlsx')

print("--- %s seconds ---" % (time.time() - start_time))


#df_signal_defs = dnu.SignalDataframeFormatter(signal_df=df_signal_defs,nlp_engine=nlp,use_case='research').lemmatize_dataframe(cols_to_adjust)
#df_signal_defs = dnu.SignalDataframeFormatter(signal_df=df_signal_defs,nlp_engine=nlp,use_case='research').lowercase_dataframe(cols_to_adjust)
#df_output = find_signals.SignalFinder(df_signal_defs=df_signal_defs,use_case='research',params = {'print_progress':True, 'unpivot':True},rw_sql=False).search_naf_files_for_signals(df_catalog)

# # select the relevant signals based on document type
#df_signal_defs = df_signal_defs[df_signal_defs['dc:type'].str.contains(DOC_TYPE, regex=False, case=False)]

#Only select pension funds that have all docs
#list_pf = []
#for pf in df_catalog['dc:creator'].unique():
#    temp = df_catalog[df_catalog['dc:creator']==pf]
    #if all(element in list(temp['dc:type']) for element in docs):
    #    list_pf = list_pf + [pf]
#df_catalog = df_catalog[(df_catalog['dc:creator'].isin(list_pf))&(df_catalog['dc:type'].isin(docs))]