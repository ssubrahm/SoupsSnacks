from django.core.management.base import BaseCommand
from customers.models import Customer


class Command(BaseCommand):
    help = 'Create sample customers for testing'

    def handle(self, *args, **options):
        sample_customers = [
            {
                'name': 'Priya Sharma',
                'mobile': '+919876543210',
                'email': 'priya.sharma@example.com',
                'apartment_name': 'Prestige Shantiniketan',
                'block': 'Tower A',
                'address': 'Flat 301, Prestige Shantiniketan, Whitefield, Bangalore 560066',
                'notes': 'Regular customer, prefers cream of mushroom soup',
                'is_active': True
            },
            {
                'name': 'Rajesh Kumar',
                'mobile': '+919876543211',
                'email': 'rajesh.kumar@example.com',
                'apartment_name': 'Prestige Shantiniketan',
                'block': 'Tower B',
                'address': 'Flat 502, Prestige Shantiniketan, Whitefield, Bangalore 560066',
                'notes': 'Loves bajji and bonda. Orders for office parties',
                'is_active': True
            },
            {
                'name': 'Lakshmi Venkatesh',
                'mobile': '+919876543212',
                'email': 'lakshmi.v@example.com',
                'apartment_name': 'Brigade Gateway',
                'block': 'Orchid',
                'address': 'Flat 1201, Brigade Gateway, Rajajinagar, Bangalore 560010',
                'notes': 'Weekly orders for pongal and upma',
                'is_active': True
            },
            {
                'name': 'Arjun Reddy',
                'mobile': '+919876543213',
                'email': 'arjun.reddy@example.com',
                'apartment_name': 'Brigade Gateway',
                'block': 'Lily',
                'address': 'Flat 804, Brigade Gateway, Rajajinagar, Bangalore 560010',
                'notes': 'Prefers dal and roti combo',
                'is_active': True
            },
            {
                'name': 'Meera Iyer',
                'mobile': '+919876543214',
                'email': None,
                'apartment_name': 'Sobha City',
                'block': 'Phase 1',
                'address': 'Flat 205, Sobha City, Thanisandra, Bangalore 560077',
                'notes': 'Orders vegetable clear soup regularly',
                'is_active': True
            },
            {
                'name': 'Suresh Patel',
                'mobile': '+919876543215',
                'email': 'suresh.patel@example.com',
                'apartment_name': 'Sobha City',
                'block': 'Phase 2',
                'address': 'Flat 1102, Sobha City, Thanisandra, Bangalore 560077',
                'notes': 'Bulk orders for family functions',
                'is_active': True
            },
            {
                'name': 'Divya Nair',
                'mobile': '+919876543216',
                'email': 'divya.nair@example.com',
                'apartment_name': 'Salarpuria Sattva',
                'block': 'Magnificia',
                'address': 'Flat 703, Salarpuria Sattva, Sarjapur Road, Bangalore 560035',
                'notes': 'Loves avalekki breakfast',
                'is_active': True
            },
            {
                'name': 'Vikram Singh',
                'mobile': '+919876543217',
                'email': None,
                'apartment_name': 'Prestige Shantiniketan',
                'block': 'Tower C',
                'address': 'Flat 404, Prestige Shantiniketan, Whitefield, Bangalore 560066',
                'notes': 'Orders cream of broccoli soup weekly',
                'is_active': False
            },
            {
                'name': 'Ananya Krishnan',
                'mobile': '+919876543218',
                'email': 'ananya.k@example.com',
                'apartment_name': 'Brigade Gateway',
                'block': 'Orchid',
                'address': 'Flat 605, Brigade Gateway, Rajajinagar, Bangalore 560010',
                'notes': 'Corporate client - orders for team lunches',
                'is_active': True
            },
            {
                'name': 'Karthik Ramesh',
                'mobile': '+919876543219',
                'email': 'karthik.r@example.com',
                'apartment_name': 'Salarpuria Sattva',
                'block': 'Celesta',
                'address': 'Flat 901, Salarpuria Sattva, Sarjapur Road, Bangalore 560035',
                'notes': 'Enjoys zucchini soup and pakoras',
                'is_active': True
            },
        ]

        created_count = 0
        skipped_count = 0

        for customer_data in sample_customers:
            # Check if customer with this mobile already exists
            if not Customer.objects.filter(mobile=customer_data['mobile']).exists():
                Customer.objects.create(**customer_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {customer_data["name"]}'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'⊘ Skipped: {customer_data["name"]} (already exists)'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {created_count} customers'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'⊘ Skipped {skipped_count} existing customers'))
