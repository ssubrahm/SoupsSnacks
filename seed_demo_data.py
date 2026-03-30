#!/usr/bin/env python
"""
Seed Demo Data Script for Soups, Snacks & More

This script creates comprehensive demo data to showcase all features:
- Users (admin, operator, cook)
- Customers with Bangalore apartments
- Products with cost components
- Orders with items
- Payments
- Daily offerings

Usage:
    python seed_demo_data.py

To reset and reseed:
    python seed_demo_data.py --reset
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soupssnacks.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from customers.models import Customer
from catalog.models import Product, ProductCostComponent
from orders.models import Order, OrderItem
from payments.models import Payment
from offerings.models import DailyOffering, DailyOfferingItem

User = get_user_model()

# Sample Bangalore apartments
APARTMENTS = [
    ('Prestige Lakeside Habitat', ['A', 'B', 'C', 'D', 'E']),
    ('Brigade Gateway', ['Orion', 'Skywalk', 'Pinnacle']),
    ('Sobha Dream Acres', ['1', '2', '3', '4']),
    ('Embassy Springs', ['Crescent', 'Olive', 'Palm']),
    ('Purva Westend', ['Tower 1', 'Tower 2', 'Tower 3']),
    ('Mantri Serenity', ['A', 'B', 'C']),
    ('Salarpuria Sattva', ['North', 'South', 'East']),
    ('RMZ Galleria', ['Block A', 'Block B']),
]

# Sample Indian names
FIRST_NAMES = [
    'Priya', 'Rahul', 'Ananya', 'Vikram', 'Sneha', 'Arjun', 'Kavya', 'Rohan',
    'Meera', 'Aditya', 'Divya', 'Karthik', 'Lakshmi', 'Sanjay', 'Pooja', 'Vivek',
    'Anjali', 'Suresh', 'Nandini', 'Rajesh', 'Shruti', 'Deepak', 'Swati', 'Ramesh',
    'Gayatri', 'Venkat', 'Radha', 'Krishna', 'Sunita', 'Mohan'
]

LAST_NAMES = [
    'Sharma', 'Patel', 'Reddy', 'Kumar', 'Singh', 'Rao', 'Iyer', 'Nair',
    'Menon', 'Gupta', 'Joshi', 'Shetty', 'Hegde', 'Murthy', 'Bhat', 'Agarwal',
    'Verma', 'Mishra', 'Das', 'Chatterjee', 'Banerjee', 'Pillai', 'Naidu', 'Gowda'
]

# Products with cost breakdown
PRODUCTS = [
    {
        'name': 'Tomato Rasam',
        'category': 'soups',
        'unit': '500ml',
        'selling_price': 120,
        'costs': [
            ('ingredient', 'Tomatoes & spices', 35),
            ('ingredient', 'Tamarind & herbs', 15),
            ('packaging', 'Container & lid', 8),
            ('labor', 'Preparation', 20),
        ]
    },
    {
        'name': 'Mulligatawny Soup',
        'category': 'soups',
        'unit': '500ml',
        'selling_price': 150,
        'costs': [
            ('ingredient', 'Lentils & vegetables', 40),
            ('ingredient', 'Spices & coconut', 20),
            ('packaging', 'Container & lid', 8),
            ('labor', 'Preparation', 25),
        ]
    },
    {
        'name': 'Masala Vada',
        'category': 'snacks',
        'unit': '6 pcs',
        'selling_price': 80,
        'costs': [
            ('ingredient', 'Chana dal & spices', 25),
            ('ingredient', 'Onions & herbs', 10),
            ('packaging', 'Box', 5),
            ('labor', 'Preparation & frying', 15),
        ]
    },
    {
        'name': 'Samosa',
        'category': 'snacks',
        'unit': '4 pcs',
        'selling_price': 60,
        'costs': [
            ('ingredient', 'Potatoes & peas', 15),
            ('ingredient', 'Flour & spices', 10),
            ('packaging', 'Box', 5),
            ('labor', 'Preparation & frying', 12),
        ]
    },
    {
        'name': 'Mysore Pak',
        'category': 'sweets',
        'unit': '250g',
        'selling_price': 200,
        'costs': [
            ('ingredient', 'Besan & ghee', 70),
            ('ingredient', 'Sugar & cardamom', 30),
            ('packaging', 'Gift box', 15),
            ('labor', 'Preparation', 25),
        ]
    },
    {
        'name': 'Gulab Jamun',
        'category': 'sweets',
        'unit': '8 pcs',
        'selling_price': 180,
        'costs': [
            ('ingredient', 'Khoya & flour', 50),
            ('ingredient', 'Sugar syrup', 25),
            ('packaging', 'Container', 10),
            ('labor', 'Preparation', 30),
        ]
    },
    {
        'name': 'Thali Meal',
        'category': 'lunch',
        'unit': '1 plate',
        'selling_price': 180,
        'costs': [
            ('ingredient', 'Rice & dal', 30),
            ('ingredient', 'Vegetables & curry', 40),
            ('ingredient', 'Roti & sides', 25),
            ('packaging', 'Thali container', 15),
            ('labor', 'Preparation', 30),
        ]
    },
    {
        'name': 'Biryani',
        'category': 'lunch',
        'unit': '1 portion',
        'selling_price': 220,
        'costs': [
            ('ingredient', 'Basmati rice', 30),
            ('ingredient', 'Vegetables & spices', 45),
            ('ingredient', 'Saffron & dry fruits', 25),
            ('packaging', 'Container', 12),
            ('labor', 'Preparation', 40),
        ]
    },
    {
        'name': 'Tender Mango Pickle 500g',
        'category': 'pickle',
        'unit': '500g',
        'selling_price': 350,
        'costs': [
            ('ingredient', 'Tender mangoes', 100),
            ('ingredient', 'Spices & oil', 60),
            ('packaging', 'Glass jar', 25),
            ('labor', 'Preparation', 40),
        ]
    },
    {
        'name': 'Tender Mango Pickle 1 KG',
        'category': 'pickle',
        'unit': '1 KG',
        'selling_price': 650,
        'costs': [
            ('ingredient', 'Tender mangoes', 200),
            ('ingredient', 'Spices & oil', 100),
            ('packaging', 'Glass jar', 35),
            ('labor', 'Preparation', 60),
        ]
    },
    {
        'name': 'Lemon Pickle',
        'category': 'pickle',
        'unit': '250g',
        'selling_price': 180,
        'costs': [
            ('ingredient', 'Lemons', 40),
            ('ingredient', 'Spices & oil', 35),
            ('packaging', 'Glass jar', 15),
            ('labor', 'Preparation', 25),
        ]
    },
    {
        'name': 'Snack Combo',
        'category': 'combos',
        'unit': '1 combo',
        'selling_price': 150,
        'costs': [
            ('ingredient', 'Mixed snacks', 50),
            ('ingredient', 'Chutneys', 15),
            ('packaging', 'Combo box', 12),
            ('labor', 'Assembly', 20),
        ]
    },
]


def create_users():
    """Create demo users"""
    print("Creating users...")
    
    users_data = [
        {'username': 'admin', 'email': 'admin@soupssnacks.com', 'password': 'admin123', 
         'first_name': 'Admin', 'last_name': 'User', 'role': 'admin'},
        {'username': 'operator', 'email': 'operator@soupssnacks.com', 'password': 'operator123',
         'first_name': 'Priya', 'last_name': 'Sharma', 'role': 'operator'},
        {'username': 'cook', 'email': 'cook@soupssnacks.com', 'password': 'cook123',
         'first_name': 'Ramesh', 'last_name': 'Kumar', 'role': 'cook'},
    ]
    
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': data['role'],
                'is_staff': data['role'] == 'admin',
                'is_superuser': data['role'] == 'admin',
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"  Created user: {data['username']} ({data['role']})")
        else:
            print(f"  User exists: {data['username']}")
    
    return User.objects.get(username='admin')


def create_customers(count=30):
    """Create demo customers"""
    print(f"Creating {count} customers...")
    
    customers = []
    used_mobiles = set()
    
    for i in range(count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        
        # Generate unique mobile
        while True:
            mobile = f"98{random.randint(10000000, 99999999)}"
            if mobile not in used_mobiles:
                used_mobiles.add(mobile)
                break
        
        apartment, blocks = random.choice(APARTMENTS)
        block = random.choice(blocks)
        flat = f"{random.randint(1, 20)}{random.randint(0, 9):02d}"
        
        customer, created = Customer.objects.get_or_create(
            mobile=mobile,
            defaults={
                'name': name,
                'email': f"{first.lower()}.{last.lower()}@email.com" if random.random() > 0.3 else '',
                'apartment_name': apartment,
                'block': block,
                'flat_number': flat,
                'address': f"Flat {flat}, {block} Block, {apartment}, Bangalore",
                'is_active': random.random() > 0.1,
            }
        )
        
        if created:
            customers.append(customer)
    
    print(f"  Created {len(customers)} new customers")
    return Customer.objects.all()


def create_products():
    """Create demo products with cost components"""
    print("Creating products...")
    
    products = []
    for data in PRODUCTS:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults={
                'category': data['category'],
                'unit': data['unit'],
                'selling_price': Decimal(str(data['selling_price'])),
                'description': f"Delicious homemade {data['name'].lower()}",
                'is_active': True,
            }
        )
        
        if created:
            # Add cost components
            for cost_type, description, amount in data['costs']:
                ProductCostComponent.objects.create(
                    product=product,
                    cost_type=cost_type,
                    description=description,
                    amount=Decimal(str(amount))
                )
            products.append(product)
            print(f"  Created: {data['name']} (₹{data['selling_price']})")
        else:
            print(f"  Exists: {data['name']}")
    
    return Product.objects.filter(is_active=True)


def create_orders(customers, products, count=50):
    """Create demo orders with items and payments"""
    print(f"Creating {count} orders...")
    
    orders_created = 0
    today = date.today()
    
    for i in range(count):
        customer = random.choice(list(customers))
        order_date = today - timedelta(days=random.randint(0, 60))
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            order_type=random.choice(['delivery', 'pickup']),
            status=random.choice(['confirmed', 'confirmed', 'completed', 'completed', 'delivered', 'preparing']),
            delivery_address=customer.address if random.random() > 0.3 else '',
            notes=random.choice(['', '', '', 'Please deliver by evening', 'Extra spicy please', 'No onion']),
        )
        
        # Add 1-4 items
        num_items = random.randint(1, 4)
        selected_products = random.sample(list(products), min(num_items, len(products)))
        
        for idx, product in enumerate(selected_products):
            qty = random.randint(1, 3)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price=product.selling_price,
                unit_cost_snapshot=product.unit_cost,
                display_order=idx
            )
        
        # Add payment for some orders
        if order.status in ['completed', 'delivered'] or random.random() > 0.4:
            total = order.total_revenue
            if total > 0:
                # Full payment or partial
                if random.random() > 0.2:
                    payment_amount = total
                else:
                    payment_amount = Decimal(str(int(total * Decimal(str(random.uniform(0.3, 0.8))))))
                
                Payment.objects.create(
                    order=order,
                    amount=payment_amount,
                    method=random.choice(['upi', 'upi', 'upi', 'cash', 'cash', 'bank_transfer']),
                    payment_date=order_date + timedelta(days=random.randint(0, 3)),
                    reference=f"REF{random.randint(10000, 99999)}" if random.random() > 0.5 else '',
                    remarks=''
                )
        
        orders_created += 1
    
    print(f"  Created {orders_created} orders")
    return Order.objects.all()


def create_offerings(products):
    """Create daily offerings for the past week and upcoming days"""
    print("Creating daily offerings...")
    
    today = date.today()
    offerings_created = 0
    
    for delta in range(-7, 4):
        offering_date = today + timedelta(days=delta)
        
        offering, created = DailyOffering.objects.get_or_create(
            offering_date=offering_date,
            defaults={
                'notes': random.choice([
                    '', 
                    'Special weekend menu!', 
                    'Limited quantities available',
                    'New items added today'
                ]) if random.random() > 0.5 else '',
                'is_active': delta >= -3
            }
        )
        
        if created:
            # Add 4-8 products
            num_products = random.randint(4, 8)
            selected = random.sample(list(products), min(num_products, len(products)))
            
            for idx, product in enumerate(selected):
                DailyOfferingItem.objects.create(
                    offering=offering,
                    product=product,
                    available_quantity=random.choice([None, None, 10, 15, 20, 25]),
                    display_order=idx
                )
            
            offerings_created += 1
    
    print(f"  Created {offerings_created} daily offerings")


def reset_data():
    """Reset all demo data"""
    print("Resetting data...")
    Payment.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    DailyOfferingItem.objects.all().delete()
    DailyOffering.objects.all().delete()
    ProductCostComponent.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    # Keep users
    print("  Data reset complete")


def main():
    """Main function to seed demo data"""
    import argparse
    parser = argparse.ArgumentParser(description='Seed demo data for Soups, Snacks & More')
    parser.add_argument('--reset', action='store_true', help='Reset all data before seeding')
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("  Soups, Snacks & More - Demo Data Seeder")
    print("="*50 + "\n")
    
    if args.reset:
        reset_data()
        print()
    
    # Create data in order
    admin = create_users()
    customers = create_customers(30)
    products = create_products()
    orders = create_orders(customers, products, 50)
    create_offerings(products)
    
    print("\n" + "="*50)
    print("  Demo data seeding complete!")
    print("="*50)
    print(f"""
Summary:
  - Users: {User.objects.count()}
  - Customers: {Customer.objects.count()}
  - Products: {Product.objects.count()}
  - Orders: {Order.objects.count()}
  - Payments: {Payment.objects.count()}
  - Daily Offerings: {DailyOffering.objects.count()}

Login credentials:
  Admin:    admin / admin123
  Operator: operator / operator123
  Cook:     cook / cook123

Start the app:
  ./setup.sh
  
Then open: http://localhost:3000
""")


if __name__ == '__main__':
    main()
