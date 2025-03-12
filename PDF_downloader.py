from requests_html import HTMLSession
import os
import time
import logging
from tqdm import tqdm
from requests.exceptions import ConnectionError, Timeout

# Initialize session
session = HTMLSession()

# Headers to mimic a browser
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
    'connection': 'keep-alive'
}

# Setup logging
logging.basicConfig(
    filename='Logfile.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

# Create a directory for PDFs if it doesn't exist
PDF_DIR = os.path.join(os.getcwd(), 'Downloaded_PDFs')
os.makedirs(PDF_DIR, exist_ok=True)


def fetch_pdf_links(url):
    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch {url} - Status Code: {response.status_code}")
            return []

        pdf_links = response.html.find('a[aria-label="Download PDF"]')
        if not pdf_links:
            logging.info(f"No PDFs found at {url}")
            return []

        pdf_urls = [url + link.attrs['href'] for link in pdf_links]
        return pdf_urls
    except (ConnectionError, Timeout) as e:
        logging.error(f"Connection error with {url}: {str(e)}")
        log_error_url(url)
        return []
    except Exception as e:
        logging.error(f"Unexpected error processing {url}: {str(e)}")
        return []


def download_pdf(pmc_pdf_url, pdf_path):
    try:
        pdf_response = session.get(pmc_pdf_url, stream=True, timeout=15)
        with open(pdf_path, 'wb') as pdf_file:
            for chunk in pdf_response.iter_content(chunk_size=1024):
                if chunk:
                    pdf_file.write(chunk)
        logging.info(f"Downloaded PDF: {pdf_path}")
    except Exception as e:
        logging.error(f"Error downloading PDF from {pmc_pdf_url} - {str(e)}")


def log_error_url(url):
    with open('Connection_Error_Urls.txt', 'a') as error_file:
        error_file.write(url + '\n')


# Read URLs from input file
input_file_path = 'inputfile.txt'

if not os.path.exists(input_file_path):
    logging.error("Input file 'inputfile.txt' not found. Exiting.")
    print("Error: 'inputfile.txt' not found!")
    exit()

with open(input_file_path, 'r') as input_file:
    pmcids = [pmcid.strip() for pmcid in input_file.readlines() if pmcid.strip()]

# Loop through URLs
for pmcid in tqdm(pmcids, desc="Processing URLs", unit="url"):
    url = 'https://pmc.ncbi.nlm.nih.gov/articles/'+pmcid+'/'
    pdf_urls = fetch_pdf_links(url)
    for pdf_url in pdf_urls:
        pmc_id = pmcid.strip()
        pdf_path = os.path.join(PDF_DIR, f"{pmc_id}.pdf")
        download_pdf(pdf_url, pdf_path)

    time.sleep(3)  # delay between requests

print('Download process complete!')
