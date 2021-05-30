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

    return index_details


pts = PyTickerSymbols()
indices = PyTickerSymbols().get_all_indices()


dax = get_index_stock_details(pytickersymbols=pts, index_name='DAX')
eu_stoxx = get_index_stock_details(pytickersymbols=pts, index_name="EURO STOXX 50")
cac_40 = get_index_stock_details(pytickersymbols=pts, index_name="CAC 40")
omx = get_index_stock_details(pytickersymbols=pts, index_name="OMX Helsinki 25")
sp500 = get_index_stock_details(pytickersymbols=pts, index_name="S&P 500")

'Indices ', dax.yahoo_ticker.to_list()

# which ticker to use? --> symbols[1]['yahoo']
dax_details = Ticker(dax.yahoo_ticker.to_list())

'', pd.DataFrame(dax_details.summary_detail)

st.stop()

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
