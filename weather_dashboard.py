import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.express as px

# Fetch data from Open Meteo API
def fetch_weather_data():
    url = 'https://archive-api.open-meteo.com/v1/archive?latitude=21.1463&longitude=79.0849&start_date=2022-05-01&end_date=2024-09-04&hourly=rain,soil_temperature_0_to_7cm&daily=weather_code,temperature_2m_max,temperature_2m_min,rain_sum&timezone=auto'
    response = requests.get(url)
    data = response.json()

    # Process daily data into a DataFrame
    daily_data = data['daily']
    df = pd.DataFrame(daily_data)
    df['time'] = pd.to_datetime(df['time'])
    return df

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Weather Data Dashboard", className='text-center mb-4'), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Select Weather Data to View"),
            dcc.Dropdown(id='data-dropdown', options=[
                {'label': 'Max Temperature (°C)', 'value': 'temperature_2m_max'},
                {'label': 'Min Temperature (°C)', 'value': 'temperature_2m_min'},
                {'label': 'Rainfall (mm)', 'value': 'rain_sum'}
            ], multi=False, placeholder="Select a data type"),
            dcc.Graph(id='weather-graph')
        ], width=8)
    ]),
])

# Callback to update graph based on selected data type
@app.callback(
    Output('weather-graph', 'figure'),
    [Input('data-dropdown', 'value')]
)
def update_weather_graph(selected_data):
    if selected_data is None:
        # Return an empty figure
        return {
            "layout": {
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Weather Data"},
                "title": "Select a data type to display"
            }
        }
    
    df = fetch_weather_data()

    # Plot the selected data
    fig = px.line(df, x='time', y=selected_data, title=f'{selected_data.replace("_", " ").title()} Over Time')
    fig.update_layout(xaxis_title='Date', yaxis_title=selected_data.replace("_", " ").title())

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
