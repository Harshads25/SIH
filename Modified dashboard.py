import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

# Function to fetch weather data from Open Meteo API
def fetch_weather_data():
    url = ('https://archive-api.open-meteo.com/v1/archive?latitude=21.1463&longitude=79.0849&start_date=2024-05-01&end_date=2024-09-04&hourly=soil_temperature_0_to_7cm&daily=temperature_2m_max,temperature_2m_min,rain_sum&timezone=auto')
    
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

# File path for price data, background, and logo
price_data_file_path = "/Users/harshadshingde/Downloads/excel_maharastra.csv"
logo_path = "/Users/harshadshingde/Desktop/SIH/Arthex.png"
background_path = "/Users/harshadshingde/Desktop/SIH/Bagraoud.jpg"  # Change to JPEG if AVIF fails

# Load price data
price_df = load_price_data(price_data_file_path)

# Initialize session state variables
if "animation_running" not in st.session_state:
    st.session_state.animation_running = False

# Set the page config to wide
st.set_page_config(page_title="Climate Insights and Market Price Tracker", layout="wide")

# Custom CSS to add the background image and display the logo in the corner
st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url('file://{background_path}');
        background-size: cover;
        background-position: center;
        height: 100vh;  /* Set height to cover the full view */
        width: 100%;  /* Set width to cover the full view */
    }}
    .logo {{
        position: fixed;
        top: 10px;
        right: 10px;
        width: 150px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Display the logo using Streamlit's st.image()
st.image(logo_path, width=150, caption="Arthex", use_column_width=False)

# Sidebar for navigation and animation control
st.sidebar.title("Dashboard")
tabs = st.sidebar.radio("Choose a tab", ["Weather Data and Price Trends", "Cumulative Rain Effect on Price Trends"])

# Animation control elements in the sidebar
animation_speed = st.sidebar.slider("Animation Speed (1 , 10 )", 1, 10, 5)
if st.sidebar.button("Start Animation"):
    st.session_state.animation_running = True

if st.sidebar.button("Stop Animation"):
    st.session_state.animation_running = False

# The rest of your code goes here...

# Merged Weather Data and Price Trends tab
if tabs == "Weather Data and Price Trends":
    st.title("Climate Insights and Market Price Tracker")

    # Fetch and display weather data
    st.write("Fetching weather data...")
    weather_df = fetch_weather_data()

    # Dropdown to select weather data type with "None" option
    weather_type = st.selectbox(
        "Select Weather Data Type",
        ["None", "Max Temperature (°C)", "Min Temperature (°C)", "Rainfall (mm)"],
        index=0
    )

    # Map the display name to column name in the dataframe
    weather_mapping = {
        "Max Temperature (°C)": "temperature_2m_max",
        "Min Temperature (°C)": "temperature_2m_min",
        "Rainfall (mm)": "rain_sum"
    }
    selected_data = weather_mapping.get(weather_type)

    # Load price data
    price_df_filtered = price_df

    # Dropdown to select commodity
    commodity = st.selectbox(
        "Select Commodity to View Price Trends",
        options=[col for col in price_df_filtered.columns if col != 'Date'],
        index=0
    )

    # Display the combined graph with separate y-axes
    st.write("### Combined Weather and Price Data ")
    plot_container = st.empty()  # Use st.empty() to allow dynamic updates

    # Create a combined DataFrame for plotting
    combined_df = pd.DataFrame({
        'Date': weather_df['time'],
        'Weather': weather_df[selected_data] if selected_data else None,
        'Price': price_df_filtered[commodity].values[:len(weather_df)]
    })

    # Plot with secondary y-axis for weather and price
    fig = go.Figure()

    # Add price data
    fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Price'], mode='lines', name=f'Price of {commodity}', yaxis="y1", line=dict(color='blue')))

    if selected_data is not None:
        # Add weather data on secondary y-axis
        fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Weather'], mode='lines', name=f'{weather_type}', yaxis="y2", line=dict(color='red')))

    # Set up layout for separate y-axes
    fig.update_layout(
        width=1200,
        height=600,
        title='Price and Weather Trends with Separate Y-Axes',
        xaxis_title='Date',
        yaxis=dict(
            title='Price',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=weather_type if selected_data else '',
            titlefont=dict(color='red'),
            tickfont=dict(color='red'),
            overlaying='y',
            side='right'
        ),
        title_x=0.5
    )

    plot_container.plotly_chart(fig)

    # Animation logic using st.session_state
    if st.session_state.animation_running:
        speed = (11 - animation_speed) * 0.1  # Adjust speed according to the slider
        for i in range(1, len(combined_df) + 1):
            fig = go.Figure()

            # Add price data
            fig.add_trace(go.Scatter(x=combined_df['Date'][:i], y=combined_df['Price'][:i], mode='lines', name=f'Price of {commodity}', yaxis="y1", line=dict(color='blue')))

            if selected_data is not None:
                fig.add_trace(go.Scatter(x=combined_df['Date'][:i], y=combined_df['Weather'][:i], mode='lines', name=f'{weather_type}', yaxis="y2", line=dict(color='red')))

            # Update layout for separate y-axes
            fig.update_layout(
                width=1200,
                height=600,
                title='Price and Weather Trends with Separate Y-Axes',
                xaxis_title='Date',
                yaxis=dict(
                    title='Price',
                    titlefont=dict(color='blue'),
                    tickfont=dict(color='blue')
                ),
                yaxis2=dict(
                    title=weather_type if selected_data else '',
                    titlefont=dict(color='red'),
                    tickfont=dict(color='red'),
                    overlaying='y',
                    side='right'
                ),
                title_x=0.5
            )

            plot_container.plotly_chart(fig)
            time.sleep(speed)

            if not st.session_state.animation_running:
                break

# Cumulative Rain Effect on Price Trends tab
if tabs == "Cumulative Rain Effect on Price Trends":
    st.title("Cumulative Effect of Rainfall on Price Trends")

    # Fetch weather data
    weather_df = fetch_weather_data()

    # Filter the weather data for rainfall
    rain_df = weather_df[['time', 'rain_sum']]

    # Filter price data
    price_df_filtered = price_df

    # Select commodity
    commodity = st.selectbox(
        "Select Commodity to View Price Trends During Rainfall",
        options=[col for col in price_df_filtered.columns if col != 'Date'],
        index=0
    )

    # Calculate cumulative rainfall over the past 7 days
    cumulative_rain = rain_df['rain_sum'].rolling(window=7).sum().fillna(0)  # 7-day rolling sum
    combined_cumulative_df = pd.DataFrame({
        'Date': rain_df['time'],
        '7-Day Cumulative Rainfall (mm)': cumulative_rain,
        'Price': price_df_filtered[commodity].values[:len(rain_df)]
    })

    # Create the graph for cumulative rainfall and its effect on price trends
    st.write("### Cumulative Rainfall and Price Trends")
    fig_cumulative = go.Figure()

    # Plot cumulative rainfall
    fig_cumulative.add_trace(go.Scatter(x=combined_cumulative_df['Date'], y=combined_cumulative_df['7-Day Cumulative Rainfall (mm)'], mode='lines', name='7-Day Cumulative Rainfall (mm)', yaxis="y2", line=dict(color='green')))

    # Plot price trends
    fig_cumulative.add_trace(go.Scatter(x=combined_cumulative_df['Date'], y=combined_cumulative_df['Price'], mode='lines', name=f'Price of {commodity}', yaxis="y1", line=dict(color='blue')))

    # Set up layout for separate y-axes
    fig_cumulative.update_layout(
        width=1200,
        height=600,
        title='Cumulative Rainfall and Price Trends',
        xaxis_title='Date',
        yaxis=dict(
            title='Price',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title='7-Day Cumulative Rainfall (mm)',
            titlefont=dict(color='green'),
            tickfont=dict(color='green'),
            overlaying='y',
            side='right'
        ),
        title_x=0.5
    )

    st.plotly_chart(fig_cumulative)
