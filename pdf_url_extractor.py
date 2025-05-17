import requests
from time import sleep
from tqdm import tqdm

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
    'connection': 'keep-alive'
}

#https://pmc.ncbi.nlm.nih.gov/articles/PMC3561829/pdf/JCI66882.pdf

urls_list = []
with open('inputfile.txt', 'r') as file:
    pmcids = file.readlines()

for pmcid in tqdm(pmcids):
    try:
        response = requests.get(f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid.strip()}/pdf/', headers=headers, timeout=10)
        pdf_urls = response.url
        urls_list.append(pdf_urls)
        sleep(2)  # Adding a short sleep to be polite to the server
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving DOI {pmcid.strip()}: {e}")
        urls_list.append(f"Error retrieving PMCID {pmcid.strip()}")

with open('pdf_url_list.csv', 'w') as file:
    file.write('PMCID,pdf_url\n')  # Adding column headers
    for pmcid, url in zip(pmcids, urls_list):
        file.write(f'{pmcid.strip()}, {url}\n')