from .utils import search_and_download

def scrape_axis_bank(driver, output_dir, year):
    bank = 'Axis Bank Ltd.'
    domains = ['axisbank.com']
    queries = [
        ('Annual Report', f'{bank} ("annual report" OR "annual financial statement") {year} filetype:pdf'),
        ('Balance Sheet', f'{bank} ("balance sheet" OR "statement of financial position") {year} filetype:pdf'),
        # Add other queries here
    ]

    for doc_type, query in queries:
        doc_dir = os.path.join(output_dir, bank, doc_type)
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)

        file_name = f'{bank}_{doc_type.replace(" ", "_")}_{year}.pdf'
        file_path = os.path.join(doc_dir, file_name)

        if os.path.exists(file_path):
            print(f'{file_name} already exists. Skipping...')
            continue

        success = False
        for domain in domains:
            site_query = f'{query} site:{domain}'
            success = search_and_download(driver, site_query, file_path)
            if success:
                break

        if not success:
            print(f'No results found for {bank} {year} {doc_type} on any domain.')