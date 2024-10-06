import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Function to fetch weather data from Open Meteo API
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

# Set the page config to wide
st.set_page_config(page_title="Climate Insights and Market Price Tracker", layout="wide")

# Sidebar for navigation and animation control
st.sidebar.title("Dashboard")
tabs = st.sidebar.radio("Choose a tab", ["Weather Data and Price Trends"])

# Animation control elements in the sidebar
animation_speed = st.sidebar.slider("Animation Speed (1 , 10 )", 1, 10, 5)
if st.sidebar.button("Start Animation"):
    st.session_state.animation_running = True

if st.sidebar.button("Stop Animation"):
    st.session_state.animation_running = False

# Set background style
st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://path_to_your_background_image.jpg");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Merged Weather Data and Price Trends tab
if tabs == "Weather Data and Price Trends":
    st.title("Climate Insights and Market Price Tracker")

    # Fetch and display weather data
    st.write("Fetching weather data...")
    weather_df = fetch_weather_data()

    # Date range selection
    start_date, end_date = st.date_input("Select Date Range", [weather_df['time'].min(), weather_df['time'].max()])
    weather_df = weather_df[(weather_df['time'] >= pd.to_datetime(start_date)) & (weather_df['time'] <= pd.to_datetime(end_date))]

    # Dropdown to select weather data type with "None" option
    weather_type = st.selectbox(
        "Select Weather Data Type",
        ["None", "Max Temperature (°C)", "Min Temperature (°C)"],
        index=0
    )

    # Map the display name to column name in the dataframe
    weather_mapping = {
        "Max Temperature (°C)": "temperature_2m_max",
        "Min Temperature (°C)": "temperature_2m_min"
    }
    selected_data = weather_mapping.get(weather_type)

    # Load and filter price data
    price_df_filtered = price_df[(price_df['Date'] >= pd.to_datetime(start_date)) & (price_df['Date'] <= pd.to_datetime(end_date))]
    
    # Dropdown to select commodity
    commodity = st.selectbox(
        "Select Commodity to View Price Trends",
        options=[col for col in price_df_filtered.columns if col != 'Date'],
        index=0
    )

    # Display the combined graph
    st.write("### Combined Weather and Price Data Plot")
    plot_container = st.empty()  # Use st.empty() to allow dynamic updates

    # Create a combined DataFrame for plotting
    combined_df = pd.DataFrame({
        'Date': weather_df['time'],
        'Weather': weather_df[selected_data] if selected_data else None,
        'Price': price_df_filtered[commodity].values[:len(weather_df)]
    })

    fig = px.line(combined_df, x='Date', y='Price', title='Price Trends Over Time', 
                   labels={'Price': commodity})

    if selected_data is not None:
        # Plot weather data if a valid type is selected
        fig.add_scatter(x=combined_df['Date'], y=combined_df['Weather'], mode='lines', 
                         name=f'{weather_type} of Weather', line=dict(color='red'))

    # Plot price trends
    fig.add_scatter(x=combined_df['Date'], y=combined_df['Price'], mode='lines', 
                     name=f'Price of {commodity}', line=dict(color='blue'))

    # Update layout for size
    fig.update_layout(
        width=1200,  # Set width to your desired value
        height=600,  # Set height to your desired value
        title_x=0.5  # Center the title
    )

    plot_container.plotly_chart(fig)

    # Animation logic using st.session_state
    if st.session_state.animation_running:
        speed = (11 - animation_speed) * 0.1  # Adjust speed according to the slider
        for i in range(1, len(combined_df) + 1):
            fig = px.line(combined_df[:i], x='Date', y='Price', title='Price Trends Over Time',
                           labels={'Price': commodity})

            if selected_data is not None:
                fig.add_scatter(x=combined_df[:i]['Date'], y=combined_df[:i]['Weather'], mode='lines', 
                                 name=f'{weather_type} of Weather', line=dict(color='red'))

            fig.add_scatter(x=combined_df[:i]['Date'], y=combined_df[:i]['Price'], mode='lines', 
                             name=f'Price of {commodity}', line=dict(color='blue'))

            # Update layout for size
            fig.update_layout(
                width=1200,  # Set width to your desired value
                height=600,  # Set height to your desired value
                title_x=0.5  # Center the title
            )

            plot_container.plotly_chart(fig)
            time.sleep(speed)  # Control animation speed

            # Check if the animation should stop
            if not st.session_state.animation_running:
                break
