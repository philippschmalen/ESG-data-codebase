"""
Make visualizations with plotly
"""
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime


def set_layout_template(template_name="tsf", show_legend=True):
    """Creates watermarks and applies colors"""
    # watermark_date = "Updated {}".format(datetime.now().strftime("%d.%B%Y"))
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
        layout_font_family="Verdana",
        layout_title_font=dict(size=24),
        layout_font=dict(size=16),
        layout_plot_bgcolor="#FFFFFF",
        layout_paper_bgcolor="#FFFFFF",
        layout_showlegend=show_legend,
        layout_xaxis=dict(showgrid=False, zeroline=False),
        layout_yaxis=dict(showgrid=False, zeroline=False),
        layout_hovermode="closest",
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
                y=-0.17,
                showarrow=False,
            ),
            # dict(
            #     name="watermark2",
            #     text=watermark_date,
            #     textangle=0,
            #     opacity=0.65,
            #     font=dict(color="#545454", size=16),
            #     xref="paper",
            #     yref="paper",
            #     x=0,
            #     y=-0.15,
            #     showarrow=False,
            # ),
        ],
    )
    pio.templates.default = "tsf"
