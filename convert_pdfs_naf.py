import pandas as pd
import pikepdf
from os import listdir, walk, remove, makedirs
from os.path import isfile, join, basename, exists
from io import StringIO
import re
import numpy as np
from lxml import etree
import stanza
import nafigator
from nafigator import nafdocument
from nafigator import parse2naf
#import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords

DOC_DATA_PATH = join('data','downloads','')
STANZA_DATA_PATH = join('data','naf_files','')
OUTPUT_DATA_PATH = join('data','output','')

stopwords_en = stopwords.words('english')
stopwords_nl = stopwords.words('dutch')
stopwords_nl += ['rapport', 'notitie', 'bijlage', 'bijlagen', 'tabel', 'tabellen', 'rapportage', 'eindrapportage', 'pagina', 'figuur']
stopwords_en += ['report', 'page', 'table']

def determine_language(raw: str):
    count_nl = 0
    for stopword_nl in stopwords_nl:
        regex = "\\s"+stopword_nl+"\\s"
        count_nl += len(re.findall(regex, raw))
    count_en = 0
    for stopword_en in stopwords_en:
        regex = "\\s"+stopword_en+"\\s"
        count_en += len(re.findall(regex, raw))
    if count_nl > count_en:
        return "nl"
    elif count_en >= count_nl:
        return "en"

stanza.download('nl')
nlp_nl = stanza.Pipeline(lang="nl", processors='tokenize,pos,lemma')
stanza.download('en')
nlp_en = stanza.Pipeline(lang="en", processors='tokenize,pos,lemma')

df = pd.read_excel(OUTPUT_DATA_PATH + 'relevant_files.xlsx',index_col=0)
df_catalog = pd.read_excel(OUTPUT_DATA_PATH + 'df_catalog.xlsx',index_col=0)

for idx, row in enumerate(df_catalog.index):
    input = df_catalog.loc[row]
    naf = join(STANZA_DATA_PATH, input['dc:identifier']+".naf.xml")
    print(naf)
    if not isfile(naf):
        print("... processing "+ str(input['dc:source']))
        print(join(DOC_DATA_PATH,basename(input['dc:creator']), basename(input['dc:source'])))
        try:
            pdf = pikepdf.open(join(DOC_DATA_PATH,basename(input['dc:creator']), basename(input['dc:source'])))
            if not exists(join(STANZA_DATA_PATH,basename(input['dc:creator']))):
                makedirs(join(STANZA_DATA_PATH,basename(input['dc:creator'])))
            pdf.save(join(STANZA_DATA_PATH,basename(input['dc:creator']),basename(input['dc:source'])))
            doc = parse2naf.generate_naf(input = join(STANZA_DATA_PATH,basename(input['dc:creator']), basename(input['dc:source'])),
                                engine = "stanza",
                                language = "nl",
                                naf_version = "v3.1",
                                dtd_validation = False,
                                params = {'public': {'source': input['dc:source'],
                                                        'format': input['dc:format'],
                                                        'language': "nl",
                                                        'type': input['dc:type'],
                                                        'coverage': str(input['dc:coverage']),
                                                        'creator': input['dc:creator']},
                                                        'linguistic_layers': ['text', 'raw','terms']},
                                                        nlp = nlp_nl)
        except:
            print("Error: " + str(row) + " : "+ input['dc:source'])
            doc = None
            df_catalog.loc[row, "status"] = "ERROR: generating_naf"     

        if doc is not None:
            lang = determine_language(doc.raw)
            df_catalog.loc[row, "dc:language"] = lang

            print("... saving " + naf)
            with open(naf, "w", encoding = "utf-8") as f:
                f.write(doc.tree2string())

            df_catalog.loc[row, 'naf:source'] = naf
            df_catalog.loc[row, 'naf:status'] = "OK" 

df_catalog.to_excel(OUTPUT_DATA_PATH + 'df_catalog.xlsx')
