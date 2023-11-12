# NightSearch
## Introduction
This is a simple parsing application written in Python. 
Its main goal is to perform a Google search with a given keyword and then find 
a contact page (if it exists) of each found site and stores it into MongoDB database.

## Installation
Clone this repository, create virtual environment and run `pip install -r requirements.txt
` and `pip install -U "celery[redis]"`

## Project setup
Create an `.env` file:

```
CELERY_BROKER_URL=redis_url
CELERY_RESULT_BACKEND=redis_url
API_KEY=your_google_search_api_key
CX=your_google_cutom_search_engine_id
MONGO_URL=your_mongodb_url
```

## Running 
Run `celery -A tasks worker --loglevel=info -P eventlet` from the root folder to start Celery worker and 
`python -m api.api` to start the server

## Usage
Navigate to [localhost:8888](https://127.0.0.1:8888) and type in a search query.
You should get the list of all pages with their contact pages if those were found. 
On another tab you can see the whole search history.

## Workflow
When we input the search query, it gets sent to the `workflow_delegate.py`, which, as the name suggests,
delegates how the workflow will be executed. The workflow then looks like this:
1. As we can only search 10 pages at once with one query with Custom Google Search Engine,
we can use Celery to make multiple requests in parallel. This is the job of task `search_google`. All the instantiated 
tasks are run at once within a group.
2. When we get the search results, we scrape each site for contact page. This is again done in parallel, with each 
instance of task `find_contact_page` searching one site. If the contact page is found, it is stored to MongoDB, again
inside each task.
3. `find_contact_page` tasks run inside a chord. After all the tasks are completed, `find_contact_page_callback` is called,
that returns all the found contact pages, so they can be immediately displayed to the user.
