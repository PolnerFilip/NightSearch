from urllib.parse import urljoin, urlparse, urlsplit

import pymongo
from bs4 import BeautifulSoup
from decouple import config
from pymongo import MongoClient


def find_contact_page_url(base_url: str, html: str) -> str | None:
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and 'contact' in href:
            return resolve_contact_page_url(base_url, href)
    return None


def resolve_contact_page_url(base_url: str, contact_url: str) -> str:
    # returns contact_url immediately if it is an absolute url
    if bool(urlparse(contact_url).netloc):
        return contact_url

    split_base = urlsplit(base_url)
    base = f'{split_base.scheme}://{split_base.netloc}'
    path_to_contact = urlsplit(contact_url).path
    resolved_url = urljoin(base, path_to_contact)
    return resolved_url


def insert_to_mongodb(page_name: str, page_url: str, contact_page_url: str, keyword: str) -> any:
    try:
        with MongoClient(config('MONGO_URL')) as connection:
            collection = connection['contactsdb']['contacts']
            document = collection.insert_one({
                'pageName': page_name,
                'pageURL': page_url,
                'contactPageURL': contact_page_url,
                'searchQuery': keyword
            })
            return document.inserted_id
    except pymongo.errors.PyMongoError as e:
        raise e



