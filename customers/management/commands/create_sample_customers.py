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
                'address': '123 MG Road, Bangalore, Karnataka 560001',
                'notes': 'Regular customer, prefers cream of mushroom soup',
                'is_active': True
            },
            {
                'name': 'Rajesh Kumar',
                'mobile': '+919876543211',
                'email': 'rajesh.kumar@example.com',
                'address': '456 Brigade Road, Bangalore, Karnataka 560025',
                'notes': 'Loves bajji and bonda. Orders for office parties',
                'is_active': True
            },
            {
                'name': 'Lakshmi Venkatesh',
                'mobile': '+919876543212',
                'email': 'lakshmi.v@example.com',
                'address': '789 Jayanagar 4th Block, Bangalore, Karnataka 560011',
                'notes': 'Weekly orders for pongal and upma',
                'is_active': True
            },
            {
                'name': 'Arjun Reddy',
                'mobile': '+919876543213',
                'email': 'arjun.reddy@example.com',
                'address': '321 Koramangala, Bangalore, Karnataka 560034',
                'notes': 'Prefers dal and roti combo',
                'is_active': True
            },
            {
                'name': 'Meera Iyer',
                'mobile': '+919876543214',
                'email': None,
                'address': '654 Indiranagar, Bangalore, Karnataka 560038',
                'notes': 'Orders vegetable clear soup regularly',
                'is_active': True
            },
            {
                'name': 'Suresh Patel',
                'mobile': '+919876543215',
                'email': 'suresh.patel@example.com',
                'address': None,
                'notes': 'Bulk orders for family functions',
                'is_active': True
            },
            {
                'name': 'Divya Nair',
                'mobile': '+919876543216',
                'email': 'divya.nair@example.com',
                'address': '987 HSR Layout, Bangalore, Karnataka 560102',
                'notes': 'Loves avalekki breakfast',
                'is_active': True
            },
            {
                'name': 'Vikram Singh',
                'mobile': '+919876543217',
                'email': None,
                'address': '147 Whitefield, Bangalore, Karnataka 560066',
                'notes': 'Orders cream of broccoli soup weekly',
                'is_active': False
            },
            {
                'name': 'Ananya Krishnan',
                'mobile': '+919876543218',
                'email': 'ananya.k@example.com',
                'address': '258 Electronic City, Bangalore, Karnataka 560100',
                'notes': 'Corporate client - orders for team lunches',
                'is_active': True
            },
            {
                'name': 'Karthik Ramesh',
                'mobile': '+919876543219',
                'email': 'karthik.r@example.com',
                'address': '369 Malleshwaram, Bangalore, Karnataka 560003',
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
