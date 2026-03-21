from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for each role'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_user(
                username='admin',
                email='admin@soupssnacks.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (admin/admin123)'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create operator user
        if not User.objects.filter(username='operator').exists():
            User.objects.create_user(
                username='operator',
                email='operator@soupssnacks.com',
                password='operator123',
                first_name='Operator',
                last_name='User',
                role='operator'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created operator user (operator/operator123)'))
        else:
            self.stdout.write(self.style.WARNING('Operator user already exists'))

        # Create cook user
        if not User.objects.filter(username='cook').exists():
            User.objects.create_user(
                username='cook',
                email='cook@soupssnacks.com',
                password='cook123',
                first_name='Cook',
                last_name='User',
                role='cook'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created cook user (cook/cook123)'))
        else:
            self.stdout.write(self.style.WARNING('Cook user already exists'))

        self.stdout.write(self.style.SUCCESS('\n✅ Test users ready!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Admin:    admin / admin123')
        self.stdout.write('  Operator: operator / operator123')
        self.stdout.write('  Cook:     cook / cook123')
