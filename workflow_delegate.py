from celery import group, chord

from tasks import search_google, find_contact_page, find_contact_page_callback


def delegate_workflow(keyword: str) -> list[dict[str, str, str]]:
    # 1. perform Google search on multiple pages at once
    tasks = [search_google.s(keyword, (i - 1) * 10 + 1) for i in range(1, 4)]
    job = group(tasks)
    result = job.apply_async()
    try:
        results = result.get()
        results_flattened = [item for sublist in results for item in sublist]
        print(results_flattened)
    except Exception as e:
        print(e)
        raise e

    # TODO: remove
    # search_results = search_results_array

    # 2. perform contact page search and database storing for multiple pages at once
    tasks = [find_contact_page.s(item['link'], item['title'], keyword) for item in results_flattened]
    c = chord(tasks)(find_contact_page_callback.s())
    try:
        return c.get()
    except Exception as e:
        raise e
