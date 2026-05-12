import requests
from bs4 import BeautifulSoup
from rich import print
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib import request
from io import BytesIO
from PyPDF2 import PdfReader

def extract_details(paper, full=False):
    title = paper.find('p', {"class": "title"})
    authors = paper.find('p', {"class": "authors"})
    listtitle = paper.find('p', {"class": "list-title"})
    linkspan = listtitle.find('span')
    links = linkspan.find_all('a')
    abstract = paper.find('span', {"class": "abstract-full"}) if full else paper.find('span', {"class": "abstract-short"})
    return {
        "title": title.get_text().strip(),
        "authors": [a.get_text().strip() for a in authors.find_all('a')],
        "abstract": abstract.get_text().split("△ Less")[0].strip() if full else abstract.get_text().split("▽ More")[0].strip(),
        "link": links[0]['href']
        }

def search_query(query, full=False):
    session = requests.Session()
    
    url=f"https://www.arxiv.org/search/?query={query}&searchtype=all&source=header"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Arxiv results are given in li elements
    results = soup.find_all('li', {"class": "arxiv-result"})
    return [extract_details(result, full) for result in results]

def extract_paper(link):
    wfile = request.urlopen(link)
    bytes_stream = BytesIO(wfile.read())
    reader = PdfReader(bytes_stream)
    paperdata=""
    for page in reader.pages:
        paperdata+=page.extract_text()
    return paperdata