from requests_html import HTMLSession
import os
import time
import logging
from requests.exceptions import ConnectionError, Timeout

# Initialize session
session = HTMLSession()

# Headers to mimic a browser
HEADERS = {
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

print('******************************')
print('STARTING TO DOWNLOAD PDF FILES...')

# Read URLs from input file
input_file_path = 'inputfile.txt'

if not os.path.exists(input_file_path):
    logging.error("Input file 'inputfile.txt' not found. Exiting.")
    print("Error: 'inputfile.txt' not found!")
    exit()

with open(input_file_path, 'r') as input_file:
    urls = [url.strip() for url in input_file.readlines() if url.strip()]

# Loop through URLs
for url in tqdm(urls, desc="Processing URLs", unit="url"):
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch {url} - Status Code: {response.status_code}")
            continue

        pdf_links = response.html.find('#main-content > aside > section:nth-child(1) > ul > li.pdf-link.other_item')

        if not pdf_links:
            logging.info(f"No PDFs found at {url}")
            continue

        for item in pdf_links:
            try:
                pmc_pdf_url = 'https://www.ncbi.nlm.nih.gov' + item.find('a', first=True).attrs['href']
                pmc_id = item.find('a', first=True).attrs['href'].split('/')[-3]
                
                pdf_response = session.get(pmc_pdf_url, stream=True, timeout=15)
                pdf_path = os.path.join(PDF_DIR, f"{pmc_id}.pdf")

                with open(pdf_path, 'wb') as pdf_file:
                    for chunk in pdf_response.iter_content(chunk_size=1024):
                        if chunk:
                            pdf_file.write(chunk)

                logging.info(f"Downloaded PDF: {pdf_path}")

            except Exception as e:
                logging.error(f"Error downloading PDF from {url} - {str(e)}")

        time.sleep(2)  # Respectful delay between requests

    except (ConnectionError, Timeout) as e:
        logging.error(f"Connection error with {url}: {str(e)}")
        with open('Connection_Error_Urls.txt', 'a') as error_file:
            error_file.write(url + '\n')

    except Exception as e:
        logging.error(f"Unexpected error processing {url}: {str(e)}")

print('Download process complete!')
