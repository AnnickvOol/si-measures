from bertopic import BERTopic
import os
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DATA_PATH = join('data','output','')
MODEL_PATH = join('data','models','Bertopic','')

#Import sentences
df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_mvb_big_sen_pred.xlsx',index_col=0)
df = df[df.prediction==1]

docs = []
for sen in df['dnb_nlp:formatted']:
    docs.append(sen)

topic_model = BERTopic.load(MODEL_PATH + "bertopic_model_mvb_50topics_new",embedding_model="paraphrase-multilingual-MiniLM-L12-v2")

print(topic_model.get_topic_info())

topics, probs = topic_model.transform(docs)
df['topic_number'] = topics

relevant_topics = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 
                   24, 25, 26, 27, 28, 30, 31, 32,33,34, 35, 36, 37, 38, 39, 40, 41,46, 47, 48, 49]
irrelevant_topics = [-1,22,29,42,43,44,45]

merged_topics = {0:[0,1,3,8,11],10:[10,12,24,35,47],9:[9,40],27:[27,36],17:[17,38],13:[13,33],25:[25,31],28:[28,34,49],26:[26,46],5:[5,15]}

for top in merged_topics.keys():
    df.loc[df['topic_number'].isin(merged_topics[top]), 'topic_number'] = top

dfa = pd.DataFrame()
#Create dataframe with amount of relevant topics present for every pension fund for every year
dfa = pd.DataFrame()
for pf in df['dc:creator'].unique():
    for year in df['dc:coverage'].unique():
        temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['topic_number'].isin(relevant_topics))]
        dfa.loc[pf,year] = len(temp['topic_number'].unique())

df.to_excel(OUTPUT_DATA_PATH + 'sentences_spectrum_measure_incl_topiclabel.xlsx')
dfa.to_excel(OUTPUT_DATA_PATH + 'spectrum_measure_DEF.xlsx')
