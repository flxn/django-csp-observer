import urllib.request
import json
import time
from . import settings as app_settings
from .models import GlobalCspRule, StoredConfig

def retrieve_rule_data():
    data = []
    with urllib.request.urlopen(app_settings.RULE_UPDATE_FILE) as f:
        raw = f.read().decode('utf-8')
        data = json.loads(raw)
    return data

def update_rules(force=False):
    if not force:
        min_update_delay = 60 * 60 * 12
        try:
            last_update = StoredConfig.objects.get(key=StoredConfig.LAST_RULE_UPDATE)
        except Exception:
            last_update = None

        time_since_update = time.time() - float(last_update.value if last_update else 0)
        if time_since_update < min_update_delay:
            raise Exception('Already updated withing last {} hours'.format(min_update_delay / 60 / 60))

    rules = retrieve_rule_data()

    # perform a little sanity check
    current_global_rule_count = GlobalCspRule.objects.all().count()
    allowed_difference = 0.5
    if len(rules) < current_global_rule_count * allowed_difference:
        # check failed
        # TODO: proper custom error handling
        raise Exception('Sanity Check Failed. Too few global rules.')

    # delete all stored rules
    GlobalCspRule.objects.all().delete()

    rule_directive_counter = 0
    for rule in rules:
        for directive in rule['directives']:
            db_rule = GlobalCspRule(
                global_id=rule['id'],
                title=rule['title'],
                description=rule['description'],
                cause=rule['cause'],
                blocked_url=directive['url'],
                effective_directive=directive['directive'] if directive['directive'] != '' else None
            )
            db_rule.save()
            rule_directive_counter += 1
    
    setting, created = StoredConfig.objects.get_or_create(key=StoredConfig.LAST_RULE_UPDATE)
    setting.value = str(time.time())
    setting.save()

    return (current_global_rule_count, len(rules), rule_directive_counter)