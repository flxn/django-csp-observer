
import urllib.parse
import urllib.request
import json
from . import settings as app_settings
from uuid import UUID

class UUIDEncoder(json.JSONEncoder):
    """https://stackoverflow.com/a/48159596"""
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

async def create_master_session(request, session_id):
    """Creates a remote session on the master collector instance and returns status."""
    # TODO: is there a better way for programmatic path reversing on a remote host?
    remote_url = "{}/master/session/{}".format(app_settings.REMOTE_CSP_OBSERVER_URL.rstrip('/'), session_id)
    raw_data = {
        'secret': app_settings.REMOTE_SECRET,
        'user_agent': request.META["HTTP_USER_AGENT"],
        'anonymized_ip': '123'#self.anonymize_ip(request.META["REMOTE_ADDR"])
    }
    data = urllib.parse.urlencode(raw_data)
    data = data.encode('ascii')
    req = urllib.request.Request(remote_url, data)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            res_data = response.read()
            print(status, res_data)
    except urllib.request.URLError as e:
        print(e)

def share_session_data(session_id, data):
    """Transmits the shared session data to the voluntary reporting endpoint."""
    data = json.dumps(data, cls=UUIDEncoder).encode('ascii')
    req = urllib.request.Request(app_settings.VOLUNTARY_DATA_SHARING_URL, data)
    with urllib.request.urlopen(req) as response:
        status = response.status
        res_data = response.read()
        return (status, res_data)

