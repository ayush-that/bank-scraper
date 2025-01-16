import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BANKS_FILE = 'banks.txt'
OUTPUT_DIR = 'bank_reports'
YEARS = ['2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']

def read_banks(file_path): ## read the bank names from the file
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def download_pdf(url, file_path): ## download the pdf from the url and save it to the file path
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    try: # download the pdf
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200: # if the response is successful
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f'Downloaded {file_path}')
        else:
            print(f'Failed to download PDF from {url}: Status code {response.status_code}')
    except Exception as e:
        print(f'Error downloading PDF from {url}: {e}') # if there is an error

def main(): # main function
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR) # create the output directory if it doesn't exist

    banks = read_banks(BANKS_FILE)

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Avoid detection
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service('chromedriver.exe')  # initialize the webdriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for bank in banks: # process each bank and year
        bank_dir = os.path.join(OUTPUT_DIR, bank)
        if not os.path.exists(bank_dir):
            os.makedirs(bank_dir)
        for year in YEARS:
            file_name = f'{bank}_{year}.pdf'
            file_path = os.path.join(bank_dir, file_name)

            if os.path.exists(file_path): # skip if the file already exists
                print(f'{file_name} already exists. Skipping...')
                continue

            query = f'{bank} "annual report" {year} filetype:pdf' # construct the search query
            search_url = f'https://www.google.com/search?q={query}'

            driver.get(search_url)
            print(f'Searching for {bank} {year}...')

            try:
                WebDriverWait(driver, 10).until( # wait for the pdf link to appear
                    EC.presence_of_element_located((By.XPATH, '//a[contains(@href, ".pdf")]'))
                )
                pdf_link = driver.find_element(By.XPATH, '//a[contains(@href, ".pdf")]') # find the pdf link
                pdf_url = pdf_link.get_attribute('href') # get the pdf url

                print(f'Found PDF for {bank} {year} at {pdf_url}')
                download_pdf(pdf_url, file_path)
            except TimeoutException: # if no results are found
                print(f'No results found for {bank} {year}')
            except NoSuchElementException: # if no pdf link is found
                print(f'No PDF link found for {bank} {year}')
            except Exception as e:
                print(f'Error searching for {bank} {year}: {e}')

    driver.quit()
    print('Scraping completed.')

if __name__ == '__main__':
    main()