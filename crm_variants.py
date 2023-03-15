import pandas as pd
import re
import string


def replace_double_spaces_df(df: pd.DataFrame, columns: list = []) -> pd.DataFrame:
    """
    Replaces double spaces in a dataframe on columns. Double spaces are quite common in CRM data.

    Args:
        df: dataframe to remove double spaces from

        Optional:
            columns: list of column names you want to replace double spaces from
    Returns:
        df: dataframe with double spaces replaced by a single one in columns
    """
    if columns:
        for i in columns:
            if df[i].dtype == "object":
                df[i] = df[i].map(str.strip)
            df[i] = df[i].replace(r'\s+', ' ')
        return df
    else:
        for i in df.columns:
            if df[i].dtype == "object":
                df[i] = df[i].map(str.strip)
            else:
                pass
        return df.replace(r'\s+', ' ')


def generate_first_name_variants(first_name: str) -> list:
    """
    Creates a list with first name variants:
    - first name as input
    - initials
    Example: Andy -> [['Andy'], ['A.']]

    Args:
        first_name: a first name as string

    Returns:
    List with first name variants.
    """
    if pd.isna(first_name):
        first_name = ''
    # Identify nickname if it exists, indicated in crm by Name (Nickname)
    nickname = re.findall(r'\((.*?)\)', first_name)
    parentheses = first_name[first_name.find('('):first_name.find(')')+1]
    first_name = first_name.replace(parentheses, '')  # remove nickname between parentheses

    # Remove leading, trailing and multiple whitespaces
    first_name = re.sub(' +', ' ', first_name).strip()
    initials = ["".join([name_part[0] + "." for name_part in first_name.split(" ")
                         if first_name != ''])]  # example: ['A.']
    first_name_variants = [[first_name]] + [nickname] + [initials]
    first_name_variants = [list(x) for x in set(tuple(x) for x in first_name_variants)]
    return first_name_variants


def generate_middle_name_variants(middle_name: str, last_name: str) -> list:
    """
    Creates two lists.
    1. middle_name_variants: with variants based on the middle name combined with the all parts of the last name
    except
    the last part:
    - parts
    - all parts in lower case
    - all parts with only first letter as capital letter
    - parts with only first letter of first part changed to upper letter
    2. middle_name_variant_extra: The middle name split in parts
    Example: middle name = Gerard and last name op het Veld -> [[['Gerard', 'op', 'het'], ['Gerard', 'Op', 'Het'],
    ['gerard', 'op', 'het']], [['Gerard']]]

    Args:
        middle_name: a middle name as string
        last_name: a last name as string

    Returns:
    List with the two lists with middle name variants. One based on only the middle name and one on the partial
    combination of middle and last name.
    """
    if pd.isna(middle_name):
        middle_name = ''
    if pd.isna(last_name):
        last_name = ''

    # Remove leading, trailing and multiple whitespaces
    middle_name = re.sub(' +', ' ', middle_name).strip()
    last_name = re.sub(' +', ' ', last_name).strip()

    middle_name_variant_extra = []
    last_name_first_parts = []
    if middle_name == '':
        if len(last_name.split(" ")) < 2:
            middle_name_variants = []
        else:
            middle_name_variant_extra = [[]]
            last_name_first_parts = last_name.rsplit(" ", 1)[0]
            middle_name_parts = last_name_first_parts.split(" ")
            middle_name_parts_lower = last_name_first_parts.lower().split(" ")
            middle_name_parts_all_upper = [
                m_name[0].upper()+m_name[1:] for m_name in middle_name_parts_lower]
            middle_name_parts_first_upper = [middle_name_parts_all_upper[0]]
            if len(last_name_first_parts.split(" ")) > 1:
                middle_name_parts_first_upper.extend(
                    last_name_first_parts.split(" ")[1:])

            middle_name_variants = [
                middle_name_parts,
                middle_name_parts_lower,
                middle_name_parts_all_upper,
                middle_name_parts_first_upper,
            ]
    else:
        middle_name_variant_extra = [middle_name.split(" ")]  # Example: [Gerard]

        middle_name = " ".join([middle_name] + last_name.split(" ")[0:-1])  # Example 'Gerard op het'
        middle_name_parts = middle_name.split(" ")  # Example: ['Gerard', 'op', 'het]'
        middle_name_parts_lower = middle_name.lower().split(" ")  # Example: ['gerard', 'op', 'het]'
        middle_name_parts_all_upper = [
            m_name[0].upper()+m_name[1:] for m_name in middle_name_parts_lower]  # Example: ['Gerard', 'Op', 'Het]'
        middle_name_parts_first_upper = [middle_name_parts_all_upper[0]]  # Example ['Gerard', 'op', 'het]'
        if len(middle_name.split(" ")) > 1:
            middle_name_parts_first_upper.extend(middle_name.split(" ")[1:])

        middle_name_variants = [
            middle_name_parts,
            middle_name_parts_lower,
            middle_name_parts_all_upper,
            middle_name_parts_first_upper,
        ]

    # remove duplicates
    middle_name_variants = [list(x) for x in set(
        tuple(x) for x in middle_name_variants)]  # Example: [['Gerard', 'op', 'het'], ['Gerard', 'Op', 'Het'],
    # ['gerard', 'op', 'het']]
    return [middle_name_variants, middle_name_variant_extra]


