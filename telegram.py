import telepot
import yaml

def read_config(file_path):
    """
    Reads config file from specified location

    Parameters:
    file_path (str): YAML file formatted with necessary config data
        config contains dict with key 'telegram'
        telegram dict contains dict wtih keys 'api_key' and 'chat_id'
        values are all str

    Returns:
    config (dict): contains all configuration data from file
    """
    with open(file_path) as file:
        config = yaml.full_load(file)
        return config['configuration']

def get_API_key(config):
    return config['telegram']['api_key']

def get_bot_chat_id(config):
    return config['telegram']['chat_id']

def send_message(jobs, bot_api_key, bot_chat_id):
    """
    Sends messages via telegram bot with specified job data
    Converts job data to a str in a readable format for messaging
    One message sent for each job

    Parameters:
    jobs (list): contains list of all job data to be sent
    bot_api_key (str): api key for telegram bot to send message
    bot_chat_id (str): chat id for telegram bot to send message
    """
    bot = telepot.Bot(bot_api_key)
    if jobs:
        for job in jobs:
            # job_dict = make_job_dict(job)
            # job_string = '***New Job Alert***! \n'
            # for key, value in job_dict.items():
            #     job_string += f'{key}: {value}\n'
            job_string = make_job_message(job)
            bot.sendMessage(bot_chat_id, job_string, parse_mode='Markdown')
    else:
        bot.sendMessage(bot_chat_id, 'No new jobs!', parse_mode='Markdown')

def make_job_message(job):
    job = f"[{job[0]}]({job[5]})\n" \
          f"{job[3]}  {job[4]}\n\n" \
          f"***Category*** \n{job[1]}\n\n" \
          f"***Organization*** \n{job[2]}\n"
    return job