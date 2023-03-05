from bertopic import BERTopic
import os
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DATA_PATH = join('data','output','')
MODEL_PATH = join('data','models','bertopic','')

#Import sentences
df = pd.read_excel(OUTPUT_DATA_PATH + 'df_results_mvb_big_prediction.xlsx',index_col=0)
df = df[df.prediction==1]

docs = []
for sen in df['dnb_nlp:sentence']:
    docs.append(sen)

topic_model = BERTopic.load(MODEL_PATH + "bertopic_model_mvb",embedding_model="paraphrase-multilingual-MiniLM-L12-v2")

topics, probs = topic_model.transform(docs)
df['topic_number'] = topics

for top in topics.keys():
    df.loc[df['topic_number'].isin(topics[top]), 'topic_number'] = top

dfa = pd.DataFrame()
#Create dataframe with amount of relevant topics present for every pension fund for every year
dfa = pd.DataFrame()
for pf in df['dc:creator'].unique():
    for year in df['dc:coverage'].unique():
        temp = df[(df['dc:creator']==pf)&(df['dc:coverage']==year)&(df['topic_number'].isin(relevant_topics))]
        dfa.loc[pf,year] = len(temp['topic_number'].unique())

dfa.to_excel(OUTPUT_DATA_PATH + 'spectrum_measure.xlsx')
