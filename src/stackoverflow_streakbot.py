import logging
import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from time import sleep
from base64 import b64encode

from utils import requests_retry_session, IFTTnotify

class StackoverflowStreakBot:
    def __init__(self, event_name, key, ua=None):
        self.ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0' if not ua else ua
        self.s=requests.Session()
        self.s.headers.update({'User-Agent':ua})
        self.event_name = event_name
        self.key = key
    
    def login(self, user, passwd, retries=15):
        """
            Tries to login to stackoverflow and returns the requests session
            ++ This function logs with logging.getLogger(__name__) ++

            user: email or user
            passwd: password
            retries: max number of tries to login
        """
        logger = logging.getLogger(__name__)
        logger.info(f'Trying to login with max of {retries} retries')
        
        url='https://stackoverflow.com/users/login?ssrc=head&returnurl=https://stackoverflow.com/'
        #host='stackoverflow.com'
        #referer='https://stackoverflow.com/'
        backoff_factor=3

        self.s=requests_retry_session(retries=retries, backoff_factor=backoff_factor, session=self.s)
    
        r=self.s.get(url)
        # logger.debug(f'GetRequest({url}) -> Response==[{r.text}]==')

        soup=BeautifulSoup(r.text, 'html.parser')
        form=soup.select('form[id="login-form"]')
        form=form[0] if len(form)>0 else None

        if form:
            actionurl=urljoin('https://stackoverflow.com', form.attrs['action'])
        else:
            actionurl=url
        
        hinputs=form.select('input[type="hidden"]') if form else []
        post_data={i.attrs['name']:i.attrs['value'] for i in hinputs 
                        if all( (i.attrs.get('name',False), i.attrs.get('value',False)) )}
        logger.debug(f'form[{form.attrs if form is not None else form}]; actionurl[{actionurl}]; post_data[{post_data}]')
        post_data.update({'email':user, 'password':passwd})

        self.s=requests_retry_session(retries=retries, backoff_factor=backoff_factor, session=self.s)
        while True:
            try:
                r=self.s.post(actionurl, data=post_data, allow_redirects=False)
                
                if r.is_redirect:
                    logger.debug(f'Got redirected to {r.headers["Location"]}')
                else:
                    logger.debug(f'No redirect. Headers[{r.headers["Location"]}]')

                if r.cookies.get('uauth', False):
                    #log ok
                    logger.info('Logged in successful. Notifying...')
                    logger.debug(f'Cookies[{r.cookies}]')
                    IFTTnotify(self.event_name, self.key, ('[StackOBot]', 'Login ok'))
                    return True
                elif r.url.startswith('https://stackoverflow.com/nocaptcha'):
                    logger.warning('Got a CAPTCHA. Trying in a minute. Notifying...')
                    IFTTnotify(self.event_name, self.key, ('[StackOBot]', 'Got captcha'))
                    sleep(60)
                    continue
                else:
                    logger.error(f'Get didnt get uauth cookie, instead [{r.cookies}]')
                    logger.debug(f'GetRequest({actionurl}) -> Response==[{b64encode(r.content)}]==')
                    raise RuntimeError

            except Exception as e:
                #log CRITICAL
                logger.critical('Couldnt login. Notifying...')
                IFTTnotify(self.event_name, self.key, ('[StackOBot]', 'Login FAILED'))
                logger.exception(e)
                return False