def generate_last_name_variants(last_name: str) -> list:
    """
    Creates two lists.
    1. last_name_variants: with variants based on the middle name combined with the all parts of the last name
    except the last part:
    - last part of last name
    - last name splitting names with "-", keeping "-" as a name part
    - last name split on "-", where each part represents a seperate variant
    2. last_name_variant_extra:
    - last name splitting names with "-", keeping "-" as a name part
    - last name split on "-", where each part represents a seperate variant
    Example: last name = op het Veld -> [[['Veld']], []]
    Args:
        middle_name: a middle name as string
        last_name: a last name as string

    Returns:
    List with the two lists with middle name variants. One based on only the middle name and one on the partial
    combination of middle and last name.
    """
    if pd.isna(last_name):
        last_name = ''

    # Remove leading, trailing and multiple whitespaces
    last_name = re.sub(' +', ' ', last_name).strip()
    last_name_variants, last_name_variant_extra = [], []

    # last name variant 1: last part of last name
    last_name_variants += [[last_name.split(" ")[-1]]]  # Example: ['Veld']
    if "-" in last_name:
        # last name variant 2: last name split on "-" keeping "-" as a name part
        last_name_split = [last_name.split(
            "-")[0].strip(), "-", last_name.split("-")[1].strip()]
        # variant 3: last name split on "-", where each part represents a seperate variant
        last_name_parts = last_name.split("-")
        last_name_parts_list = [[part.strip()] for part in last_name_parts]
        if " " in last_name:
            # variant 3: last name split on "-", where each part represents a seperate variant
            last_name_variant_extra = [
                last_name_split, *last_name_parts_list]
        else:
            # variant 3: last name split on "-", where each part represents a seperate variant
            last_name_variants += [last_name_split, *last_name_parts_list]
    return [last_name_variants, last_name_variant_extra]


