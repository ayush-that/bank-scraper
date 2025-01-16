import os
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*#]', '_', filename)

def download_pdf(url, folder, filename):
    try:
        response = requests.get(url)
        os.makedirs(folder, exist_ok=True)
        sanitized_filename = sanitize_filename(filename)
        filepath = os.path.join(folder, sanitized_filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filepath}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

url = "https://www.hdfcbank.com/personal/resources/regulatory-disclosures"
driver.get(url)
time.sleep(5)
accordions = driver.find_elements(By.CLASS_NAME, "imp-product-notice-links")

for accordion in accordions:
    year = accordion.find_element(By.CLASS_NAME, "imp-label-heading").text.strip()
    print(f"Processing year: {year}")
    pdf_list = accordion.find_element(By.CLASS_NAME, "imp-product-view-list")
    pdf_links = pdf_list.find_elements(By.TAG_NAME, "a")

    for link in pdf_links:
        pdf_url = link.get_attribute("href")
        if pdf_url and pdf_url.endswith(".pdf"):
            pdf_name = pdf_url.split("/")[-1]
            download_pdf(pdf_url, year, pdf_name)

driver.quit()