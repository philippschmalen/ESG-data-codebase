# -*- coding: utf-8 -*-
import streamlit as st

import logging
import pandas as pd
import yaml

import sys
sys.path.append('../src/data')
sys.path.append('../src/visualization')


#---------------------------------------------------
# FIRM NAMES
#---------------------------------------------------

from yahooquery import Ticker
from pytickersymbols import PyTickerSymbols
import logging
import numpy as np
import re 

def get_index_stock_details(pytickersymbols, index_name):
    """Get firm name, stock ticker for a specified stock index. 
    Available indices from pytickersymbols: PyTickerSymbols().get_all_indices() 
    See https://github.com/portfolioplus/pytickersymbols for package details

    Args:
        pytickersymbols (object): Init object from PyTickerSymbols()
        index_name (str): Index name from PyTickerSymbols().get_all_indices() 
    
    Returns:
        Dataframe: 
    """
    index_details = pd.DataFrame(pytickersymbols.get_stocks_by_index(index_name))
    
    # string encoding
    try: 
        index_details.name = index_details.name.str.encode('latin-1').str.decode('utf-8')
    except Exception as e: 
        logging.warning(f"Encoding error for {index_name}")
        index_details.name = index_details.name.str.encode('utf-8').str.decode('utf-8')

    # retrieve yahoo ticker symbol
    index_details['yahoo_ticker'] = index_details.symbols.apply(lambda x: x[0]['yahoo'] if len(x) > 1 else np.nan)
    index_details.yahoo_ticker.fillna(index_details.symbol, inplace=True)

    # set ticker as index
    index_details.set_index('yahoo_ticker', inplace=True, drop=False)
    index_details.drop(columns=['id'], inplace=True)

    return index_details

def get_esg_details(yahoo_ticker):
    """Returns dataframe with esg information for suitable yahoo ticker (can be string, pd.Series or list)"""
    
    # convert series to list
    if isinstance(yahoo_ticker, pd.Series): 
        yahoo_ticker = yahoo_ticker.to_list()
    
    ticker_details = Ticker(yahoo_ticker)
    esg_df = pd.DataFrame(ticker_details.esg_scores).T

    return esg_df

@st.cache(allow_output_mutation=True)
def get_index_firm_esg(pytickersymbols, index_name):
    index_stocks = get_index_stock_details(pytickersymbols=pytickersymbols, index_name=index_name)
    esg_details = get_esg_details(yahoo_ticker=index_stocks.yahoo_ticker)
    
    stocks_esg = pd.concat([index_stocks, esg_details], axis=1)

    return stocks_esg


def regex_strip_legalname(legal_firm_name):
    """Removes legal entity, technical description or firm type from firm name

    Args:
        legal_firm_names (list): strings with full firm names
        
    Returns:
        list: firm names without legal suffix 

    """

    pattern = r"""(\s|\.|\,|\&)*(\.com|Enterprise|Worldwide|Int\'l|N\.V\.|LLC|Co\b|Inc\b|Corp\w*|Group\sInc|Group|Company|Holdings\sInc|\WCo(\s|\.)|plc|Ltd|Int'l\.|AG|SE|Kommanditgesellschaft auf Aktien|KGaA|PLC|versicherungs-Gesellschaft|\.|Vz|KGaA St|Holdings\(?Class\s\w+\)?)\.?\W?"""
    stripped_names = re.sub(pattern,'', legal_firm_name)

    return stripped_names

def replace_firm_names(df, settings_path):
    """Replace firm names as specified in settings.yaml"""

    with open(settings_path, encoding='utf8') as file:
        settings = yaml.full_load(file)

    try: settings['query']['firm_name']
    except: logging.warning("No firm names specified in settings['query']['firm_name']. \
        Firm names still contain legal suffix which compromises search results.")
    assert "name" in df.columns , "Dataframe has no name column. Firm names cannot be replaced."

    replace_firm_names = settings['query']['firm_names']
    df['firm_name'] = df.name.replace(replace_firm_names, regex=True)

    return df

def get_esg_controversy_keywords(settings_path):
    """Load controversy keywords from settings.yaml"""

    with open(settings_path, encoding='utf8') as file:
        settings = yaml.full_load(file)

    controversies = settings['esg']['negative']

    return controversies

