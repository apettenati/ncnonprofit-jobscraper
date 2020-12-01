#! python

import requests
from bs4 import BeautifulSoup
import logging
import datetime
import telepot
import yaml
import os
from rich import print

logging.basicConfig(level=logging.INFO, filename='log.txt')

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
        for k, v in table_lists.items():
            jobs_list[i].append(v[i])
    return jobs_list

def get_last_run_timestamp():
    with open('run_timestamp.txt') as file:
        date = file.read()
        timestamp = datetime.datetime.strptime(date, '%d-%b-%y %H:%M:%S')
        return timestamp

def set_last_run_timestamp(timestamp=datetime.datetime.now()):
    with open('run_timestamp.txt', 'w') as file:
        timestamp = timestamp
        file.write(str(datetime.datetime.strftime(timestamp, '%d-%b-%y %H:%M:%S')))

def get_new_jobs(jobs):
    new_jobs = []
    last_run = get_last_run_timestamp()
    for job in jobs:
        date = datetime.datetime.strptime(job[3], '%b. %d, %Y')
        if date > last_run:
            new_jobs.append(job)
    return new_jobs

def make_job_dict(job):
    job_dict = {
        'Job Title': job[0],
        'Category': job[1],
        'Organization Name': job[2],
        'Updated Date': job[3],
        'County': job[4],
        'Link': job[5]
    }
    return job_dict

def send_message(jobs, bot_api_key, bot_chat_id):
    bot = telepot.Bot(bot_api_key)
    if jobs:
        for job in jobs:
            job_dict = make_job_dict(job)
            job_string = 'New Job Alert! \n'
            for key, value in job_dict.items():
                job_string += f'{key}: {value}\n'
            bot.sendMessage(bot_chat_id, job_string, parse_mode='Markdown')
    else:
        bot.sendMessage(bot_chat_id, 'No new jobs!', parse_mode='Markdown')


def read_config(file_path):
    with open(file_path) as file:
        config = yaml.full_load(file)
        return config['configuration']

def main():
    config = read_config(os.getcwd() + '\\config.yaml')
    bot_api_key = config['telegram']['api_key']
    bot_chat_id = config['telegram']['chat_id']
    request = create_request()
    if check_HTTP_status(request):
        jobs = get_jobs(request)

        # for job in jobs:
        #     print(job)

        new_jobs = get_new_jobs(jobs)
        if new_jobs:
            send_message(new_jobs, bot_api_key, bot_chat_id)

            for job in new_jobs:
                print(job)
        else:
            print('No new jobs!')
            send_message(new_jobs, bot_api_key, bot_chat_id)
        set_last_run_timestamp()
        logging.info(f'Successfully ran at {get_last_run_timestamp()}')

if __name__ == "__main__":
    main()
