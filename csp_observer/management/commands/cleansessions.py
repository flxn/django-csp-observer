from django.core.management.base import BaseCommand, CommandError
from csp_observer.models import Session
from csp_observer import settings as app_settings
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes old session data from the database'

    def add_arguments(self, parser):
        parser.add_argument('--days', nargs='?', default=app_settings.SESSION_KEEP_DAYS, type=int)

    def handle(self, *args, **options):
        last_relevant_date = timezone.now() - timedelta(days=options['days'])
        num_deleted, _ = Session.objects.filter(created_at__lt=last_relevant_date).delete()
        if num_deleted > 0:
            self.stdout.write(self.style.SUCCESS('Successfully deleted {} sessions'.format(num_deleted)))
        else:
            self.stdout.write(self.style.SUCCESS('Nothing to clean - no sessions older than {} days'.format(options['days'])))