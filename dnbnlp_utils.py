# coding: utf-8

"""
dnbnlp_utils.py

All utility functions for NLP projects

"""

import pandas as pd
import stanza
from nafigator import parse2naf
from nafigator import nafdocument
import nafigator as naf
import re
import logging
import os
from os import walk, remove
import numpy as np
from stanza.resources.common import HOME_DIR

try:
    from nltk.corpus import stopwords
except Exception as e:
    import nltk
    nltk.download('stopwords')
    from nltk.corpus import stopwords


class Languagedetector():
    """
    @TODO: When we're not working on Dataiku anymore. Change the init args to:
    (self, words_nl=stopwords.words('dutch'), words_en=stopwords.words('english'))
    We can't get it to work on Dataiku, but it would be the proper input. Also
    remove the arguments it in generate_naf_docs() (in definition and where this
    class is being called)
    """

    def __init__(self, words_nl, words_en):
        self.words_nl = words_nl
        self.words_en = words_en

    def detect(self, raw: str):
        count_nl = 0
        for word_nl in self.words_nl:
            regex = "\\s"+word_nl+"\\s"
            count_nl += len(re.findall(regex, raw))
        count_en = 0
        for word_en in self.words_en:
            regex = "\\s"+word_en+"\\s"
            count_en += len(re.findall(regex, raw))
        if count_nl > count_en:
            return "nl"
        elif count_en >= count_nl:
            return "en"


def create_fileslist(path: str) -> list:
    """
    Puts all accepted doctypes of path in a list.

    Args:
        path: path to the documents
    Returns:
        files: a list of all accepted doctypes
    """
    files = []
    for r, d, f in walk(path):
        for file in f:
            if file.lower().endswith(('.pdf', '.html', '.docx')):
                files.append(os.path.join(r, file))
    return files


def doc2catalog(files: list,
                df_cat: pd.DataFrame,
                document_source=None,
                document_type=None,
                document_year=None,
                prefix: str = '') -> pd.DataFrame:
    """
    Adds file location and file metadata to a dataframe.

    Args:
        files: a list with files
        df_cat: an existing df catalog
        document_source: the document source outside of platform (None if not applicable)
        document_type: e.g. Jaarverslag or Notulen
        document_year: document year
        df: a dataframe containing columns: ['dc:identifier', 'dc:source', 'dc:relation',
                                            'dc:creator', 'dc:format', 'dc:language', 'dc:type',
                                            'dc:coverage', "naf:source", 'naf:status']
        prefix: Name to add as a prefix to unique identifier (e.g. TAAR or TONE)
    Returns:
        df_combined: a Dataframe containing metadata
    """
    dfs_new = []
    for file in files:
        if file.lower().endswith(('.pdf', '.html', '.docx')):
            if file.lower().endswith('pdf'):
                file_format = 'application/pdf'
            if file.lower().endswith('html'):
                file_format = 'text/html'
            if file.lower().endswith('docx'):
                file_format = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            if file not in df_cat['dc:source'].unique():
                logging.info("\t Adding to catalog: " + str(file))
                dfs_new.append(pd.DataFrame(columns=['dc:identifier', 'dc:source', 'dc:relation',
                                                     'dc:creator', 'dc:format', 'dc:language', 'dc:type',
                                                     'dc:coverage', "naf:source", 'naf:status'],
                                            data=[["", file, "", document_source, file_format, "",
                                                   document_type, document_year, "", ""]]))

    if dfs_new == []:   # Catch case when there are no new files to add
        return df_cat

    dfs_new_combined = pd.concat(dfs_new, ignore_index=True)

    # identifier should continue from the existing df_catalog if it isn't empty
    if len(df_cat.index) != 0:
        dfs_new_combined['dc:identifier'] = [prefix + "%05d" %
                                             (val + max(df_cat.index)+1) for val in dfs_new_combined.index]
    else:
        dfs_new_combined['dc:identifier'] = [prefix + "%05d" %
                                             (val) for val in dfs_new_combined.index]
    dfs_new_combined = pd.concat([df_cat] + [dfs_new_combined], ignore_index=True)
    return dfs_new_combined


