from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import time
import os
from bs4 import BeautifulSoup
import base64

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")

chrome_driver_path = "chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://sbi.co.in/web/corporate-governance/basel-iii-disclosures"

driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
reports = soup.find_all('div', class_='reportshide')
base_url = "https://sbi.co.in"
download_dir = "sbi_pdfs_year_wise"
os.makedirs(download_dir, exist_ok=True)

for report in reports:
    year = report.get('id')
    if year:
        year_dir = os.path.join(download_dir, year)
        os.makedirs(year_dir, exist_ok=True)

        pdf_links = report.find_all('a', href=True)
        for link in pdf_links:
            pdf_page_url = base_url + link['href']

            driver.get(pdf_page_url)
            time.sleep(5)

            embed_tag = driver.find_element(By.TAG_NAME, 'embed')
            pdf_url = embed_tag.get_attribute('original-url')

            if pdf_url:
                pdf_name = pdf_url.split('/')[-1].split('?')[0]
                pdf_path = os.path.join(year_dir, pdf_name)

                print(f"Downloading {pdf_name}...")
                response = requests.get(pdf_url)
                response.raise_for_status()

                with open(pdf_path, 'wb') as f:
                    f.write(response.content)

                print(f"Saved {pdf_name} to {pdf_path}")
            else:
                print(f"PDF URL not found for {pdf_page_url}")

driver.quit()

print("All PDFs downloaded and organized year-wise.")