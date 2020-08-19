import time
from django.core.management.base import BaseCommand, CommandError
from csp_observer import settings as app_settings
from csp_observer.update import update_rules
from csp_observer.models import StoredConfig

class Command(BaseCommand):
    help = 'Updates global rules from central repository'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force', action='store_true', dest='force', default=False, help='Force update')

    def handle(self, *args, **options):
        force_update = options['force']

        try:
            count_pre, new_rules, count_post = update_rules(force=force_update)
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Successfully updated {} rules (entries: {} pre, {} post)'.format(new_rules, count_pre, count_post)))
