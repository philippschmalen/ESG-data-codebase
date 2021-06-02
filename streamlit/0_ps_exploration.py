# -*- coding: utf-8 -*-
import streamlit as st

import logging
import pandas as pd
import yaml
import plotly.express as px

import sys
sys.path.append('../')
sys.path.append('../src/data')
sys.path.append('../src/visualization')


from pytickersymbols import PyTickerSymbols
import src.data.yahoofinance_extract as yq
from src.data.gtrends_extract import get_interest_over_time
from tsf_plots import set_layout_template


esg_df = yq.esg_firm_query_keywords_pipeline(index_name='DAX', path_to_settings='../settings.yaml')
indices = PyTickerSymbols().get_all_indices()

trends_df = get_interest_over_time(keyword_list=esg_df.query_keyword, 
    filepath='../data/raw/dax_search_interest_020621.csv', 
    filepath_failed='../data/raw/failed_dax_search_interest_020621.csv')

# '', trends_df

# join esg and gtrends 
# search_interest = pd.read_csv(filepath).set_index('keyword', drop=False)
# esg_df = esg_df.set_index('query_keyword', drop=False)
# search_interest.join(esg_df)


# set_layout_template()
# fig_over_time = px.scatter(df, x='date', y='search_interest', color='keyword')
# st.plotly_chart(fig_over_time)



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