def generate_naf_files(df_catalog: pd.DataFrame,
                       document_types_to_process: list,
                       output_dir: str,
                       stanza_dir: str = HOME_DIR + '/stanza_resources',
                       words_nl=['de', 'het', 'een', 'rapport', 'notitie', 'bijlage', 'bijlagen',
                                 'tabel', 'tabellen', 'rapportage', 'eindrapportage', 'pagina', 'figuur'],
                       words_en=['the', 'a', 'it', 'report', 'page', 'table']) -> pd.DataFrame:
    """
    Generates naf files and writes back naf:source and naf:status to df_catalog

    Args:
        df_catalog: dataframe containing metadata about the input files
        document_types_to_process: list with document type to process (e.g. jaarverslag, notulen)
        output_dir: location to write naf files to
        stanza_dir: location of stanza resources
        words_nl: list of Dutch stopwords @TODO remove when not working on Dataiku anymore (see Languagedetector())
        words_en: list of English stopwords @TODO remove when not working on Dataiku anymore (see Languagedetector())
    Returns:
        df_catalog: dataframe containing metadata and naf:source & naf:status
    """
    language_detector = Languagedetector(words_nl, words_en)
    nlp_en = stanza.Pipeline(lang="en", verbose=False, dir=stanza_dir)
    nlp_nl = stanza.Pipeline(lang="nl", verbose=False, dir=stanza_dir)

    df_catalog['naf:source'] = df_catalog['naf:source'].replace(np.nan, '')
    subset = df_catalog[df_catalog['dc:type'].str.lower().isin(
        document_types_to_process)]

    for idx, row in subset.iterrows():
        naf = os.path.join(output_dir, row['dc:identifier']+".naf.xml")
        if row['naf:status'] != "ERROR: generating_naf":
            if not os.path.isfile(naf):
                logging.info("... processing " + str(row['dc:source']))
                try:
                    doc = parse2naf.generate_naf(input=row['dc:source'],
                                                 engine="stanza",
                                                 language="nl",
                                                 naf_version="v3.1",
                                                 dtd_validation=False,
                                                 params={'public': {'source': row['dc:source'],
                                                                    'format': row['dc:format'],
                                                                    'language': "nl",
                                                                    'type': row['dc:type'],
                                                                    'coverage': str(row['dc:coverage']),
                                                                    'creator': row['dc:creator']},
                                                         'linguistic_layers': ['text', 'raw']},
                                                 nlp=nlp_nl)
                except Exception as e:
                    logging.warning("\t ERROR: " + str(idx) + str(e))
                    doc = None
                    df_catalog.loc[idx, "naf:status"] = "ERROR: generating_naf"
                    continue

                if doc is not None:
                    lang = language_detector.detect(doc.raw)
                    df_catalog.loc[idx, "dc:language"] = lang
                    doc = parse2naf.generate_naf(input=row['dc:source'],
                                                 engine="stanza",
                                                 language=lang,
                                                 naf_version="v3.1",
                                                 dtd_validation=False,
                                                 params={'public': {'source': row['dc:source'],
                                                                    'format': row['dc:format'],
                                                                    'language': lang,
                                                                    'type': row['dc:type'],
                                                                    'coverage': str(row['dc:coverage']),
                                                                    'creator': row['dc:creator']}},
                                                 nlp=nlp_en if lang == "en" else nlp_nl)
                    logging.warning("... saving " + naf)
                    # write to file
                    with open(naf, "w", encoding="utf-8") as f:
                        f.write(doc.tree2string())

                    df_catalog.loc[idx, 'naf:source'] = naf
                    df_catalog.loc[idx, 'naf:status'] = "OK"
            elif row['naf:source'] == '':
                doc = nafdocument.NafDocument().open(naf)
                # check if naf source is same as catalog source
                if doc.header['public']['{http://purl.org/dc/elements/1.1/}source'] == row['dc:source']:
                    logging.info("... already done")
                    df_catalog.loc[idx, 'naf:source'] = naf
                    df_catalog.loc[idx,
                                   'dc:language'] = doc.header['public']['{http://purl.org/dc/elements/1.1/}language']
                    df_catalog.loc[idx, 'naf:status'] = "OK"
                else:
                    # delete naf file if it doesnt correspond
                    logging.warning("incorrect naf file: " +
                                    naf + ", this should not happen")
                    logging.warning(
                        "---naf    : "+doc.header['public']['{http://purl.org/dc/elements/1.1/}source'])
                    logging.warning("---catalog: "+row['dc:source'])
                    remove(naf)
        else:
            logging.info(
                "... skipped " + str(row['dc:source']) + ", status: " + str(row['naf:status']))
    return df_catalog


def evaluate_sentence(sentence: list, mandatory_terms: list, avoid_terms: list):
    """
    Evaluate sentence on occurrence of mandatory terms and non occurrence of
    term to avoid

    Args:
        sentence: list of terms of sentence to be assessed
        mandatory_terms: list of terms that must be in sentence
        avoid_terms: list of terms that must not be in sentence

    Returns:
        True if mandatory terms are in sentence and avoid terms are not

    """
    # if all mandatory words are in the sentence and none of the avoid_terms
    # then signal
    if (
        all([naf.utils.sublist_indices(t.split(" "), sentence) != []
             for t in mandatory_terms])
        is True
    ):
        if not any(
            [naf.utils.sublist_indices(t.split(" "), sentence) != []
             for t in avoid_terms]
        ):
            return True
    return False


def lemmatize_dataframe(df: pd.DataFrame, nlp: dict, cols_to_lemmatize: list) -> pd.DataFrame:
    """
    Function to lemmatize the signal definitions dataframe.
    @TODO: is this really a function that should be in here or in the analysis itself?
    Args:
        df: signal definitions dataframe ('sig_def:search_method')
        nlp: dict of nlp processors (one per language)
        cols_to_lemmatize: name(s) of the columns to lemmatize
    Returns
        lemmatized signal definitions dataframe
    """
    rows_to_lemmatize = df['sig_def:search_method'] == "lemmatized"
    language = df['dc:language']
    df.loc[rows_to_lemmatize, cols_to_lemmatize] = naf.lemmatize(
        df[rows_to_lemmatize][cols_to_lemmatize],
        language=language[rows_to_lemmatize],
        nlp=nlp
    )
    return df


def lowercase_dataframe(df: pd.DataFrame, columns_to_lowercase: list) -> pd.DataFrame:
    """
    Function to lower case some hardcoded signal definitions columns for rows where the signal isn't Case-sensitive.
    @TODO: is this really a function that should be in here or in the analysis itself?
    Args:
        df: signal definitions dataframe ('sig_def:case_sensitive')
        columns_to_lowercase: name(s) of the columns to lowercase
    Returns
        lower-cased signal definitions dataframe
    """
    rows_to_lowercase = ~df["sig_def:case_sensitive"]
    df.loc[rows_to_lowercase, columns_to_lowercase] = naf.lowercase(
        df[rows_to_lowercase][columns_to_lowercase])
    return df
