from imap_tools import MailBox, AND
from datetime import datetime, timedelta

from dotenv import dotenv_values

config = dotenv_values('.env')
EMAIL_SEARCH_CUTOFF = {'days': 10}

with MailBox('imap.gmail.com').login(config['EMAIL_ACCOUNT'], config['EMAIL_PASSWORD']) as mailbox:
    since_datetime = datetime.today() - timedelta(**EMAIL_SEARCH_CUTOFF)
    for msg in mailbox.fetch(AND(from_=config['EMAIL_SERVICE_FROM'], date_gte=since_datetime.date())):
        print(msg)