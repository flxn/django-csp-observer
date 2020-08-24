import urllib.request
import json
import time
from . import settings as app_settings
from .models import CspRule

def retrieve_rule_data():
    """Returns the data of the global rule.json from the global data repository."""
    data = []
    with urllib.request.urlopen(app_settings.RULE_UPDATE_FILE) as f:
        raw = f.read().decode('utf-8')
        data = json.loads(raw)
    return data

def update_rules(force=False):
    """Updates the local rule database from the global data repository.

    The data is only requested if a minimum time period since the last update has passed.
    Can be forced by calling with force=True.
    """
    last_update = app_settings.get_stored(app_settings.KEY_LAST_RULE_UPDATE, default=None)
    last_update = float(last_update if last_update else 0)

    if not force:
        time_since_update = time.time() - last_update
        if time_since_update < app_settings.RULE_UPDATE_INTERVAL:
            raise Exception('Already updated within last {} hours'.format(app_settings.RULE_UPDATE_INTERVAL / 60 / 60))

    rule_database = retrieve_rule_data()
    if rule_database['last_updated'] < last_update:
        raise Exception('Local database already on latest version')
    
    # perform a little sanity check
    current_global_rule_count = CspRule.objects.get_global().count()
    allowed_difference = 0.5
    if len(rule_database['rules']) < current_global_rule_count * allowed_difference:
        # check failed
        # TODO: proper custom error handling
        raise Exception('Sanity Check Failed. Too few global rules.')

    # delete all stored rules
    CspRule.objects.get_global().delete()

    # insert the new rules into the local database
    rule_directive_counter = 0
    for rule in rule_database['rules']:
        for directive in rule['directives']:
            db_rule = CspRule(
                global_id=rule['id'],
                title=rule['title'],
                short_description=rule['short_description'],
                long_description=rule['long_description'],
                cause=rule['cause'],
                blocked_url=directive['url'],
                effective_directive=directive['directive'] if directive['directive'] != '' else None
            )
            db_rule.save()
            rule_directive_counter += 1
    
    app_settings.put_stored(app_settings.KEY_LAST_RULE_UPDATE, time.time())

    return (current_global_rule_count, len(rule_database['rules']), rule_directive_counter)