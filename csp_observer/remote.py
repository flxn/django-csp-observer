import json
import logging
import time
import urllib.parse
import urllib.request
from .models import Session
from . import settings as app_settings

def create_master_session(user_agent, anonymized_ip):
    remote_url = "{}/master/session".format(app_settings.REMOTE_CSP_OBSERVER_URL.rstrip('/'))
    raw_data = {
        'user_agent': user_agent,
        'anonymized_ip': anonymized_ip
    }
    data = urllib.parse.urlencode(raw_data)
    data = data.encode('ascii')
    req = urllib.request.Request(remote_url, data)
    with urllib.request.urlopen(req) as response:
        status = response.status
        res_data = response.read()
        print(status, res_data)
        