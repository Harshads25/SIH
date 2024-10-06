import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Function to fetch weather data from Open Meteo API
def fetch_weather_data():"/Users/harshadshingde/Downloads/excel_maharastra (1).csv"
def fetch_weather_data():
    url = ('https://archive-api.open-meteo.com/v1/archive?'
           'latitude=21.455335357109544&longitude=78.95753859046016&'
           'start_date=2024-05-01&end_date=2024-09-04&hourly=soil_temperature_0_to_7cm&'
           'daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto')
       
    response = requests.get(url)
    data = response.json()

    # Process daily data into a DataFrame
    daily_data = data['daily']
    df = pd.DataFrame(daily_data)
    df['time'] = pd.to_datetime(df['time'])
    return df

# Function to load price trend data
def load_price_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])  # Ensure 'Date' column is parsed as datetime
    return df

# File path for price data
price_data_file_path = "/Users/harshadshingde/Downloads/excel_maharastra.csv"
price_df = load_price_data(price_data_file_path)

# Initialize session state variables
if "animation_running" not in st.session_state:
    st.session_state.animation_running = False

# Sidebar for navigation and animation control
st.sidebar.title("Dashboard")
tabs = st.sidebar.radio("Choose a tab", ["Weather Data", "Price Trends"])

# Animation control elements in the sidebar
animation_speed = st.sidebar.slider("Animation Speed (1 , 10 )", 1, 10, 5)
if st.sidebar.button("Start Animation"):
    st.session_state.animation_running = True

if st.sidebar.button("Stop Animation"):
    st.session_state.animation_running = False

# Weather Data tab
if tabs == "Weather Data":
    st.title("Climate Insights")

    # Fetch and display weather data
    st.write("Fetching weather data...")
    weather_df = fetch_weather_data()

    # Dropdown to select weather data type
    weather_type = st.selectbox(
        "Select Weather Data Type",
        ["Max Temperature (°C)", "Min Temperature (°C)", "Rainfall (mm)"],
        index=0
    )

    # Map the display name to column name in the dataframe
    weather_mapping = {
        "Max Temperature (°C)": "temperature_2m_max",
        "Min Temperature (°C)": "temperature_2m_min",
        "Rainfall (mm)": "rain_sum"
    }
    selected_data = weather_mapping[weather_type]
    
    # Display the initial graph
    st.write("### Weather Data Plot")
    plot_container = st.empty()  # Use st.empty() to allow dynamic updates
    fig = px.line(weather_df, x='time', y=selected_data, title=f'{weather_type} Over Time')
    plot_container.plotly_chart(fig)
    
    # Animation logic using st.session_state
    if st.session_state.animation_running:
        speed = (11 - animation_speed) * 0.1  # Adjust speed according to the slider
        for i in range(1, len(weather_df) + 1):
            fig = px.line(weather_df[:i], x='time', y=selected_data, title=f'{weather_type} Over Time')
            fig.update_layout(xaxis_title='Date', yaxis_title=weather_type)
            plot_container.plotly_chart(fig)
            
            # Use the st.empty() to update dynamically without blocking the UI
            time.sleep(speed)  # Control animation speed

            # Check if the animation should stop
            if not st.session_state.animation_running:
                break

# Price Trends tab
elif tabs == "Price Trends":
    st.title("Market Price Tracker")

    # Dropdown to select commodity
    commodity = st.selectbox(
        "Select Commodity to View Price Trends",
        options=[col for col in price_df.columns if col != 'Date'],
        index=0
    )

    # Display the initial graph
    st.write("### Price Trends Plot")
    plot_container = st.empty()
    fig = px.line(price_df, x="Date", y=commodity, title=f'Price Trends: {commodity}')
    plot_container.plotly_chart(fig)

    # Animation logic using st.session_state
    if st.session_state.animation_running:
        speed = (11 - animation_speed) * 0.1  # Adjust speed according to the slider
        for i in range(1, len(price_df) + 1):
            fig = px.line(price_df[:i], x="Date", y=commodity, title=f'Price Trends: {commodity}')
            fig.update_layout(xaxis_title='Date', yaxis_title='Price')
            plot_container.plotly_chart(fig)
            
            # Use the st.empty() to update dynamically without blocking the UI
            time.sleep(speed)  # Control animation speed

            # Check if the animation should stop
            if not st.session_state.animation_running:
                break
