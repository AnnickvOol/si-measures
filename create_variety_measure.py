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
warnings.filterwarnings("ignore")

DATA_PATH = join('data','input','')
DOWN_PATH = join('data','downloads','')
OUTPUT_DATA_PATH = join('data','output','')

dfa = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx')
df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_methods_complete.xlsx',index_col=0)
dfs = pd.read_excel(DATA_PATH + 'signal_definitions_methods.xlsx')

list_columns = []; list_terms = ['uit','uit_wapens','uit_steenkool','uit_tabak','uit_clustermunitie','eng','eng_pu','eng_pr','int','scr','bic','ps','ns','gb','ii']; 
list_terms_text = ['uit','eng','eng_pu','eng_pr','int','scr','bic','ps','ns','gb','ii']
for term in list_terms: #indicators to be calculated
    for year in df['dc:coverage'].unique():
        list_columns = list_columns + [term+'_'+str(year)]
for term in list_terms_text: #indicators for which text is shown
    for year in df['dc:coverage'].unique():
        list_columns = list_columns + [term+'_text_'+str(year)]
total_columns = ['naam','nummer','JV2016','JV2017','JV2018','JV2019','JV2020'] + list_columns

dfr = pd.DataFrame(columns=total_columns)
dfr['naam'] = dfa['Unnamed: 0']
dfr['nummer'] = dfa['number']

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
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].str.contains('uit_1'))])>0:
        #     dfr.loc[pf,'uit_wapens_' + str(year)] = 1
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].str.contains('uit_2'))])>0:
        #     dfr.loc[pf,'uit_steenkool_' + str(year)] = 1
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].str.contains('uit_3'))])>0:
        #     dfr.loc[pf,'uit_tabak_' + str(year)] = 1
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].str.contains('uit_4'))])>0:
        #     dfr.loc[pf,'uit_clustermunitie_' + str(year)] = 1
        if (len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="uit")])>0): 
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="uit")]
            for ind in range(0,len(temp.index)):
                if ind==0:
                    dfr.loc[pf,'uit_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'uit_text_'+str(year)] = dfr.loc[pf,'uit_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        # #Engagement
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng')])>0:
        #     dfr.loc[pf,'eng_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="eng")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'eng_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'eng_text_'+str(year)] = dfr.loc[pf,'eng_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
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
                    print(sen)
                    dfr.loc[pf,'eng_pu_' + str(year)] = 1
                    if ('eng_pu_text_'+str(year) in dfr.columns)==False:
                        dfr.loc[pf,'eng_pu_text_'+str(year)] = sen
                    else:
                        dfr.loc[pf,'eng_pu_text_'+str(year)] = str(dfr.loc[pf,'eng_pu_text_'+str(year)]) + "   +   " + sen
                    #if ind==0: 
                    #dfr.loc[pf,'eng_pu_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                    #else:
                    #dfr.loc[pf,'eng_pu_text_'+str(year)] = dfr.loc[pf,'eng_pu_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
            #WORKING ON IT!!!
        #Private engagement
        if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr')])>0:
            dfr.loc[pf,'eng_pr_' + str(year)] = 1
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="eng_pr")]
            for ind in range(0,len(temp.index)):
                if ('eng_pr_text_'+str(year) in dfr.columns)==False:
                #if ind==0:
                    dfr.loc[pf,'eng_pr_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
                else:
                    dfr.loc[pf,'eng_pr_text_'+str(year)] = str(dfr.loc[pf,'eng_pr_text_'+str(year)]) + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        if (len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr1')])>0)&(len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr2')])>0):
            temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier'].isin(['eng_pr1','eng_pr2']))]
            for sen in temp['dnb_nlp:sentence'].unique():
                if (len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='eng_pr1')])>0)&(len(temp[(temp['dnb_nlp:sentence']==sen)&(temp['sig_def:identifier']=='eng_pr2')])>0):
                    print(sen)
                    dfr.loc[pf,'eng_pr_' + str(year)] = 1
                    if ('eng_pr_text_'+str(year) in dfr.columns)==False:
                        dfr.loc[pf,'eng_pr_text_'+str(year)] = sen
                    else:
                        dfr.loc[pf,'eng_pr_text_'+str(year)] = str(dfr.loc[pf,'eng_pr_text_'+str(year)]) + "   +   " + sen
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='eng_pr')])>0:
        #     dfr.loc[pf,'eng_pr_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="eng_pr")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'eng_pr_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'eng_pr_text_'+str(year)] = dfr.loc[pf,'eng_pr_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
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
                    print(sen)
                    dfr.loc[pf,'int_' + str(year)] = 1
                    if ('int_text_'+str(year) in dfr.columns)==False:
                        dfr.loc[pf,'int_text_'+str(year)] = sen
                    else:
                        dfr.loc[pf,'int_text_'+str(year)] = str(dfr.loc[pf,'int_text_'+str(year)]) + "   +   " + sen
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='int')])>0:
        #     dfr.loc[pf,'int_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="int")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'int_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'int_text_'+str(year)] = dfr.loc[pf,'int_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
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
        # #Best-in-class
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='bic')])>0:
        #     dfr.loc[pf,'bic_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="bic")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'bic_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'bic_text_'+str(year)] = dfr.loc[pf,'bic_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        # #Positive screening
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='ps')])>0:
        #     dfr.loc[pf,'ps_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="ps")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'ps_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'ps_text_'+str(year)] = dfr.loc[pf,'ps_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        # #Negative screening
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='ns')])>0:
        #     dfr.loc[pf,'ns_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="ns")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'ns_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'ns_text_'+str(year)] = dfr.loc[pf,'ns_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        # #Green bonds
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='gb')])>0:
        #     dfr.loc[pf,'gb_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="gb")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'gb_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'gb_text_'+str(year)] = dfr.loc[pf,'gb_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
        # #Impact investing
        # if len(df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=='ii')])>0:
        #     dfr.loc[pf,'ii_' + str(year)] = 1
        #     temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['sig_def:identifier']=="ii")]
        #     for ind in range(0,len(temp.index)):
        #         if ind==0:
        #             dfr.loc[pf,'ii_text_'+str(year)] = temp.iloc[ind,:]['dnb_nlp:sentence']
        #         else:
        #             dfr.loc[pf,'ii_text_'+str(year)] = dfr.loc[pf,'ii_text_'+str(year)] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']

