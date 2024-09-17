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

# Setup the WebDriver
driver = webdriver.Chrome()

# Create an empty DataFrame to store the results
columns = ['Date', 'States/UTs', 'Rice', 'Wheat', 'Atta', 'Gram Dal', 'Tur/Arhar Dal', 'Urad Dal', 'Moong Dal', 
           'Masoor Dal', 'Sugar', 'Milk', 'Groundnut Oil', 'Mustard Oil', 'Vanaspati', 'Soya Oil', 'Sunflower Oil', 
           'Palm Oil', 'Gur', 'Tea', 'Salt', 'Potato', 'Onion', 'Tomato']
df = pd.DataFrame(columns=columns)

# File path for saving the data
csv_file_path = "daily_prices_data.csv"

# Check if the CSV file exists; if not, create it
if not os.path.exists(csv_file_path):
    df.to_csv(csv_file_path, index=False)
    print(f"Created new CSV file: {csv_file_path}")
else:
    # If the file exists, load it into the DataFrame
    df = pd.read_csv(csv_file_path)
    print(f"Loaded existing CSV file: {csv_file_path}")

# Today's date
today = datetime(2024, 2, 27)

# Function to parse the HTML and save data
def parse_html_and_save(html_content, date_str):
    # Replace slashes in the date string to make it file-system friendly
    date_str_safe = date_str.replace("/", "-")  # This changes '06/09/2024' to '06-09-2024'
    
    # Define the HTML file path
    html_file_path = f"daily_prices_{date_str_safe}.html"
    
    # Check if HTML file exists
    if not os.path.exists(html_file_path):
        # Save the HTML file with the date in the filename
        with open(html_file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
        print(f"Created new HTML file for {date_str}: {html_file_path}")
    else:
        print(f"HTML file for {date_str} already exists: {html_file_path}")
    
    # Parse the HTML to extract the data (assuming the first table is the relevant one)
    table_data = pd.read_html(html_content)[0]  # Assuming the table is the first one
    table_data.insert(0, 'Date', date_str)  # Add the date as the first column
    return table_data

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
        select.select_by_visible_text("Daily Prices")  # Choose the option by its visible text


        date_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Txt_FrmDate"))
        )

        # Step 4: Add the date to the date field
        date_field = driver.find_element(By.ID, "ctl00_MainContent_Txt_FrmDate")
        date_field.clear()
        date_field.send_keys(date_str)
        date_field.send_keys(Keys.RETURN)

        # Step 5: Wait for the result and get the HTML
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Get the page source (HTML)
        html_content = driver.page_source

        print(f"HTML presented for - {date_str}")

        # Step 6: Parse the HTML and save the data
        daily_data = parse_html_and_save(html_content, date_str)
        df = pd.concat([df, daily_data], ignore_index=True)

        # Step 7: Save the updated DataFrame to the CSV file
        df.to_csv(csv_file_path, index=False)
        print(f"Data has been saved to CSV successfully! {csv_file_path}")

        time.sleep(3)  # Wait for the page to reload

        # Break the loop after the range is finished
        if date < today - timedelta(days=3*365):
            break
        
finally:
    driver.quit()