
#  Stackoverflow Streak Bot

A bot who daily login and visit a page on Stackoverflow to maintain a streak. This script
- sends a notification to your phone via IFTT by [this applet](https://ifttt.com/recipes/442155-simple-rest-based-phone-notification) if the login succeed, if you got a captcha or if the logging failed
- use the `logging` module and log to file `stackoverflow_streak.log`
- read the credentials of the file `credentials.jsonl` (*user, password, apikey*)

Requires Python 3.7
You can setup to run this daily via *crontab* by adding

    0 8 * * * cd /path/to/repo/src && python3 ./main.py >> ~/cron.log 2>&1
    
to your crontab file (`crontab -e`)
