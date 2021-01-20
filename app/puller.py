import os
from imap_tools import MailBox, AND
from datetime import datetime, timedelta
import re
import logging
from hashlib import sha256

logger = logging.getLogger(__name__)

from dotenv import dotenv_values
from redis import Redis

r = Redis(host='localhost', port=6379, db=0)

config = dotenv_values("{}/.env".format(os.path.dirname(os.path.realpath(__file__))))
EMAIL_SEARCH_CUTOFF = {'days': 10}


def email_to_userid(email):
    return email.split('@')[0].split('+')[1]


def get_track_id(user_id, track_code):
        track_code_hash = sha256(track_code.encode('utf-8')).hexdigest()
        return f"{user_id}:{track_code_hash}"


with MailBox('imap.gmail.com').login(config['EMAIL_ACCOUNT'], config['EMAIL_PASSWORD']) as mailbox:
    since_datetime = datetime.today() - timedelta(**EMAIL_SEARCH_CUTOFF)
    for msg in mailbox.fetch(AND(from_=config['EMAIL_SERVICE_FROM'], date_gte=since_datetime.date()), bulk=True):
        user_id = email_to_userid(msg.to_values[0]['email'])
        data = re.findall(r"""<(https://.+livetracking.+\?(.+)?)>""", msg.text, re.M, )
        if data:
            url, track_code = data[0][0], data[0][1]
            r.hset(get_track_id(user_id, track_code),
                    mapping={
                        'track_code': track_code,
                        'url': url,
                        'updated_at': datetime.now().timestamp(),
                    })
        else:
            logger.debug(f"No link detected. user_id: {user_id}, msg: `{msg.text}`")