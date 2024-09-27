from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# Load the data
df = pd.read_csv("/Users/harshadshingde/Downloads/excel_maharastra.csv")

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Price Trends and Prediction Dashboard"),
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        value=df.columns[1]  # Default value
    ),
    dcc.Graph(id='price-trend-graph'),
    html.Div(id='data-table'),
])

@app.callback(
    Output('price-trend-graph', 'figure'),
    [Input('column-dropdown', 'value')]
)
def update_graph(selected_column):
    fig = px.line(df, x="Date", y=selected_column, title=f'Price Trends: {selected_column}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
