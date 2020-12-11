#! python

import datetime
import logging
import requests
import argparse
import os
from bs4 import BeautifulSoup
from rich import print
from telegram import read_config, get_API_key, get_bot_chat_id, send_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

def check_HTTP_status(request):
    """
    Checks HTTP status from provided get request url

    Parameters:
    request (request object): get request with provided url

    Returns:
        boolean with True if returned status code is 200, else false
    """
    if request.status_code == 200:
        return True
    else:
        print(f"Status code: {request.status_code}")
        return False

def create_request():
    """
    Creates get request from given url

    Returns:
    request (request object): request object with get request from provided url
    """
    url = 'https://www.ncnonprofits.org/nc-nonprofit-careers/search-posted-jobs'
    request = requests.get(url)
    return request

def get_jobs(request):
    """
    Retrieves all jobs from given url

    Parameter:
    request (requests object): get request with previously provided url

    Returns:
    jobs_list (list): list containing a list for each job with attributes:
        Job Title, Category, Organization Name, Updated Date, and County
    """
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

    links = [f"https://www.ncnonprofits.org{i['href']}" for i in soup.table.find_all('a', property='')]
    table_lists['Links'] = links

    jobs_list = []
    list_len = len(table_lists['Job Title'])
    for i in range(list_len):
        jobs_list.append([])
        for job in table_lists.values():
            jobs_list[i].append(job[i])
    return jobs_list

def get_last_run_timestamp():
    """
    Reads 'run_timestamp.txt' file to retrieve datetime object

    Returns:
    timestamp (datetime object): datetime indicating last time program was executed
    """
    with open('run_timestamp.txt') as file:
        date = file.read()
        timestamp = datetime.datetime.strptime(date, '%d-%b-%y')
        return timestamp

def set_last_run_timestamp(timestamp=None):
    """
    Creates datetime object showing last application run time
    Writes timestamp to file

    Parameters:
    timestamp (datetime object): datetime which defaults to now
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()
    with open('run_timestamp.txt', 'w') as file:
        timestamp = timestamp
        file.write(str(datetime.datetime.strftime(timestamp, '%d-%b-%y')))

def get_new_jobs(jobs, last_run):
    """
    Based on existing jobs list, filters to only return jobs posted after last run time

    Parameters:
    jobs (list): contains all job data from site
    last_run (datetime object): datetime indicating filter to be applied to jobs

    Returns:
    new_jobs (list): returns jobs filtered to remove items with dates prior to latest timestamp
    """
    new_jobs = []
    for job in jobs:
        date = datetime.datetime.strptime(job[3], '%b. %d, %Y')
        if date > last_run:
            new_jobs.append(job)
    return new_jobs

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file-name", help="provide a config.yaml file containing", type=str)
    return parser.parse_args()

def main():
    config_file = parser().file_name
    config = read_config(config_file)
    # config = read_config(os.getcwd() + '\\config.yaml')
    bot_api_key = get_API_key(config)
    bot_chat_id = get_bot_chat_id(config)
    logger.debug(bot_chat_id)
    request = create_request()
    if check_HTTP_status(request):
        jobs = get_jobs(request)
        last_run = get_last_run_timestamp()
        new_jobs = get_new_jobs(jobs, last_run)
        if new_jobs:
            send_message(new_jobs, bot_api_key, bot_chat_id)
            # for job in new_jobs:
            #     print(job)
        else:
            print('No new jobs!')
            send_message(new_jobs, bot_api_key, bot_chat_id)
        set_last_run_timestamp()
        logger.info(f'Successfully ran at {get_last_run_timestamp()}')

if __name__ == "__main__":
    # set_last_run_timestamp(datetime.date(2020, 12, 3))
    main()
