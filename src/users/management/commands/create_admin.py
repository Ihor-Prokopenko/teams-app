from django.core.management import BaseCommand, CommandError
from django.db import OperationalError, connection
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except OperationalError as e:
            raise CommandError('No access to the database: ', str(e))

        admin_email = 'admin@example.com'

        existing_admin = User.objects.filter(email=admin_email).first()
        if existing_admin:
            return self.stderr.write(self.style.SUCCESS(f'User with email {admin_email} already exists.'))

        User.objects.create_superuser(email=admin_email, username=admin_email, password='admin')

        self.stderr.write(self.style.SUCCESS('Admin user created.'))
