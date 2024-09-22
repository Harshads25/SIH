from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

# Directory where your files are stored
# directory = r"C:\SIH"

chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode
chrome_options.add_argument('--ignore-certificate-errors')  # Ignore SSL errors
driver = webdriver.Chrome(options=chrome_options)


# Columns to store the extracted data
columns = ['Date', 'States/UTs', 'Rice', 'Wheat', 'Atta', 'Gram Dal', 'Tur/Arhar Dal', 'Urad Dal', 'Moong Dal', 
           'Masoor Dal', 'Sugar', 'Milk', 'Groundnut Oil', 'Mustard Oil', 'Vanaspati', 'Soya Oil', 'Sunflower Oil', 
           'Palm Oil', 'Gur', 'Tea', 'Salt', 'Potato', 'Onion', 'Tomato']

# Initialize an empty DataFrame to store all the extracted data
all_data = pd.DataFrame()

today = datetime(2024, 9, 20)

# List of commodities to extract
commodities_of_interest = ['Rice', 'Wheat', 'Potato', 'Onion', 'Tomato']

# Loop through all the files in the directory
try:
    # Loop over the last 3 years
    for i in range(3 * 365):
        date = today - timedelta(days=i)
        date_str = date.strftime("%d/%m/%Y")  # Format the date as needed for the input field

        # Step 1: Open the website
        driver.get('https://fcainfoweb.nic.in/reports/report_menu_web.aspx')

        # Step 2: Wait for the "Price report" radio button to appear and select it
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_MainContent_Rbl_Rpt_type_0"))
        ).click()

        # Step 3: Wait for the dropdown to appear and select "Daily Prices"
        dropdown_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Ddl_Rpt_Option0"))
        )

        # Use the Select class to interact with the dropdown
        select = Select(dropdown_element)
        select.select_by_visible_text("Daily Prices")

        # Step 4: Add the date to the date field
        date_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Txt_FrmDate"))
        )
        date_field.clear()
        date_field.send_keys(date_str)
        date_field.send_keys(Keys.RETURN)

        # Step 5: Wait for the result and get the HTML
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Get the page source (HTML)
        html_content = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the table in the HTML (assuming it's the first table)
        table = soup.find('table', {'id': 'gv0'})

        # If the table is found, read it into a pandas DataFrame
        if table:
            df = pd.read_html(str(table))[0]

            # Add the date column to the DataFrame
            df['Date'] = date_str

            # Filter the data for the commodities of interest
            df_filtered = df[['States/UTs', 'Date'] + commodities_of_interest]

            # Filter for a specific location of interest
            location_of_interest = 'Maharashtra'
            df_filtered = df_filtered[df_filtered['States/UTs'] == location_of_interest].sort_values(by='Date', ascending=True)
            # Print the filtered DataFrame
            # print(df_filtered)
            file_path = r"C:\SIH\excel_maharastra.csv"
            file_exists = os.path.exists(file_path)

#           # Save the DataFrame to CSV (append mode)
            df_filtered.to_csv(file_path, mode='a', header=not file_exists, index=False)
        
finally:
    driver.quit()
