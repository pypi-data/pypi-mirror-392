import pandas as pd
import plotly.express as px

def generate_bar_graph(data, x_col, y_col, title):
    """
    Generate a Plotly bar graph and return as HTML string.
    """
    df = pd.DataFrame(data)

    if df.empty:
        return "<p>No data available to display.</p>"

    fig = px.bar(df, x=x_col, y=y_col, title=title)

    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        title={'x': 0.5},
        bargap=0.2
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')
