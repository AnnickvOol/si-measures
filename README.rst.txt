=========
si-measures
=========

Features
--------

The si-measures repository contains the source code for the paper [Talk the green talk: a textual analysis of pension funds' disclosures.](https://...).

Abstract:
In this paper, we analyze the disclosures of sustainable investing by Dutch pension funds in their annual reports from 2016 to 2021. We introduce a novel textual analysis approach using state-of-the-art natural language processing (NLP) techniques to measure the awareness and implementation of sustainable investing, where we define awareness as the amount of attention paid to sustainable investing in the annual report. We exploit a proprietary dataset to analyze the relation between pension fund characteristics and sustainable investing. We find that a pension fund's size increases both the awareness and the implementation of sustainable investing. Moreover, we analyze the role of signing the International Responsible Business Conduct (IRBC) initiative. Large pension funds, pension funds with more female trustees or pension funds with a positive belief about the risk-return relation of sustainable investing are more likely to sign the IRBC initiative. Although signing this initiative increases the specificity of pension fund statements about sustainable investing, we do not find an effect on the implementation of sustainable investing.

This repository contains the source code to calculate the five sustainable-investment measures that quantify the awareness and implementation of sustainabe investing.

### Citing this work

If you find this work useful in your research, please consider citing:

```
@article{Bauer2023,
  title={Talk the green talk: a textual analysis of pension funds' disclosures.},
  author={Bauer, Rob and Broeders, Dirk and van Ool, Annick},
  journal={DNB Working Paper Series},
  number={...},
  year={2023},
  publisher={DNB}
}

```

# Install

### Clone the repo and install dependencies 

```shell
## Download the repository
git clone https://github.com/AnnickvOol/si-measures.git
cd si-measures
## Create python env with relevant packages
conda create --name nlp-si python=3.8
source activate nlp-si
pip install -r requirements.txt

```

# Create catalog with files



# Extracting relevant sentences

We use a dictionary with SI-related keywords and combinations of keywords to extract all SI-related sentences using a lemmatized key-word search. 

# Training BERT model

We train a BERT model ....




## License

