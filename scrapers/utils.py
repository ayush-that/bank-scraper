import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Download PDF from a URL
def download_pdf(url, file_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f'Downloaded {file_path}')
        else:
            print(f'Failed to download PDF from {url}: Status code {response.status_code}')
    except Exception as e:
        print(f'Error downloading PDF from {url}: {e}')

# Perform Google search and download PDF
def search_and_download(driver, query, file_path):
    search_url = f'https://www.google.com/search?q={query}'
    driver.get(search_url)
    print(f'Searching for {query}...')

    try:
        # Wait for the first PDF link to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href, ".pdf")]'))
        )
        # Find the first PDF link
        pdf_link = driver.find_element(By.XPATH, '//a[contains(@href, ".pdf")]')
        pdf_url = pdf_link.get_attribute('href')

        # Download the PDF
        print(f'Found PDF at {pdf_url}')
        download_pdf(pdf_url, file_path)
        return True  # Success
    except TimeoutException:
        print(f'No results found for {query}')
    except NoSuchElementException:
        print(f'No PDF link found for {query}')
    except Exception as e:
        print(f'Error searching for {query}: {e}')
    return False  # Failure