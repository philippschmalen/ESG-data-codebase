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

Configure `settings.yaml`

TODO: Describe how to use the code snippets

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
