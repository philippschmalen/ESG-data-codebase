"""
Central place to make analyses
Loads modules form src
"""

import streamlit as st


import plotly.express as px
import pandas as pd

from datetime import datetime
from glob import glob

import src.data.data_utilities as data_utils
import src.data.gtrends_extract as gt
import src.visuals.plotly_utilities as plt_utils

# TODO: could insert view selection a la awesome streamlit
# https://github.com/MarcSkovMadsen/awesome-streamlit/blob/master/app.py


st.title("Towards sustainable finance - visuals")


# ----------------------------------------
# -- query search interest
# How to load data from Google trands:
# ----------------------------------------
keywords = ["greenwashing", "sustainable finance"]
if st.sidebar.button(
    f"Get current search interest for\n {', '.join(str(x) for x in keywords)}"
):
    ts = data_utils.timestamp_now()
    timeframe = "today 5-y"  # f'2019-06-01 {datetime.utcnow().strftime("%Y-%m-%d")}'
    filepath = f"./data/raw/greenwashing_{ts}.csv"
    filepath_failed = f"./data/raw/greenwashing_FAILED_{ts}.csv"

    search_interest = gt.get_interest_over_time(
        keyword_list=keywords,
        filepath=filepath,
        filepath_failed=filepath_failed,
        timeframe=timeframe,
    )

    st.info(f"Loaded CSV to {filepath}.")


# ----------------------------------------
# -- load data
# ----------------------------------------
raw_data_csv_files = st.sidebar.selectbox(
    "Select data",
    options=glob("data/raw/*csv"),
    format_func=lambda x: x.split("\\")[-1],
)
df_raw = data_utils.load_data(
    filepath=raw_data_csv_files, parse_dates=["date"]
).set_index("date")


df = data_utils.group_search_interest_on_time_unit(df=df_raw)

# ----------------------------------------
# -- Main plot
# ----------------------------------------
plt_utils.set_layout_template(colorscale=plt_utils.load_colorscale("settings.yaml"))

fig = px.line(
    df,
    x="date",
    y="search_interest",
    color="keyword",
    line_shape="spline",
    title="Google search interest",
    labels={"date": "", "search_interest": "Search interest"},
    template="tsf",
)


# logo
fig.add_layout_image(
    dict(
        source="https://i.ibb.co/K0cfVFs/plot-thumbnail-white.png",
        xref="paper",
        yref="paper",
        x=1,
        y=1,
        sizex=0.3,
        sizey=0.3,
        xanchor="right",
        yanchor="bottom",
    )
)

# layout tweaks
fig.update_traces(line=dict(width=5))  # thicker line
fig.update_layout(
    plot_bgcolor="white", legend=dict(x=0.1, y=0.9, title="")
)  # white background

st.plotly_chart(fig)
