import pandas as pd
import nafigator
import ast
import os
from os.path import join
import sys
sys.path.append(os.getcwd())
from typing import Union
import find_signals
import dnbnlp_utils as dnu
import time
import stanza

stanza.download('nl')
nlp_nl = stanza.Pipeline(lang="nl", processors='tokenize,pos,lemma')
stanza.download('en')
nlp_en = stanza.Pipeline(lang="en", processors='tokenize,pos,lemma')
nlp = {'en': nlp_en, "nl": nlp_nl}

DATA_PATH = join('data','input','')
OUTPUT_DATA_PATH = join('data','output','')

start_time = time.time()

#Import catalog
df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog.xlsx',index_col=0)

#Select documents
docs = ['JV2016','JV2017','JV2018','JV2019','JV2020','JV2021']

#Import signals
df_signal_defs = pd.read_excel(DATA_PATH + "signal_definitions_mvb_big.xlsx")
#df_signal_defs = pd.read_excel(DATA_PATH + "signal_definitions_methods.xlsx")

df_catalog = df_catalog[df_catalog['dc:type'].isin(docs)]

# # necessary datatype conversion for dataiku (lists and dicts)
df_signal_defs['sig_def:aliases'] = df_signal_defs['sig_def:aliases'].apply(lambda x: ast.literal_eval(str(x)) if not pd.isna(x) else dict())
df_signal_defs['sig_def:case_sensitive'] = df_signal_defs['sig_def:case_sensitive'].apply(lambda x: ast.literal_eval(str(x)) if not pd.isna(x) else False)

# lemmatize and lowercase 
cols_to_adjust = ["sig_def:mandatory_terms","sig_def:avoid_terms", "sig_def:aliases"]
df_signal_defs = dnu.lemmatize_dataframe(df_signal_defs, nlp, cols_to_adjust)
df_signal_defs = dnu.lowercase_dataframe(df_signal_defs, cols_to_adjust)

#df_output = find_signals.search_naf_files_for_signals(df_catalog, df_signal_defs, params = {'print_progress':True,'add_context':True})
df_output = find_signals.search_naf_files_for_signals(df_catalog, df_signal_defs, params = {'print_progress':True, 'unpivot':True})

df_output.to_excel(OUTPUT_DATA_PATH + 'df_results_mvb_big.xlsx')
#df_output.to_excel(OUTPUT_DATA_PATH + 'df_results_methods.xlsx')

print("--- %s seconds ---" % (time.time() - start_time))
