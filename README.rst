=========
si-measures
=========

Features
--------

The si-measures repository contains the source code for the paper Talk the green talk: a textual analysis of pension funds' disclosures.
(link)

Abstract:
In this paper, we analyze the disclosures of sustainable investing by Dutch pension funds in their annual reports from 2016 to 2021. We introduce a novel textual analysis approach using state-of-the-art natural language processing (NLP) techniques to measure the awareness and implementation of sustainable investing, where we define awareness as the amount of attention paid to sustainable investing in the annual report. We exploit a proprietary dataset to analyze the relation between pension fund characteristics and sustainable investing. We find that a pension fund's size increases both the awareness and the implementation of sustainable investing. Moreover, we analyze the role of signing the International Responsible Business Conduct (IRBC) initiative. Large pension funds, pension funds with more female trustees or pension funds with a positive belief about the risk-return relation of sustainable investing are more likely to sign the IRBC initiative. Although signing this initiative increases the specificity of pension fund statements about sustainable investing, we do not find an effect on the implementation of sustainable investing.

This repository contains the source code to calculate the five sustainable-investment measures that quantify the awareness and implementation of sustainabe investing.

Installation
------------

Clone the repo and install the dependencies

::

    git clone https://github.com/AnnickvOol/si-measures.git
    cd si-measures

Create Python environment with relevant packages

::

    conda create --name nlp-si python=3.8
    source activate nlp-si
    pip install -r requirements.txt


How to run
----------

Select relevant files and create catalog with all files

::

    python select_relevant_files.py
    python create_catalog.py
    
Convert pdf files to naf files

::

    python convert_pdfs_naf.py
    
Extract all SI-related sentences from the naf files

::

    select_relevant_sentences.py

We finetune a trained BERT model using labeled datasets for two classification tasks: determining whether a sentence is SI-related or not and determining whether a paragraph is specific or not.

::
    
    Finetune BERT model.ipynb

One of the SI measures makes use of the output of BERTopic. In the following notebook latent topics are extracted from the set of SI-related sentences.

::

    Topic modelling BERTopic.ipynb

Calculate the sustainable-investment measures
   
::

    create_intensity_measure.py
    create_variety_measure.py
    create_specificity_measure.py
    create_spectrum_measure.py
    create_scope_measure.py
