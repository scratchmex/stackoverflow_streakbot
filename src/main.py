import logging
import requests
import json

from stackoverflow_streakbot import StackoverflowStreakBot
from utils import IFTTnotify

if __name__ == "__main__":
    #set logging handler
    logging.basicConfig(filename='stackoverflow_streak.log',
                        level=logging.DEBUG,
                        format='%(asctime)s~%(levelname)s::%(module)s @ %(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    console = logging.StreamHandler()
    formatter=logging.Formatter('%(asctime)s~%(levelname)s::%(module)s @ %(funcName)s: %(message)s', '%Y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logger.addHandler(console) #add print to stdout

    with open('credentials.jsonl', 'r') as f:
        try:
            line=f.readline()
        except Exception as e:
            #log FATAL
            logger.critical('This is really bad, i could not open "credentials.jsonl"')
            logger.exception(e)
            exit('Could not load credentials!')
        creds=json.loads(line)
        logger.info('Credentials loaded :)')

    event_name='stackoverflow_login'

    bot=StackoverflowStreakBot(event_name, creds['apikey'])
    if bot.login(creds['user'], creds['password']):
        logger.info('Searching for the python tag')

        r=bot.s.get('https://stackoverflow.com/questions/tagged/python')
        # logger.debug(f'GetRequest(https://stackoverflow.com/questions/tagged/python) -> Response==[{r.text}]==')

        if r.ok:
            logger.info('Visited Python tag page :D')
            IFTTnotify(event_name, creds['apikey'], ('[StackOBot]', 'Python tag visited'))
        else:
            logger.warning(f'Python tag page with status code {r.status_code}')
    else:
        exit('Couldnt login!')
