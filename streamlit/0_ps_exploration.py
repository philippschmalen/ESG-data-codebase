# -*- coding: utf-8 -*-
import streamlit as st

import logging
import pandas as pd

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

def get_index_firm_esg(pytickersymbols, index_name):
    index_stocks = get_index_stock_details(pytickersymbols=pytickersymbols, index_name=index_name)
    esg_details = get_esg_details(yahoo_ticker=index_stocks.yahoo_ticker)
    
    stocks_esg = pd.concat([index_stocks, esg_details], axis=1)

    return stocks_esg
    



pts = PyTickerSymbols()
indices = PyTickerSymbols().get_all_indices()

'', get_index_firm_esg(pytickersymbols=pts, index_name='DAX')

st.stop()


dax = get_index_stock_details(pytickersymbols=pts, index_name='DAX')
# eu_stoxx = get_index_stock_details(pytickersymbols=pts, index_name="EURO STOXX 50")
# cac_40 = get_index_stock_details(pytickersymbols=pts, index_name="CAC 40")
# omx = get_index_stock_details(pytickersymbols=pts, index_name="OMX Helsinki 25")
# sp500 = get_index_stock_details(pytickersymbols=pts, index_name="S&P 500")

esg_df = get_esg_details(yahoo_ticker=dax.yahoo_ticker)

'', pd.concat([dax, esg_df], axis=1)

# dax_details = Ticker(dax.yahoo_ticker.to_list())
# 'ESG data', pd.DataFrame(dax_details.esg_scores).T

# NEXT: 


#---------------------------------------------------
# CONSTRUCT KEYWORDS
#---------------------------------------------------




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
