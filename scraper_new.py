import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

OUTPUT_DIR = 'bank_reports'
YEAR = '2023-24'
BANK_WEBSITES = {
    'Axis Bank Ltd.': ['axisbank.com'],
    'HDFC Bank Ltd': ['hdfcbank.com'],
    'ICICI Bank Ltd.': ['icicibank.com', 'icicilombard.com'],
    'State Bank of India': ['sbi.co.in'],
    'Kotak Mahindra Bank Ltd': ['kotak.com']
}

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

# Main function
def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Avoid detection
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Initialize the WebDriver
    service = Service('chromedriver.exe')  # Path to chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Process each bank
    for bank, domains in BANK_WEBSITES.items():
        bank_dir = os.path.join(OUTPUT_DIR, bank)
        if not os.path.exists(bank_dir):
            os.makedirs(bank_dir)

        # Define the queries (excluding Quarterly Report)
        queries = [
            ('Annual Report', f'{bank} ("annual report" OR "annual financial statement") {YEAR} filetype:pdf'),
            ('Balance Sheet', f'{bank} ("balance sheet" OR "statement of financial position") {YEAR} filetype:pdf'),
            ('Income Statement', f'{bank} ("income statement" OR "profit and loss statement" OR "statement of comprehensive income") {YEAR} filetype:pdf'),
            ('Cash Flow Statement', f'{bank} ("cash flow statement" OR "statement of cash flows") {YEAR} filetype:pdf'),
            ('Statement of Changes in Equity', f'{bank} ("statement of changes in equity" OR "statement of stockholders\' equity") {YEAR} filetype:pdf'),
            ('Basel III Disclosures', f'{bank} ("Basel III disclosures" OR "Basel III report" OR "capital adequacy report") {YEAR} filetype:pdf'),
            ('Pillar 3 Disclosures', f'{bank} ("Pillar 3 disclosures" OR "Pillar III report" OR "risk disclosure report") {YEAR} filetype:pdf'),
            ('Risk Management Report', f'{bank} ("risk management report" OR "risk assessment report") {YEAR} filetype:pdf'),
            ('Investor Presentation', f'{bank} ("investor presentation" OR "earnings presentation" OR "financial presentation") {YEAR} filetype:pdf'),
            ('Shareholding Pattern', f'{bank} ("shareholding pattern" OR "ownership structure") {YEAR} filetype:pdf'),
            ('Corporate Governance Report', f'{bank} ("corporate governance report" OR "governance statement") {YEAR} filetype:pdf'),
            ('Sustainability Report', f'{bank} ("sustainability report" OR "ESG report" OR "environmental social governance report") {YEAR} filetype:pdf'),
            ('Management Discussion and Analysis', f'{bank} ("MD&A" OR "Management Discussion and Analysis" OR "management commentary") {YEAR} filetype:pdf'),
            ('Auditor\'s Report', f'{bank} ("auditor\'s report" OR "independent auditor\'s report" OR "statutory auditor\'s report") {YEAR} filetype:pdf')
        ]

        # Process each query
        for doc_type, query in queries:
            doc_dir = os.path.join(bank_dir, doc_type)
            if not os.path.exists(doc_dir):
                os.makedirs(doc_dir)

            file_name = f'{bank}_{doc_type.replace(" ", "_")}_{YEAR}.pdf'
            file_path = os.path.join(doc_dir, file_name)

            # Skip if the file already exists
            if os.path.exists(file_path):
                print(f'{file_name} already exists. Skipping...')
                continue

            # Try each domain for the bank
            success = False
            for domain in domains:
                site_query = f'{query} site:{domain}'
                success = search_and_download(driver, site_query, file_path)
                if success:
                    break  # Stop if the PDF is found

            if not success:
                print(f'No results found for {bank} {YEAR} {doc_type} on any domain.')

            # Add a small delay between requests to avoid being blocked
            time.sleep(5)

    # Close the WebDriver
    driver.quit()
    print('Scraping completed.')

if __name__ == '__main__':
    main()