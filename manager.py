import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from scrapers.axis_bank import scrape_axis_bank
from scrapers.hdfc_bank import scrape_hdfc_bank
from scrapers.icici_bank import scrape_icici_bank
from scrapers.sbi import scrape_sbi
from scrapers.kotak_bank import scrape_kotak_bank

# Constants
OUTPUT_DIR = 'bank_reports'
YEAR = '2023-24'

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the WebDriver
service = Service('chromedriver.exe')  # Path to chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Run all scrapers
scrape_axis_bank(driver, OUTPUT_DIR, YEAR)
scrape_hdfc_bank(driver, OUTPUT_DIR, YEAR)
scrape_icici_bank(driver, OUTPUT_DIR, YEAR)
scrape_sbi(driver, OUTPUT_DIR, YEAR)
scrape_kotak_bank(driver, OUTPUT_DIR, YEAR)

# Close the WebDriver
driver.quit()
print('Scraping completed.')