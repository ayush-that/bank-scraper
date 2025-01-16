import os
import re
import time
import requests
from urllib.parse import urljoin

OUTPUT_DIR = 'kotak_bank_reports'
BASE_URL = 'https://www.kotak.com/content/dam/Kotak/investor-relation/Financial-Result/QuarterlyReport/'
YEARS = range(2011, 2026)
QUARTERS = ['q1', 'q2', 'q3', 'q4']
REPORT_TYPES = {
    'Press-Release': ['PressRelease'],
    'Investor-Presentation': ['Investor-Presentation']
}

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
            return True
        else:
            print(f'Failed to download PDF from {url}: Status code {response.status_code}')
            return False
    except Exception as e:
        print(f'Error downloading PDF from {url}: {e}')
        return False

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for year in YEARS:
        print(f'Processing FY-{year}...')

        year_dir = os.path.join(OUTPUT_DIR, f'FY-{year}')
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        for quarter in QUARTERS:
            print(f'  Processing {quarter}...')

            for report_type, url_paths in REPORT_TYPES.items():
                if report_type == 'Press-Release':
                    file_names = [
                        f'{quarter.upper()}FY{str(year)[-2:]}-Press-Release.pdf',
                        f'{quarter.upper()}FY{str(year)[-2:]}PressRelease.pdf'
                    ]
                elif report_type == 'Investor-Presentation':
                    file_names = [
                        f'{quarter.upper()}FY{str(year)[-2:]}_Investor_Presentation.pdf',
                        f'{quarter.upper()}FY{str(year)[-2:]}_Investor_presentation.pdf'
                    ]

                for file_name in file_names:
                    report_url = f'{BASE_URL}FY-{year}/{quarter}/{url_paths[0]}/'

                    full_url = urljoin(report_url, file_name)
                    file_path = os.path.join(year_dir, file_name)

                    print(f'    Trying URL: {full_url}')
                    if download_pdf(full_url, file_path):
                        break
                    else:
                        print(f'    URL not found: {full_url}')

        time.sleep(2)

    print('Scraping completed.')

if __name__ == '__main__':
    main()