dfr.to_excel(OUTPUT_DATA_PATH + 'indicators_methods_text.xlsx') 

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

#Calculate measure max based on results 
dict_years = {2016: [2016],2017:[2016,2017],2018:[2016,2017,2018],2019:[2016,2017,2018,2019],2020:[2016,2017,2018,2019,2020],2021:[2016,2017,2018,2019,2020,2021]}
dft = pd.DataFrame()
methods=['uit','eng_pu','eng_pr','int','scr']
for pf in df['dc:creator'].unique():
    for year in  df['dc:coverage'].unique():
        count=0
        for met in methods:
            list_col = [met+'_'+str(y) for y in dict_years[year]]
            if sum(dfr.loc[pf,list_col])>=1:
                count+=1
            dft.loc[pf,year] = count 
dft.to_excel(OUTPUT_DATA_PATH + 'variety_measure_max.xlsx') 

# #Take maximum over time
# dfn = pd.DataFrame()
# for pf in df_catalog['dc:creator'].unique():
#     year=2016#year 2016
#     for cat in cats:
#         dfr.loc[pf + '_' + str(year) + '_max',cat] = dfr.loc[pf + '_' + str(year),cat]
#     try:
#         dfn.loc[pf,year] = dfr.loc[pf + '_' + str(year),cats].sum()
#     except:
#         dfn.loc[pf,year] = 0
#     for year in years[1:]: #later years
#         for cat in cats:
#             dfr.loc[pf + '_' + str(year) + '_max',cat] = max(dfr.loc[pf + '_' + str(year-1) + '_max',cat],dfr.loc[pf + '_' + str(year),cat])
#         try:
#             dfn.loc[pf,year] = dfr.loc[pf + '_' + str(year) + '_max',cats].sum()
#         except:
#             dfn.loc[pf,year] = 0
# dfn.to_excel(OUTPUT_DATA_PATH + 'variety_measure_max.xlsx')

#OLD CODE

# dfa = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx')
# df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_stanza.xlsx',index_col=0)
# dfs = pd.read_excel(DATA_PATH + 'signal_definitions_climate.xlsx')

# terms = df['sig_def:identifier'].unique()
# terms2 = list(set(terms) - set(['sfdr','sfdr_1','sfdr_2a','sfdr_2b','sfdr_3','imvb','imvb_1','uit','uit_1','uit_2','uit_3','uit_4','rr','rr_2']))
# list_columns = []
# for term in terms2:
#     list_columns += [term, term + ' text']

# dfr = pd.DataFrame()
# total_columns = ['naam','nummer','MVR','MVB','JV2020','BB','SFDR','sfdr: true','sfdr: false','sfdr: optout','sfdr text','imvb: getekend','imvb text','uit: wapens','uit: steenkool','uit: tabak','uit: clustermunitie','uit text','rr: pos','rr text'] + list_columns
# dfr = pd.DataFrame(columns=total_columns)
# dfr['naam'] = dfa['Unnamed: 0']
# dfr['nummer'] = dfa['number']

