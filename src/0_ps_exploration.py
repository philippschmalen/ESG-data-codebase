# -*- coding: utf-8 -*-
import streamlit as st

import logging
import pandas as pd
import yaml
from glob import glob
from datetime import datetime
import plotly.express as px
import chart_studio.plotly as cs
import visuals.tsf_plots as plot

from pytickersymbols import PyTickerSymbols
import data.yahoofinance_extract as yq
from data.gtrends_extract import get_interest_over_time, get_query_date_index
from data.data_utilities import timestamp_now


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

csv = st.sidebar.selectbox(
    "Select csv file from raw data", options=glob("../data/raw/*csv"), 
    format_func=lambda x: x.split('\\')[-1]
)

# load data with 
df_raw = pd.read_csv(csv, parse_dates=["date"])
df = df_raw.set_index("date").groupby("keyword").resample("M").mean().reset_index()


# ---------------------------------------------------
# QUERIES
# ---------------------------------------------------

index_name = "DAX"

if st.sidebar.checkbox(f"Run query for {index_name}"):
    esg_df = yq.esg_firm_query_keywords_pipeline(
        index_name="DAX", path_to_settings="../settings.yaml"
    )

    indices = PyTickerSymbols().get_all_indices()

    trends_df = get_interest_over_time(
        keyword_list=esg_df.query_keyword[:100],
        filepath=f"../data/raw/dax_search_interest_{timestamp_now()}.csv",
        filepath_failed=f"../data/raw/failed_dax_search_interest_{timestamp_now()}.csv",
    )

keyword_list = ["greenwashing", "sustainable finance", "msci", "esg"]
selected_keywords = st.sidebar.multiselect("Select keywords", options=keyword_list)

if st.sidebar.checkbox(f"Run query for {selected_keywords}"):
    timeframe = f'2016-12-14 {datetime.now().strftime("%Y-%m-%d")}'
    df_search_interest = get_interest_over_time(
        keyword_list=selected_keywords, timeframe=timeframe, 
        filepath=f"../data/raw/{selected_keywords[0]}_trends_{timestamp_now()}.csv",
        filepath_failed=f"../data/raw/{selected_keywords[0]}_trends_{timestamp_now()}.csv"
    )


# ---------------------------------------------------
# VISUALS
# ---------------------------------------------------

def plot_interest_over_time(df, title):
    """line chart: weekly change of Google trends"""
    fig = px.line(
        df,
        x="date",
        y="search_interest",
        color="keyword",
        line_shape="spline",
        title=title,
        labels={"date": "", "keyword": "", "search_interest": "Search interest"},
    )

    # layout tweaks
    fig.update_traces(line=dict(width=5))  # thicker line
    fig.update_layout(plot_bgcolor="white")  # white background

    # -- customize legend
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.8,
        xanchor="right", 
        x=0.4, 
        bgcolor='rgba(0,0,0,0)'), # transparent  
        hovermode="closest",
    )

    fig.update_layout()
    return fig


def deploy_figure(figure, filename):
    """Upload graph to chartstudio"""
    logging.info(f"Upload {filename} figure to plotly")
    cs.plot(figure, filename=filename)


plot.set_layout_template()
fig = plot_interest_over_time(df, title=f"Google search interest")
st.plotly_chart(fig)

if st.sidebar.checkbox("Deploy figure to chart studio"):
    deploy_figure(figure=fig, filename="gtrends_greenwashing_sf")
