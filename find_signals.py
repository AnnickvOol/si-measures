import pandas as pd
import nafigator
import re
import dnbnlp_genfun.dnbnlp_utils as dnbutils
from nafigator.utils import get_context_rows

def retrieve_named_entities(df_name_vars: pd.DataFrame, sentence: dict, words: dict) -> dict:
    """
    Returns dict of named entities (term ids) in a sentence

    Args:
        df_name_vars: dataframe containing NameVariants crm:PersonId, crm:Initials, crm:MiddleName, crm:LastName
        sentence: naf sentence dict
        words: naf word list of naf document

    Returns:
        dict of named entities found in sentence where key is entity id
                    and value is entity initials + last name

    """
    sentence_words = [words[word['id']]['text'] for word in sentence['span']]
    sentence_term_ids = [term['id'] for term in sentence['terms']]
    named_entities = dict()
    for row in df_name_vars.index:
        name_variant = df_name_vars.loc[row, "NameVariants"]
        entity_id = df_name_vars.loc[row, "crm:PersonId"]
        entity_name = ' '.join([df_name_vars.loc[row, 'crm:Initials'], df_name_vars.loc[row, 'crm:MiddleName'],
                                df_name_vars.loc[row, "crm:LastName"]]).strip()
        entity_term_indices = nafigator.sublist_indices(name_variant, sentence_words)
        if entity_term_indices != []:
            spans = [[sentence_term_ids[idx] for idx in result] for result in entity_term_indices]
            # if already found a named_entity then add other spans
            if entity_id in named_entities.keys():
                spans += named_entities[entity_id]
            spans = nafigator.remove_sublists(spans)
            named_entities[entity_id] = entity_name
    return named_entities


def get_sentences_para(para_id,sent_id,naf_sentences):
    """
    Retrieves ...
    Args:
        para_id: List with paragraph id 
        sent_id: List with sentence id(s)
        naf_sentences: a NafDocument.sentences 

    Returns:
        result: list with seperate sentences in paragraph 
    """

    para_sent = []
    for sent in sent_id:
        para_sent += [naf_sentences[int(sent)-1]['text']]

    return para_sent

def add_signal(results: pd.DataFrame, sig_count: int, terms: list, sentence: dict,
               sig_def_id: str, sig_def_group: str, doc: nafigator.NafDocument, params: dict = {}):
    """
    Add signal to results dictionary and add sig_count
    If sentence already in results then append signal term to terms list

    Args:
        results: dict with all signals
        sig_count: signal number count
        terms: terms of the signal
        sentence: naf sentence dict
        sig_def_id: signal definition identifier
        sig_def_group: signal definition group
        params (optional): could contain any of add_context: int, print_progress: bool, extra_cols: list,
                            df_kfh_vars: pd.DataFrame
    Returns:
        results: dict with all found results
        sig_count: signal number
    """
    doc_words = {word['id']: word for word in doc.text}
    df_kfh_vars = pd.DataFrame()
    found = False
    unpivot = False
    add_context = 0
    if "unpivot" in params.keys():
        unpivot = params['unpivot']
    if "add_context" in params.keys():
        add_context = params['add_context']
    if "df_kfh_vars" in params.keys():
        df_kfh_vars = params["df_kfh_vars"]

    # Merges sig_res:terms if already exists in results, adding together the terms as a list
    # note that it only shows the identifier and group of the first term if you do this.
    if not unpivot:
        for sig in results.keys():  # Check if sentence already in results.
            if sentence['text'] == results[sig]['dnb_nlp:sentence']:
                if terms not in results[sig]['sig_res:terms']:
                    results[sig]['sig_res:terms'].append(terms)
                found = True

    if not found:
        sig_res_id = sig_def_id + ":" + str(sig_count)

        results[sig_res_id] = {"sig_res:identifier": sig_res_id,
                               "sig_def:identifier": sig_def_id,
                               "sig_def:group": sig_def_group,
                               "sig_res:terms": [terms],
                               "dnb_nlp:sentence": sentence['text'],
                               "dnb_nlp:page": sorted([int(item) for item in sentence['page']]),
                               "dnb_nlp:para_id": sentence['para'],
                               "dnb_nlp:sent_id": sentence['sent']}
        if add_context > 0:
            results[sig_res_id].update({"dnb_nlp:formatted": get_sentences_para(sentence['para'],sentence['sent'],doc.sentences)}) #if list with sentences added to pargraph
            #results[sig_res_id].update({"dnb_nlp:formatted": get_context_rows(
            #    sentence, doc_words, doc.formats, add_context)})
        if len(df_kfh_vars) > 0:
            named_entities = list(retrieve_named_entities(df_kfh_vars, sentence, doc_words).values())
            results[sig_res_id].update({"dnb_nlp:PERSON": named_entities})

        sig_count += 1

    return results, sig_count

