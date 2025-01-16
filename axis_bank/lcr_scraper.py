import requests
from bs4 import BeautifulSoup
import os
import re
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

url = "https://www.axisbank.com/shareholders-corner/regulatory-disclosure/liquidity-coverage-ratio-disclosure"

retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
)
    
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def sanitize_filename(filename):
    filename = re.sub(r"\?.*$", "", filename)
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    return filename

response = session.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', class_='share_link')
    base_url = "https://www.axisbank.com"
    save_directory = "axis_bank_lcr_disclosures"
    
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    for link in links:
        relative_url = link.get('href')
        
        if relative_url.startswith("/docs/default-source/regulatory-disclosure-section/liquidity-coverage-ratio-disclosure/"):
            full_url = base_url + relative_url
            
            file_name = os.path.basename(relative_url)
            file_name = sanitize_filename(file_name)
            file_path = os.path.join(save_directory, file_name)
            
            try:
                print(f"Downloading {full_url}...")
                file_response = session.get(full_url, headers=headers, timeout=10)
                
                if file_response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(file_response.content)
                    print(f"Saved to {file_path}")
                else:
                    print(f"Failed to download {full_url}. Status code: {file_response.status_code}")
            except Exception as e:
                print(f"Error downloading {full_url}: {e}")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")