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

dfa = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx')
df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_methods.xlsx',index_col=0)
dfs = pd.read_excel(DATA_PATH + 'signal_definitions_methods.xlsx')

list_columns = []; list_terms = ['uit','uit_wapens','uit_steenkool','uit_tabak','uit_clustermunitie','eng','eng_pu','eng_pr','int','scr','bic','ps','ns','gb','ii']; 
list_terms_text = ['uit','eng','eng_pu','eng_pr','int','scr','bic','ps','ns','gb','ii']
for term in list_terms: #indicators to be calculated
    for year in df['dc:coverage'].unique():
        list_columns = list_columns + [term+'_'+str(year)]
for term in list_terms_text: #indicators for which text is shown
    for year in df['dc:coverage'].unique():
        list_columns = list_columns + [term+'_text_'+str(year)]
total_columns = ['naam','JV2016','JV2017','JV2018','JV2019','JV2020'] + list_columns

dfr = pd.DataFrame(columns=total_columns)
dfr['naam'] = dfa['Unnamed: 0']

#Presence documents
docs = ['JV2016','JV2017','JV2018','JV2019','JV2020']
for doc in docs:
    dfr[doc] = 1*(dfa[doc].isnull()==False)

dfr = dfr.set_index('naam')
for pf in df['dc:creator'].unique():
    for year in  df['dc:coverage'].unique():
        #Uitsluitingen
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].str.contains('uit'))])>0:
            dfr.loc[pf,'uit_' + str(year)] = 1
        if (len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="uit")])>0): 
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="uit")]
            for ind in range(0,len(temp.index)):
                if ind==0:
                    dfr.loc[pf,'uit_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'uit_text_'+str(year)] = dfr.loc[pf,'uit_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        #Public engagement
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pu')])>0:
            dfr.loc[pf,'eng_pu_' + str(year)] = 1
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="eng_pu")]
            for ind in range(0,len(temp.index)):
                if ('eng_pu_text_'+str(year) in dfr.columns)==False:
                #if ind==0:
                    dfr.loc[pf,'eng_pu_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'eng_pu_text_'+str(year)] = str(dfr.loc[pf,'eng_pu_text_'+str(year)]) + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        if (len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pu1')])>0)&(len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pu2')])>0):
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].isin(['eng_pu1','eng_pu2']))]
            for sen in temp['dnb_nlp:sentence'].unique():
                if (len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='eng_pu1')])>0)&(len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='eng_pu2')])>0):
                    dfr.loc[pf,'eng_pu_' + str(year)] = 1
                    if ('eng_pu_text_'+str(year) in dfr.columns)==False:
                        dfr.loc[pf,'eng_pu_text_'+str(year)] = sen
                    else:
                        dfr.loc[pf,'eng_pu_text_'+str(year)] = str(dfr.loc[pf,'eng_pu_text_'+str(year)]) + "   +   " + sen
        #Private engagement
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr')])>0:
            dfr.loc[pf,'eng_pr_' + str(year)] = 1
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="eng_pr")]
            for ind in range(0,len(temp.index)):
                if ('eng_pr_text_'+str(year) in dfr.columns)==False:
                    dfr.loc[pf,'eng_pr_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'eng_pr_text_'+str(year)] = str(dfr.loc[pf,'eng_pr_text_'+str(year)]) + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        if (len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr1')])>0)&(len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr2')])>0):
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].isin(['eng_pr1','eng_pr2']))]
            for sen in temp['dnb_nlp:sentence'].unique():
                if (len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='eng_pr1')])>0)&(len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='eng_pr2')])>0):
                    dfr.loc[pf,'eng_pr_' + str(year)] = 1
                    if ('eng_pr_text_'+str(year) in dfr.columns)==False:
                        dfr.loc[pf,'eng_pr_text_'+str(year)] = sen
                    else:
                        dfr.loc[pf,'eng_pr_text_'+str(year)] = str(dfr.loc[pf,'eng_pr_text_'+str(year)]) + "   +   " + sen
        #ESG integration
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='int')])>0:
            dfr.loc[pf,'int_' + str(year)] = 1
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="int")]
            for ind in range(0,len(temp.index)):
                if ('int_text_'+str(year) in dfr.columns)==False:
                #if ind==0:
                    dfr.loc[pf,'int_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'int_text_'+str(year)] = str(dfr.loc[pf,'int_text_'+str(year)]) + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        if (len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='int1')])>0)&(len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='int2')])>0):
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].isin(['int1','int2']))]
            for sen in temp['dnb_nlp:sentence'].unique():
                if (len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='int1')])>0)&(len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='int2')])>0):
                    dfr.loc[pf,'int_' + str(year)] = 1
                    if ('int_text_'+str(year) in dfr.columns)==False:
                        dfr.loc[pf,'int_text_'+str(year)] = sen
                    else:
                        dfr.loc[pf,'int_text_'+str(year)] = str(dfr.loc[pf,'int_text_'+str(year)]) + "   +   " + sen
        #Screening
        screening_signals = ['bic','ps','ns']
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].isin(screening_signals))])>0:
            dfr.loc[pf,'scr_' + str(year)] = 1
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].isin(screening_signals))]
            for ind in range(0,len(temp.index)):
                if ind==0:
                    dfr.loc[pf,'scr_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'scr_text_'+str(year)] = str(dfr.loc[pf,'scr_text_'+str(year)]) + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']        

#Calculate measure based on results 
dft = pd.DataFrame()
methods=['uit','eng_pu','eng_pr','int','scr']
for pf in df['dc:creator'].unique():
    for year in  df['dc:coverage'].unique():
        count=0
        for met in methods:
            if dfr.loc[pf,met+'_'+str(year)]==1:
                count+=1
            dft.loc[pf,year] = count 
dft.to_excel(OUTPUT_DATA_PATH + 'variety_measure.xlsx') 
