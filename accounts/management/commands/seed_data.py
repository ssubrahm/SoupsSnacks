from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seed command framework ready'))
        self.stdout.write('TODO: Implement seeding logic in future steps')
