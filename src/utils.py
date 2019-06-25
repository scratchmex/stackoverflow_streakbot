import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from time import sleep

def IFTTnotify(event_name, key, vals):
    """
        Send a notification to your phone via IFTT by the applet https://ifttt.com/recipes/442155-simple-rest-based-phone-notification
        See https://github.com/hossman/ifttt-trigger for more info about this applet
        This function tries every second until the response is ok
        ++ This function logs with logging.getLogger(__name__) ++

        event_name: the event name to trigger
        key: the key of the Webhook service in IFTTT (https://ifttt.com/maker_webhooks)
        vals: a list of up to 3 string vals, [value1, value2, value3]
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'vals[{vals}]')
    vals={f'value{i+1}':v for i,v in enumerate(vals[:3]) if isinstance(v, str)}
    url=f'https://maker.ifttt.com/trigger/{event_name}/with/key/{key}'

    while True:#this needs to work
        try:
            r=requests.post(url, json=vals)

            if r.ok:
                logger.info(f'Notification sent[{event_name}, {vals}]')
                logger.debug(f'Response[{r.text}]')
                return r.text
                
            logger.warning(f'Notification couldnt be sent[{event_name}, {vals}]. Status code {r.status_code}. Sleeping 1 sec')
            sleep(1)

        except Exception as e:
            logger.error('Notification couldnt be sent some exception occurred. Sleeping 5 secs')
            logger.exception(e)
            sleep(5)
        

def requests_retry_session(retries=3,
                           backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    """
        Returns a session prepared with a retry object 
        This implementation was obtained in https://www.peterbe.com/plog/best-practice-with-retries-with-requests
        ++ This function logs with logging.getLogger(__name__) ++
    """
    # logger = logging.getLogger(__name__)

    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session