def remove_missing_esg_firms(esg_df, missing_placeholder="No fundamentals data"):
    """Drops firms that have no ESG scores. Placeholder from Yahoo"""
    return esg_df.loc[~esg_df.peerGroup.str.contains(missing_placeholder)]
    
def create_query_keywords(esg_df, keyword_list, explode=True):
    """Construct query keywords from firm_name and a list of keywords
    
    Args:
        esg_df (Dataframe): Data from yahooquery Ticker(yahoo_ticker).esg_scores, processed firm names
        keyword_list (list): list of strings that are attached to each firm name
        explode (boolean): If true re-shapes to logn format with each row having a unique query_keyword

    Returns:
        Dataframe: added query_keyword column (firm_name + keyword)

    """
    esg_df['query_keyword'] = esg_df.firm_name.apply(lambda x: [x+kw for kw in keyword_list])

    if explode: return esg_df.explode(column='query_keyword')
    else: return esg_df

def esg_firm_query_keywords_pipeline(pytickersymbols, index_name, path_to_settings):
    """ 

    Args:
        pytickersymbols (object): PyTickerSymbols() from pytickersymbols import PyTickerSymbols 
        index_name (string): Index name, one of PyTickerSymbols().get_all_indices()
        path_to_settings (string): path to settings.yaml, where all esg keywords are specified
    
    Returns:
        Dataframe: esg scores and related data from Yahoo!Finance incl. processed firm names and query keywords

    """
    controversy_keywords = get_esg_controversy_keywords(path_to_settings)
    esg_df = (get_index_firm_esg(pytickersymbols=pytickersymbols, index_name=index_name)
                        .pipe(replace_firm_names, settings_path=path_to_settings)
                        .pipe(remove_missing_esg_firms)
                        .pipe(create_query_keywords, keyword_list=controversy_keywords))

    return esg_df

esg_df = esg_firm_query_keywords_pipeline(pytickersymbols=PyTickerSymbols(), index_name='DAX', path_to_settings='../settings.yaml')
indices = PyTickerSymbols().get_all_indices()



'', esg_df


st.stop()





#---------------------------------------------------
# INTEREST OVER TIME
#---------------------------------------------------

from gtrends_extract import get_interest_over_time

keyword_list = ['abott labor strike', 'CenterPoint Energy greenwashing', 'abott greenwashing', 'abott transparency']

'', get_interest_over_time(keyword_list=keyword_list, 
    filepath='../data/raw/gtrend_test.csv', 
    filepath_failed='../data/raw/gtrend_test_failed.csv', max_retries=1, timeout=5)




#---------------------------------------------------
# VISUALS
#---------------------------------------------------

from datetime import datetime
import plotly.express as px
import chart_studio.plotly as cs

timeframe = f'2016-12-14 {datetime.now().strftime("%Y-%m-%d")}' 
date_index = get_query_date_index(timeframe=timeframe)
df_search_interest =  query_googletrends(keyword_list, date_index=date_index, timeframe=timeframe)
'', df_search_interest.set_index('date').resample('M')

import tsf_plots

def plot_interest_over_time(df):
    """line chart: weekly change of Google trends """
    fig = px.line(df, x="date", y="search_interest", color="keyword", 
                    line_shape='spline',
                  title='Search interest over time', 
                 labels={
                         "date": "",
                         "keyword": "", 
                         "search_interest": "Search interest"
                     },
                  # text = df.keyword
                 )
    # fig.update_traces(mode="markers+lines", hovertemplate="%{text}<br>" + "%{y:20.0f}Mio.<br>%{x}<extra></extra>") 
    
    # -- customize legend
    fig.update_layout(
        # legend=dict(
        # orientation="v",
        # yanchor="bottom",
        # y=0.9,
        # xanchor="right", 
        # x=0.5, 
        # bgcolor='rgba(0,0,0,0)'), # transparent  
        hovermode="closest",
    )
    return fig

def deploy_figure(figure, filename):    
    """ Upload graph to chartstudio """
    logging.info(f"Upload {filename} figure to plotly")
    cs.plot(figure, filename=filename)


tsf_plots.set_layout_template()
fig = plot_interest_over_time(df_search_interest)
st.plotly_chart(fig)
deploy_figure(figure=fig, filename='gtrends_greenwashing_sf')
