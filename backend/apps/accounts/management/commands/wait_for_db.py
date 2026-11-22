import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Waits for PostgreSQL database to be available before proceeding'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database connection...')
        db_conn = None
        attempts = 0
        max_attempts = 30
        while not db_conn and attempts < max_attempts:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('Database is ready and accepting connections!'))
                return
            except OperationalError:
                attempts += 1
                self.stdout.write(f'Database unavailable, waiting 1 second... (attempt {attempts}/{max_attempts})')
                time.sleep(1)

        self.stdout.write(self.style.ERROR('Could not connect to database after multiple attempts.'))
        raise OperationalError("Database connection failed.")
