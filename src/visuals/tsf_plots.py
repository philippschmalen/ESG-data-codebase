"""
Make visualizations with plotly
"""
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime


def set_layout_template():
    """Creates watermarks and applies colors"""
    watermark_date = "Updated {}".format(datetime.now().strftime("%d.%B%Y"))
    watermark_url = "towardssustainablefinance.com"

    tsf_colorscale = [
        "#4d886d",
        "#f3dab9",
        "#9bcab8",
        "#829fa5",
        "#dc9b4d",
        "#4a82a1",
        "#cfaea5",
        "#D5E6E0",
    ]

    pio.templates["tsf"] = go.layout.Template(
        layout_colorway=tsf_colorscale,
        layout_hovermode="closest",
        layout_font_family="Verdana",
        layout_annotations=[
            dict(
                name="watermark",
                text=watermark_url,
                textangle=0,
                opacity=0.65,
                font=dict(color="#545454", size=20),
                xref="paper",
                yref="paper",
                x=1,
                y=-0.15,
                showarrow=False,
            ),
            dict(
                name="watermark2",
                text=watermark_date,
                textangle=0,
                opacity=0.65,
                font=dict(color="#545454", size=16),
                xref="paper",
                yref="paper",
                x=0,
                y=0.1,
                showarrow=False,
            ),
        ],
    )
    pio.templates.default = "tsf"
