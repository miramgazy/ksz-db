import os
from django.core.management.base import BaseCommand
from apps.accounts.models import User

class Command(BaseCommand):
    help = 'Creates default Superadmin user if not already present'

    def handle(self, *args, **options):
        # Remove accidental duplicate legacy admin if miramgazy exists
        if User.objects.filter(username='miramgazy', is_superuser=True).exists():
            User.objects.filter(username='admin').delete()

        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'miramgazy')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@ksz.kz')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'fodtin-fywmuR-qytga7')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'full_name': 'Главный Администратор',
                'role': User.Roles.SUPERADMIN,
                'registration_status': User.RegistrationStatus.ACTIVE,
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superadmin '{username}' created successfully! (password: {password})"))
        else:
            # Ensure proper roles
            updated = False
            if password and not user.check_password(password):
                user.set_password(password)
                updated = True
            if user.role != User.Roles.SUPERADMIN:
                user.role = User.Roles.SUPERADMIN
                updated = True
            if not user.is_active:
                user.is_active = True
                updated = True
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                updated = True
            if updated:
                user.save()
            self.stdout.write(self.style.NOTICE(f"Superadmin '{username}' already exists."))