def apply_signals(naf: nafigator.NafDocument, df_signals: pd.DataFrame, sig_count: int, params: dict = {}):
    """
    Apply signal definitions to naf document

    Args:
        naf: the naf document to be searched
        df_signals: the signal definitions
        sig_count: signal number count
        params (optional): should contain add_context: int, print_progress: bool, extra_cols: list,
                            df_kfh_vars: pd.DataFrame

    Returns:
        results: dict with all signals
        sig_count: signal number

    """
    results = dict()
    naf_terms = {term['id']: term for term in naf.terms}
    for idx in df_signals[df_signals['dc:language'] == naf.language].index:
        # get signal definition
        sig_def_id = df_signals.loc[idx, 'sig_def:identifier']
        sig_def_group = df_signals.loc[idx, 'sig_def:group']
        search_method = df_signals.loc[idx, 'sig_def:search_method']
        case_sensitive = df_signals.loc[idx, 'sig_def:case_sensitive']
        search_level = df_signals.loc[idx, "sig_def:search_level"]
        if "sentence" in search_level:
            search_items = naf.sentences
        elif "paragraph" in search_level:
            search_items = naf.paragraphs
        else:
            search_items = naf.paragraphs
        # perform search
        if search_method == "lemmatized":
            mandatory_terms = [term.strip() for term in df_signals.loc[idx, 'sig_def:mandatory_terms'].split(",")]
            if not pd.isna(df_signals.loc[idx, 'sig_def:avoid_terms']):
                avoid_terms = [term.strip() for term in df_signals.loc[idx, 'sig_def:avoid_terms'].split(",")]
            else:
                avoid_terms = []
            aliases = df_signals.loc[idx, 'sig_def:aliases']
            for sentence in search_items:
                lemmatized_sentence = nafigator.lemmatize_sentence(sentence, naf_terms)
                if not case_sensitive:
                    lemmatized_sentence = nafigator.lowercase(lemmatized_sentence)

                    if dnbutils.evaluate_sentence(lemmatized_sentence, mandatory_terms, avoid_terms):
                        results, sig_count = add_signal(results,
                                                        sig_count,
                                                        mandatory_terms,
                                                        sentence,
                                                        sig_def_id,
                                                        sig_def_group,
                                                        naf,
                                                        params)
                    for term in aliases.keys():
                        for alias in aliases[term]:
                            mandatory_aliases = [t.replace(term, alias) for t in mandatory_terms]
                            if dnbutils.evaluate_sentence(lemmatized_sentence, mandatory_aliases, avoid_terms):
                                results, sig_count = add_signal(results,
                                                                sig_count,
                                                                mandatory_terms,
                                                                sentence,
                                                                sig_def_id,
                                                                sig_def_group,
                                                                naf,
                                                                params)

        elif search_method == "regex":
            reg_expr = df_signals.loc[idx, 'sig_def:mandatory_terms']
            reg_expr_compiled = re.compile(reg_expr)  # @TODO: add flags
            for sentence in search_items:
                text = sentence['text']
                if not case_sensitive:
                    text = nafigator.lowercase(text)
                if bool(reg_expr_compiled.search(text)):
                    results, sig_count = add_signal(
                        results, sig_count, [reg_expr], sentence, sig_def_id, sig_def_group, naf, params)
        else:
            print("search method not yet implemented")
    return results, sig_count


def search_naf_files_for_signals(df_catalog: pd.DataFrame,
                                 df_signal_defs: pd.DataFrame,
                                 params: dict = {}) -> pd.DataFrame:
    """
    Searches through the naf files of df_catalog for the signals in df_signals. Saves them in a dataframe.

    Args:
        df_catalog: catalog dataframe ('dc:identifier', 'dc:source', 'dc:relation',
                        'dc:creator', 'dc:format', 'dc:language', 'dc:type', 'dc:coverage')
        df_signal_defs: dataframe with signals to find ('sig_def:identifier', 'sig_def:group',
                        'sig_def:search_method', 'sig_def:case_sensitive')
        params (optional): could contain any or combination of any of
                            add_context: bool, print_progress: bool, extra_cols: list,
                            df_kfh_vars: pd.DataFrame

    Returns:
        Dataframe with signals that have been found.
    """
    # init extra flags
    print_progress = False
    add_context = 0
    extra_cols = []
    df_kfh_vars = pd.DataFrame()

    if "add_context" in params.keys():
        add_context = params['add_context']
    if "print_progress" in params.keys():
        print_progress = params['print_progress']
    if "extra_cols" in params.keys():
        extra_cols = params['extra_cols']
    if "df_kfh_vars" in params.keys():
        df_kfh_vars = params['df_kfh_vars']

    catalog_columns = ['dc:identifier', 'dc:source', 'dc:relation',
                       'dc:creator', 'dc:format', 'dc:language', 'dc:type', 'dc:coverage', 'naf:source','dc:number'] + extra_cols
    assert all(col in df_catalog.keys() for col in catalog_columns), \
        "df_catalog doesn't have all the right columns: " + str(catalog_columns)

    output = []
    sig_count = 1
    for _, row in df_catalog.iterrows():
        naf_file = row['naf:source']
        if pd.notna(naf_file):
            naf = nafigator.NafDocument().open(naf_file)
            # term_dict = {term['id']: term for term in naf.terms}
            if print_progress:
                print('Processing: ' + naf_file)

            signals, sig_count = apply_signals(naf, df_signal_defs, sig_count, params)

            if signals != {}:
                output.extend([list(row[catalog_columns].values) +
                               list(signal.values()) for signal in signals.values()])
        else:
            print("Skipped: " + row['dc:source'] + ": no NAF file")

    columns = catalog_columns + ['sig_res:identifier',
                                 'sig_def:identifier',
                                 'sig_def:group',
                                 'sig_res:terms',
                                 'dnb_nlp:sentence',
                                 'dnb_nlp:page',
                                 'dnb_nlp:para_id',
                                 'dnb_nlp:sent_id']

    if add_context > 0:
        columns = columns + ['dnb_nlp:formatted']
    if len(df_kfh_vars) > 0:
        columns = columns + ['dnb_nlp:PERSON']

    return pd.DataFrame(data=output, columns=columns)