def generate_variants(first_name: str,
                      middle_name: str,
                      last_name: str,
                      first_name_variants: list,
                      middle_name_variants: list,
                      last_name_variants: list) -> list:
    """
    Creates a list with all kinds of name variants by combining first, middle and last name variants.
    Example: first name is Andy, second name is Gerard, last name is op het Veld ->
    [['Andy', 'gerard', 'op', 'het', 'Veld'],
        ['Andy', 'Gerard', 'Op', 'Het', 'Veld'],
        ['Andy', 'Gerard', 'op', 'het', 'Veld'],
        ['A.', 'gerard', 'op', 'het', 'Veld'],
        ['A.', 'Gerard', 'Op', 'Het', 'Veld'],
        ['A.', 'Gerard', 'op', 'het', 'Veld'],
        ['gerard', 'op', 'het', 'Veld'],
        ['Gerard', 'Op', 'Het', 'Veld'],
        ['Gerard', 'op', 'het', 'Veld']]

    Args:
        first_name: a first name as string
        middle_name: a middle name as string
        last_name: a last name as string
        firstNameVariants: list of variations on first name
        middleNameVariants: list of variantions on middle name
        lastNameVariants: list of variantions on middle name

    Returns:
    List with name variations as a result of different combinations of first, middle and last name variants.
    """

    if pd.isna(first_name):
        first_name = ''
    if pd.isna(middle_name):
        middle_name = ''
    if pd.isna(last_name):
        last_name = ''

    # Remove leading, trailing and multiple whitespaces
    first_name = re.sub(' +', ' ', first_name).strip()
    middle_name = re.sub(' +', ' ', middle_name).strip()
    last_name = re.sub(' +', ' ', last_name).strip()

    middle_name_variant_extra = middle_name_variants[1]
    middle_name_variants = middle_name_variants[0]
    last_name_variant_extra = last_name_variants[1]
    last_name_variants = last_name_variants[0]

    if middle_name == '' and len(last_name.split(" ")) > 1:
        last_name_first_parts = last_name.rsplit(" ", 1)[0]
    else:
        last_name_first_parts = []
    variants2, variants3, variants4 = [], [], []

    if first_name == '':
        if (middle_name == '') and (last_name_first_parts == []):
            variants1 = last_name_variants
        else:
            variants1 = [[*m_name, *l_name]
                         for m_name in middle_name_variants for l_name in last_name_variants]
            variants2 = [[*m_name, *l_name] for m_name in middle_name_variant_extra
                         for l_name in last_name_variant_extra]
    else:
        if (middle_name == '') and (last_name_first_parts == []):
            variants1 = [[*f_name, *l_name]
                         for f_name in first_name_variants for l_name in last_name_variants]
            variants2 = last_name_variants
        else:
            variants1 = [[*f_name, *m_name, *l_name] for f_name in first_name_variants
                         for m_name in middle_name_variants for l_name in last_name_variants]
            variants2 = [[*m_name, *l_name] for m_name in middle_name_variants
                         for l_name in last_name_variants]
            variants3 = [[*f_name, *m_name, *l_name] for f_name in first_name_variants
                         for m_name in middle_name_variant_extra for l_name in last_name_variant_extra]
            variants4 = [[*m_name, *l_name] for m_name in middle_name_variant_extra
                         for l_name in last_name_variant_extra]

    variant_list = variants1 + variants2 + variants3 + variants4
    # Example variants1:
    # [['Andy', 'gerard', 'op', 'het', 'Veld'],
    #  ['Andy', 'Gerard', 'Op', 'Het', 'Veld'],
    #  ['Andy', 'Gerard', 'op', 'het', 'Veld'],
    #  ['A.', 'gerard', 'op', 'het', 'Veld'],
    #  ['A.', 'Gerard', 'Op', 'Het', 'Veld'],
    #  ['A.', 'Gerard', 'op', 'het', 'Veld']]
    # Example variants2:
    # [['gerard', 'op', 'het', 'Veld'],
    #  ['Gerard', 'Op', 'Het', 'Veld'],
    #  ['Gerard', 'op', 'het', 'Veld']]
    # Example variants3: []
    # Example variants4: []
    # Example variant_list:
    # [['Andy', 'gerard', 'op', 'het', 'Veld'],
    #  ['Andy', 'Gerard', 'Op', 'Het', 'Veld'],
    #  ['Andy', 'Gerard', 'op', 'het', 'Veld'],
    #  ['A.', 'gerard', 'op', 'het', 'Veld'],
    #  ['A.', 'Gerard', 'Op', 'Het', 'Veld'],
    #  ['A.', 'Gerard', 'op', 'het', 'Veld'],
    #  ['gerard', 'op', 'het', 'Veld'],
    #  ['Gerard', 'Op', 'Het', 'Veld'],
    #  ['Gerard', 'op', 'het', 'Veld']]

    return [list(x) for x in set(tuple(x) for x in variant_list)]


def generate_org_name_variants(organizations_df: pd.DataFrame) -> pd.DataFrame:
    """Generates organization name variants
    Args:
        organizations_df: a dataframe containing organization names from
                        CRM (columns: Name, Id, MDMNumber, RelationNumber)
    Returns:
        name_var_df: dataframe containing one or more name variants for every name in organizations_df
    """
    # list of legal terms you'd want to substract from the crm organization name
    exceptionlist = ['NV', 'N.V.', 'n.v.', 'BV', 'B.V.', 'b.v.', 'VOF', 'V.O.F.', 'LLP',
                     'GmbH', 'CV', 'Limited', 'Inc', 'Ltd', 'plc', 'UA', 'U.A.', 'BA', 'SA',
                     'LP', 'AG', 'AB', 'AD', 'Fonds', 'Coöperatief', 'Coöperatieve', 'Hedged',
                     'Fund', 'Portfolio', 'liquidatie']
    # add "space or start of string" and "space or end of string" to exception
    exceptionlist = [r'((^|\s)' + val.replace('.', '\\.') +
                     r'($|\s))' for val in exceptionlist]
    exceptions_regex = '|'.join(exceptionlist)

    name_var_df = organizations_df[[
        'Name', 'Id', 'MDMNumber', 'RelationNumber']].copy()
    name_var_df = replace_double_spaces_df(name_var_df, ['Name'])

    name_var_df['Name'] = name_var_df['Name'].fillna('')
    name_var_df['Name'] = name_var_df['Name'].str.replace(',', '')

    name_var_df['Name_wo_quotes'] = name_var_df.Name.replace(
        r'"', '', regex=True)  # replace quotes

    name_var_df['Name_wo_punctuation'] = name_var_df.Name.replace(
        r'[^\w\s]', '', regex=True)  # replace punctuation

    name_var_df['Name_wo_quotes_wo_exceptions'] = name_var_df['Name_wo_quotes'].replace(
        exceptions_regex, ' ', regex=True)  # no exceptions

    name_var_df['Name_no_parentheses'] = name_var_df['Name_wo_quotes'].apply(
        lambda x: re.sub(r"\([^()]*\)", "", x))  # remove words between parentheses

    name_var_df['Short_hand_name'] = name_var_df['Name'].str.extract(
        r'\"(.*)\"')  # extract shorthand name between ""
    name_var_df['Short_hand_name'].fillna('', inplace=True)

    name_var_df['Without_shorthand'] = [a.replace(b, '').strip() for a, b in zip(
        name_var_df['Name_no_parentheses'], name_var_df['Short_hand_name'])]  # remove shorthand name from no parenthese

    # Put everything into long format, drop duplicate and empty name variants.
    name_var_df = (pd.melt(name_var_df, id_vars=['Name', 'Id', 'MDMNumber', 'RelationNumber'])
                     .rename(columns={'value': 'Name_Variants'})
                     .drop('variable', axis=1)
                     .dropna(axis=0, subset=['Name_Variants'])
                     .drop_duplicates()
                     .sort_values('Name')
                     .reset_index(drop=True))

    # Remove leftover spacing at the end of the strings.
    name_var_df['Name_Variants'] = name_var_df.Name_Variants.str.strip().str.split()
    return name_var_df


