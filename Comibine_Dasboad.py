from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.express as px

# Load the price trend data
file_path = "/Users/harshadshingde/Downloads/excel_maharastra.csv"
df = pd.read_csv(file_path)

# Convert 'Date' column to datetime format and handle day-first dates
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

# Filter out non-numeric columns and resample for daily data
numeric_columns = df.select_dtypes(include='number').columns
df_numeric = df[['Date'] + list(numeric_columns)]  # Keep 'Date' and numeric columns only
df_numeric = df_numeric.set_index('Date').resample('D').mean().reset_index()

# Fetch data from Open Meteo API
def fetch_weather_data():
    url = 'https://archive-api.open-meteo.com/v1/archive?latitude=21.1463&longitude=79.0849&start_date=2022-05-01&end_date=2024-09-04&hourly=rain,soil_temperature_0_to_7cm&daily=weather_code,temperature_2m_max,temperature_2m_min,rain_sum&timezone=auto'
    response = requests.get(url)
    data = response.json()

    # Process daily data into a DataFrame
    daily_data = data['daily']
    df_weather = pd.DataFrame(daily_data)
    df_weather['time'] = pd.to_datetime(df_weather['time'])
    return df_weather

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Data Dashboard", className='text-center mb-4'), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Select Data Type"),
            dcc.Dropdown(
                id='data-type-dropdown',
                options=[
                    {'label': 'Price Trends', 'value': 'price'},
                    {'label': 'Weather Data', 'value': 'weather'}
                ],
                value='price',  # Default selection
                clearable=False
            )
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Select Date Range"),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=df['Date'].min(),
                max_date_allowed=df['Date'].max(),
                start_date=df['Date'].min(),
                end_date=df['Date'].max()
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='data-graph-container')
        ], width=12)
    ])
])

# Callback to update the displayed graph based on selected data type
@app.callback(
    Output('data-graph-container', 'children'),
    Input('data-type-dropdown', 'value')
)
def update_graph(selected_data_type):
    if selected_data_type == 'price':
        return [
            html.H5("Select Price Data to View"),
            dcc.Dropdown(
                id='price-dropdown',
                options=[{'label': col, 'value': col} for col in numeric_columns],
                value=numeric_columns[0],
                clearable=False
            ),
            dcc.Graph(id='price-trend-graph'),
        ]
    else:
        return [
            html.H5("Select Weather Data to View"),
            dcc.Dropdown(
                id='weather-dropdown',
                options=[
                    {'label': 'Max Temperature (°C)', 'value': 'temperature_2m_max'},
                    {'label': 'Min Temperature (°C)', 'value': 'temperature_2m_min'},
                    {'label': 'Rainfall (mm)', 'value': 'rain_sum'}
                ],
                clearable=False
            ),
            dcc.Graph(id='weather-graph'),
        ]

# Callback to update the price trend graph
@app.callback(
    Output('price-trend-graph', 'figure'),
    [Input('price-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_price_graph(selected_column, start_date, end_date):
    # Filter data between the selected date range
    df_filtered = df_numeric[(df_numeric['Date'] >= start_date) & (df_numeric['Date'] <= end_date)]
    
    fig = px.line(df_filtered, x='Date', y=selected_column, title=f'Price Trends: {selected_column}')
    
    # Update layout to add background color and increase height
    fig.update_layout(
        height=750,  # Set the height of the graph
        yaxis=dict(scaleanchor="x", scaleratio=2),  # Adjust aspect ratio
        plot_bgcolor="lightgray",  # Set plot background color
        paper_bgcolor="lightblue",  # Set the paper background color (outside plot)
    )
    
    return fig

# Callback to update the weather graph based on selected data type and date range
@app.callback(
    Output('weather-graph', 'figure'),
    [Input('weather-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_weather_graph(selected_data, start_date, end_date):
    if selected_data is None:
        # Return an empty figure
        return {
            "layout": {
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Weather Data"},
                "title": "Select a data type to display"
            }
        }
    
    df_weather = fetch_weather_data()

    # Filter data between the selected date range
    df_filtered = df_weather[(df_weather['time'] >= start_date) & (df_weather['time'] <= end_date)]

    # Plot the selected weather data
    fig = px.line(df_filtered, x='time', y=selected_data, title=f'{selected_data.replace("_", " ").title()} Over Time')
    
    # Update layout to add background color and height
    fig.update_layout(
        height=750,  # Set the height of the graph
        plot_bgcolor="lightgray",  # Set plot background color
        paper_bgcolor="lightblue",  # Set the paper background color (outside plot)
        xaxis_title='Date',
        yaxis_title=selected_data.replace("_", " ").title()
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
