from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import os
import time
import pandas as pd
from datetime import datetime, timedelta

# Setup the WebDriver
driver = webdriver.Chrome()

# Today's date
today = datetime(2023, 3, 6)

# Create directory to save the files if not exists
output_dir = 'Wholesale_Reports2'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to save the page source as an HTML file
def save_html_report(report_name, date_str, html_content):
    date_str_safe = date_str.replace("/", "-")  # Make date file-system friendly
    filename = f"{output_dir}/{report_name}_{date_str_safe}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"Saved {report_name} report for {date_str} as {filename}")

try:
    # Loop over the last 3 years (or adjust the range as necessary)
    for i in range(3 * 365):
        date = today - timedelta(days=i)
        date_str = date.strftime("%d/%m/%Y")  # Format the date as needed for the input field
        
        # Step 1: Open the website
        driver.get('https://fcainfoweb.nic.in/reports/report_menu_web.aspx')
        
        # Step 2: Select the "Price report" radio button using JavaScript Executor
        price_report_radio = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Rbl_Rpt_type_0"))
        )
        driver.execute_script("arguments[0].click();", price_report_radio)  # Force click using JS
        
        # Step 3: Select "Wholesale" from the report type dropdown
        report_type_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Ddl_Rpt_type"))
        )
        select_report_type = Select(report_type_dropdown)
        select_report_type.select_by_visible_text("Wholesale")
        
        # Step 4: Select the "Price Report" option from the second dropdown
        report_option_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Ddl_Rpt_Option0"))
        )
        select_report_option = Select(report_option_dropdown)
        
        # Select the first option: "Price Report"
        select_report_option.select_by_index(1)  # Index 1 assuming the first valid option is "Price Report"
        report_name = "Wholesale"  # Get the name of the selected option
        
        # Step 5: Add the date to the date field
        date_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_Txt_FrmDate"))
        )
        date_field.clear()
        date_field.send_keys(date_str)
        date_field.send_keys(Keys.RETURN)
        
        # # Step 6: Click the "Get Data" button to retrieve the report
        # get_data_button = WebDriverWait(driver, 20).until(
        #     EC.element_to_be_clickable((By.ID, "ctl00_MainContent_btn_getdata1"))
        # )
        # get_data_button.click()

        # Step 7: Wait for the table to load and get the HTML
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        html_content = driver.page_source
        
        # Step 8: Save the HTML content for this report and date
        save_html_report(report_name, date_str, html_content)

        # Wait before processing the next date
        time.sleep(3)

        # Break after completing 3 years of scraping (adjust as necessary)
        if date < today - timedelta(days=3*365):
            break

finally:
    driver.quit()