def generate_name_variants_df(name_input_df: pd.DataFrame,
                              cols_to_keep: list = ['crm:PersonId',
                                                    'crm:FirstName',
                                                    'crm:MiddleName',
                                                    'crm:LastName',
                                                    'crm:Organisatie.RelationNumber'],
                              unpivot: bool = False) -> pd.DataFrame:
    """
    Generates a DataFrame with name variants given a first, middle and last name.
    Used to look up these generated name variants in text later.

    Example:
    Input: Dataframe with columns first_name = "Andy", middle_name = "Gerard", last_name "op het Veld"
    Output: The output will add a columns:
            FirstNameVariants =
            [['Andy'], ['A.']]
            MiddletNameVariants =
            [[['Gerard', 'op', 'het'], ['Gerard', 'Op', 'Het'],
              ['gerard', 'op', 'het']], [['Gerard']]]
            LastNameVariants =
            [[['Veld']], []]
            NameVariants =
            [['A.', 'Gerard', 'Op', 'Het', 'Veld'],
             ['A.', 'gerard', 'op', 'het', 'Veld'],
             ['A.', 'Gerard', 'op', 'het', 'Veld'],
             ['Andy', 'Gerard', 'Op', 'Het', 'Veld'],
             ['Andy', 'gerard', 'op', 'het', 'Veld'],
             ['Andy', 'Gerard', 'op', 'het', 'Veld'],
             ['Gerard', 'Op', 'Het', 'Veld'],
             ['gerard', 'op', 'het', 'Veld'],
             ['Gerard', 'op', 'het', 'Veld']]


    Args:
        name_input_df: a dataframe containing at least a first name, middle name and last name.
        cols_to_keep: a list of columns to be kept in the output DataFrame.
        unpivot: boolean indicating whether to unpivot the table based on the name variants.
    Returns:
        DataFrame with cols_to_keep and a column with the name variants tokens.
    """

    # cleaning
    name_df = name_input_df.filter(items=cols_to_keep)
    cols = ["crm:FirstName", "crm:MiddleName", "crm:LastName"]
    name_df.fillna({x: '' for x in cols}, inplace=True)
    replace_double_spaces_df(name_df, cols)

    name_df['FirstNameVariants'] = list(map(generate_first_name_variants,
                                            name_df['crm:FirstName']))

    name_df['MiddleNameVariants'] = list(map(generate_middle_name_variants,
                                             name_df['crm:MiddleName'], name_df['crm:LastName']))

    name_df['LastNameVariants'] = list(map(generate_last_name_variants,
                                           name_df['crm:LastName']))

    name_df['NameVariants'] = list(map(generate_variants,
                                       name_df['crm:FirstName'],
                                       name_df['crm:MiddleName'],
                                       name_df['crm:LastName'],
                                       name_df['FirstNameVariants'],
                                       name_df['MiddleNameVariants'],
                                       name_df['LastNameVariants']))

    name_df['NameVariants'] = pd.DataFrame(map(lambda x, y: [[[x]] + y],
                                               name_df['crm:FirstName'],
                                               name_df['NameVariants']))

    if unpivot:
        cols_to_keep += ['NameVariants']

        name_df = name_df[cols_to_keep].explode('NameVariants')

    return name_df.reset_index(drop=True)
