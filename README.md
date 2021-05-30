ESG data codebase
==============================

Collection of python scripts and code snippets to get alternative ESG data from sources like Google Trends or Google results. 

## Goal

Empower projects within _sustainable finance_ with a codebase and provide a starting point for data sourcing, analyses or modelling. We plan to upload python scripts that source from

1. Google Trends
2. Google results
3. Yahoo! Finance

The project is in the scope of the [towards sustainable finance](http://towardssustainablefinance.com/) initiative. We always welcome anyone interested in joining forces and look forward to your [message](mailto:info@towardssustainablefinance.com).

<center><img src="references/img/tsf_logo.png" height ="300" width="310"/></center>

## Getting started

Configure `settings.yaml`. Mine looks like:

```yaml
dir:
  raw: 'data/raw'
  interim: 'data/interim'
  processed: 'data/processed'
  external: 'data/external'
query:
  google_results:
    user_agent: {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    base_url: "https://www.google.com/search?q="
```

### Search interest over time

To get analysis-ready data from Google trends, use  `get_interest_over_time()`. It takes a list of keywords and stores each query result into a CSV in `filepath`. It has in-built error handling and is designed fail-safe. For example, it increases the timeout between queries if one fails due to rate limit. Even after max retries, data is not lost, but the unsuccessful keywords are stored in a csv. 


## Code reference

Here is the official documentation powered by mkdocs and mkdocstrings.

> https://philippschmalen.github.io/ESG-data-codebase/

## Useful resources

The project benefits from previous work of the repositories: 

1. https://github.com/philippschmalen/ESG-trending-topics-radar
2. https://github.com/philippschmalen/ESG-with-googletrends
3. https://github.com/philippschmalen/ESG-topics-Google-count
4. https://github.com/philippschmalen/etl_spark_airflow_emr


Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- Files build with mkdocs and mkdocstrings. Use Google style docstrings
    │
    ├── streamlit          <- Streamlit apps to interact with data. Naming convention according to TDS process:
    │                         the process step and a short `-` delimited step description, e.g.
    │                         `0-exploration`, `1-preprocessing`, `2-feature_engineering`, `3-modelling`.
    │
    ├── notebooks          <- Jupyter notebooks to interact with data. Same conventions like ./streamlit apply
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── conda_env.yaml      <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `conda env export -f --no-builds  > conda_env.yaml`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
            └── make_dataset.py



--------

## Dev

Here is everything related to further develop and maintain the project.  

### Conda virtual env

__Build__ `conda env create -f conda_env.yaml`

__Export to yaml__ `conda env export --no-builds > conda_env.yaml`


### Build documentation with mkdocs

Following Google style doccstrings: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html 

A common issue that causes false rendering is to include a space after a headline. `Args: ` will __not__ work, but `Args:` will do.

Workflow to update documentation: 

```bash
# conda activate esg_codebase
mkdocs serve # live-reloading for editing
mkdocs build # build static site
mkdocs gh-deploy # deploy to github pages
```

#### From scratch

```bash
# in project root, run with conda env activated
mkdocs new . 
# created mkdocs.yml and ./docs
```
Configure `mkdocs.yml` to work with `mkdocstrings` package. 
```yaml
site_name: ESG data codebase
theme:
  name: "material" # theme works with mkdocstrings
plugins: 
  - search
  - mkdocstrings:
      default_handler: python 
      watch:
        - src/data # enable auto-reload
```

Add python scripts to `index.md` so that they appear in the code reference: 

```markdown
# Code reference
## Google results count
::: src.data.gresults_extract.py
---
## Google trends
::: src.data.gtrends_extract.py
```

--- 

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
