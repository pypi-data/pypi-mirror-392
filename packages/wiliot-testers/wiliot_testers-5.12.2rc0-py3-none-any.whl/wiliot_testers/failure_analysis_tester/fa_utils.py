from jinja2 import Template
import numpy as np
import pandas as pd
from pathlib import Path
import plotly.io as pio
import plotly.graph_objects as go
from typing import Union


def plot_value(df: pd.DataFrame, reference_df: Union[pd.DataFrame, None], value: str, tag_alias: str = '') -> go.Figure:
    def denan(arr):
        """Remove NaN values from an array."""
        return arr[~np.isnan(arr)]
    fig = go.Figure()
    for tag in df['tag_alias'].unique():
        p_df = df[df['tag_alias'] == tag]
        fig.add_trace(go.Scatter(
            x=p_df[value + '_current_uA'].values, 
            y=p_df[value + '_voltage_V'].values, 
            mode='markers', 
            name=str(tag),
            marker=dict(size=6)
        ))

    if reference_df is not None and value + '_current_uA' in reference_df.columns:
        x_ref = denan(reference_df[value + '_current_uA'].values)
        lower_limit = denan(reference_df[value + '_min_voltage'].values)
        upper_limit = denan(reference_df[value + '_max_voltage'].values)
        
        # Add red dashed lines for control limits
        fig.add_trace(go.Scatter(
            x=x_ref, 
            y=lower_limit, 
            mode='lines+markers',
            name="Min Control Limit",
            line=dict(color='red', dash='dash', width=2),
            marker=dict(color='red', size=4)
        ))
        fig.add_trace(go.Scatter(
            x=x_ref, 
            y=upper_limit, 
            mode='lines+markers',
            name="Max Control Limit",
            line=dict(color='red', dash='dash', width=2),
            marker=dict(color='red', size=4)
        ))
        
        # Add shaded area between control limits
        fig.add_trace(go.Scatter(
            x=x_ref,
            y=upper_limit,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=x_ref,
            y=lower_limit,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.2)',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    chart_title = f"{tag_alias}_{value}" if tag_alias else f"Test_{value}"
    
    fig.update_layout(
        title=chart_title,
        showlegend=True,
        xaxis_title="Current [uA]", 
        yaxis_title="Voltage [V]",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='black',
            borderwidth=1
        )
    )

    return fig


def generate_html_report(list_for_report:list, output_path:Path, main_plot:list):
    """
    Generate an HTML report from a list of test result dictionaries.
    The keys are extracted from the dictionary, the only required key is:
    - 'graph': plotly.graph_objects.Figure | None
    """
    # Convert plotly figures to HTML snippets
    for item in list_for_report:
        item['graph_html'] = pio.to_html(item['graph'], include_plotlyjs=True, full_html=False) if item['graph'] is not None else None

    main_plot_html = []
    for p in main_plot:
        main_plot_html.append(pio.to_html(p, include_plotlyjs=True, full_html=False))

    # Jinja2 HTML template
    template = Template("""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>Test Report</h1>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr>
                {% for col in cols %}
                <th>{{col}}</th>
                {% endfor %}
            </tr>
            {% for row in results %}
            <tr>
                {% for col in cols %}
                <td>{{ row[col] }}</td>
                {% endfor %}
            </tr>
            {% if row['graph_html'] is not none %}
            <tr>
                <td colspan="4">{{ row['graph_html'] | safe }}</td>
            </tr>
            {% endif %}
            {% endfor %}
        </table>
        {% if main_plot_html %}
        <h1>All Results</h1>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            {% for p in main_plot_html %}
            <tr>
                <td colspan="4">{{ p | safe }}</td>
            </tr>
            {% endfor %}
        {% endif %}
        </table>
    </body>
    </html>
    """)

    # Render and save
    cols = list(list_for_report[0].keys())
    if 'graph' in cols: cols.remove('graph')
    if 'graph_html' in cols: cols.remove('graph_html')
    html_output = template.render(results=list_for_report, cols=cols, main_plot_html=main_plot_html)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

if __name__ == '__main__':
    l = []
    l.append({'Test Name': 'col','Tag Id': 'tag_alias','percent_pass': 54.3214235,'result': 'N/A','graph': None})
    l.append({'Test Name': 'col','Tag Id': 'tag_alias','percent_pass': None,'result': 'N/A','graph': None})
    generate_html_report(l, Path('/Users/eilam.sher/Downloads/report/report.html'),[])
