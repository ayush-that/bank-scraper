import os
import time
import requests
from bs4 import BeautifulSoup
import re
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin

OUTPUT_DIR = 'kotak_bank_reports'
BASE_URL = 'https://www.kotak.com/en/investor-relations/financial-results/regulatory-disclosure.html'
YEARS = range(2010, 2026)

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename

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

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    for year in YEARS:
        print(f'Processing FY-{year}...')
        year_dir = os.path.join(OUTPUT_DIR, f'FY-{year}')
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        year_url = f'{BASE_URL}#FY-{year}'

        response = session.get(year_url)
        if response.status_code != 200:
            print(f'Failed to fetch {year_url}. Status code: {response.status_code}')
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))
        for link in pdf_links:
            pdf_url = link['href']
            if '/content/dam/Kotak/investor-relation/Financial-Result/Regulatory-Disclosure/' in pdf_url:
                full_pdf_url = urljoin(BASE_URL, pdf_url)
                file_name = os.path.basename(pdf_url)
                file_name = sanitize_filename(file_name)
                file_path = os.path.join(year_dir, file_name)

                if os.path.exists(file_path):
                    print(f'{file_name} already exists. Skipping...')
                    continue

                print(f'Found PDF at {full_pdf_url}')
                download_pdf(full_pdf_url, file_path)

        time.sleep(2)

    print('Scraping completed.')

if __name__ == '__main__':
    main()