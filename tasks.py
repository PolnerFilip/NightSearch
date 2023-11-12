import logging

import pymongo.errors
import requests
from celery import Celery
from celery.utils.log import get_task_logger


from search_results_test import search_results_array
from utils import insert_to_mongodb, find_contact_page_url
from decouple import config

BROKER_URL = config('CELERY_BROKER_URL')
BACKEND_URL = config('CELERY_RESULT_BACKEND')
API_KEY = config('API_KEY')
CX = config('CX')

app = Celery('nightwatch', broker=BROKER_URL, backend=BACKEND_URL)

logger = get_task_logger(__name__)

log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(filename='celery_log.txt', format=log_format)
file_handler = logging.FileHandler('celery_log.txt')
file_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(file_handler)


@app.task()
def search_google(keyword: str, start: int) -> [dict]:
    search_url = f'https://www.googleapis.com/customsearch/v1'
    params = {
        "q": keyword,
        "key": API_KEY,
        "cx": CX,
        "start": start
    }

    try:
        response = requests.get(search_url, params=params)
    except requests.exceptions.RequestException as e:
        logger.exception('Request exception has occured')
        raise e

    items = response.json()['items']
    results = [{'title': item['title'], 'link': item['link']} for item in items]
    return results


@app.task(
    autoretry_for=(requests.exceptions.Timeout,),
    retry_kwargs={'max_retries': 3, 'countdown': 5}
)
def find_contact_page(page_url: str, page_name: str, keyword: str) -> dict[str, str, str] | bool:
    try:
        res = requests.get(page_url, timeout=5)
    except requests.exceptions.Timeout as e:
        logger.exception('Timeout exception has occurred')
        raise e
    except requests.exceptions.RequestException as e:
        logger.exception('Request exception has occurred')
        raise e
    
    contact_page_url = find_contact_page_url(page_url, res.text)

    if contact_page_url is None:
        logger.info(f'Contact page for "{page_url}" not found')
        return False
    else:
        try:
            inserted_id = insert_to_mongodb(page_name, page_url, contact_page_url, keyword)
            logger.info(f'Inserted document {inserted_id} to database')
            return {
                'page_name': page_name,
                'page_url': page_url,
                'contact_page_url': contact_page_url
            }
        except pymongo.errors.PyMongoError as e:
            logger.exception('PyMongo error has occurred')
            raise e


@app.task()
def find_contact_page_callback(results) -> list[dict[str, str, str]]:
    total_pages = len(results)
    contact_pages_not_found_count = 0
    contact_pages_found = []
    for result in results:
        if not result:
            contact_pages_not_found_count += 1
        else:
            contact_pages_found.append(result)

    logger.info(
        f'''Searched {total_pages} pages. 
        Contact pages found on: {len(contact_pages_found)} sites.
        Contact pages not found on: {contact_pages_not_found_count} sites''')

    return contact_pages_found
