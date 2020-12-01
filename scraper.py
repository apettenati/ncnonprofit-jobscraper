import requests
from bs4 import BeautifulSoup
import logging
import sys
import datetime
import csv

logging.basicConfig(level=logging.DEBUG)

def check_HTTP_status(request):
    if request.status_code == 200:
        return True
    else:
        print(f"Status code: {request.status_code}")
        return False

def create_request():
    url = 'https://www.ncnonprofits.org/nc-nonprofit-careers/search-posted-jobs'
    request = requests.get(url)
    return request

def get_jobs(request):
    # TODO: get links from hrefs
    soup = BeautifulSoup(request.content, 'lxml')
    table_dict = {
        'Job Title': 'views-field views-field-title',
        'Category': 'views-field-field-jp-category',
        'Organization Name': 'views-field views-field-field-jp-organization-name',
        'Updated Date': 'views-field views-field-changed',
        'County': 'views-field views-field-field-ypl-county'
    }
    table_lists = {}
    for key, value in table_dict.items():
        table_lists[key] = [x.text.strip() for x in soup.table.find_all(class_=value)][1:]

    jobs_list = []
    list_len = len(table_lists['Job Title'])
    for i in range(list_len):
        jobs_list.append([])
        for k, v in table_lists.items():
            jobs_list[i].append(v[i])
    return jobs_list

def get_new_jobs(jobs):
    # TODO: update to get timestamp upon run
    new_jobs = []
    last_run = datetime.datetime(2020, 11, 28)
    for job in jobs:
        strip_date = job[3].replace('.', '').replace(',', '')
        date = datetime.datetime.strptime(strip_date, '%b %d %Y')
        if date > last_run:
            new_jobs.append(job)
    return new_jobs

def main():
    request = create_request()
    if check_HTTP_status(request):
        jobs = get_jobs(request)
        for job in jobs:
            print(job)
        print()
        new_jobs = get_new_jobs(jobs)
        for job in new_jobs:
            print(job)

if __name__ == "__main__":
    main()