# #Presence documents
# docs = ['MVR','MVB','JV2020','BB','SFDR']
# for doc in docs:
#     dfr[doc] = 1*(dfa[doc].isnull()==False)

# dfr = dfr.set_index('naam')
# for pf in df['dc:creator'].unique():
#     #SFDR
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('sfdr_1'))])>0:
#         dfr.loc[pf,'sfdr: true'] = 1
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('sfdr_2'))])>0:
#         dfr.loc[pf,'sfdr: false'] = 1
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('sfdr_3'))])>0:
#         dfr.loc[pf,'sfdr: optout'] = 1
#     if (len(df[(df['dc:creator']==pf)&(df['sig_def:identifier']=="sfdr")])>0)&(dfr.loc[pf,'sfdr: true']!=1)&(dfr.loc[pf,'sfdr: false']!=1)&(dfr.loc[pf,'sfdr: optout']!=1): 
#         temp = df[(df['dc:creator']==pf)&(df['sig_def:identifier']=="sfdr")]
#         for ind in range(0,len(temp.index)):
#             if ind==0:
#                 dfr.loc[pf,'sfdr text'] = temp.iloc[ind,:]['dnb_nlp:sentence']
#             else:
#                 dfr.loc[pf,'sfdr text'] = dfr.loc[pf,'sfdr text'] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
#     #IMVB
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('imvb_1'))])>0:
#         dfr.loc[pf,'imvb: getekend'] = 1
#     if (len(df[(df['dc:creator']==pf)&(df['sig_def:identifier']=='imvb')])>0)&(dfr.loc[pf,'imvb: getekend']!=1): 
#         temp = df[(df['dc:creator']==pf)&(df['sig_def:identifier']=="imvb")]
#         for ind in range(0,len(temp.index)):
#             if ind==0:
#                 dfr.loc[pf,'imvb text'] = temp.iloc[ind,:]['dnb_nlp:sentence']
#             else:
#                 dfr.loc[pf,'imvb text'] = dfr.loc[pf,'imvb text'] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
#     #Uitsluitingen
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('uit_1'))])>0:
#         dfr.loc[pf,'uit: wapens'] = 1
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('uit_2'))])>0:
#         dfr.loc[pf,'uit: steenkool'] = 1
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('uit_3'))])>0:
#         dfr.loc[pf,'uit: tabak'] = 1
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('uit_4'))])>0:
#         dfr.loc[pf,'uit: clustermunitie'] = 1
#     if (len(df[(df['dc:creator']==pf)&(df['sig_def:identifier']=="uit")])>0): 
#         temp = df[(df['dc:creator']==pf)&(df['sig_def:identifier']=="uit")]
#         for ind in range(0,len(temp.index)):
#             if ind==0:
#                 dfr.loc[pf,'uit text'] = temp.iloc[ind,:]['dnb_nlp:sentence']
#             else:
#                 dfr.loc[pf,'uit text'] = dfr.loc[pf,'uit text'] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
#     #RR
#     if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains('rr_'))])>0:
#         dfr.loc[pf,'rr: pos'] = 1
#     if (len(df[(df['dc:creator']==pf)&(df['sig_def:identifier']=='rr')])>0)&(dfr.loc[pf,'rr: pos']!=1): 
#         temp = df[(df['dc:creator']==pf)&(df['sig_def:identifier']=="rr")]
#         for ind in range(0,len(temp.index)):
#             if ind==0:
#                 dfr.loc[pf,'rr text'] = temp.iloc[ind,:]['dnb_nlp:sentence']
#             else:
#                 dfr.loc[pf,'rr text'] = dfr.loc[pf,'rr text'] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']

#     #Other terms
#     for term in terms2:
#         if len(df[(df['dc:creator']==pf)&(df['sig_def:identifier'].str.contains(term))])>0:
#             dfr.loc[pf,term] = 1
#             temp = df[(df['dc:creator']==pf)&(df['sig_def:identifier']==term)]
#             for ind in range(0,len(temp.index)):
#                 if ind==0:
#                     dfr.loc[pf,term+' text'] = temp.iloc[ind,:]['dnb_nlp:sentence']
#                 else:
#                     dfr.loc[pf,term+' text'] = dfr.loc[pf,term+' text'] + "   +   " + temp.iloc[ind,:]['dnb_nlp:sentence']
# list3 =  [col for col in list(dfr.columns) if (' text' in col)]
# dfrnt = dfr.drop(columns=list3)


# dfrnt.to_excel(OUTPUT_DATA_PATH + 'indicators.xlsx')
# dfr.to_excel(OUTPUT_DATA_PATH + 'indicators_text.xlsx') 
