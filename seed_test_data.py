#!/usr/bin/env python
"""
Seed Test Data for Customer Loyalty Analytics Testing

This script creates realistic test data with:
- 25 customers with varying order patterns
- Orders spanning 6 months
- Different loyalty segments (new, repeat, loyal)
- Different recency statuses (active, at-risk, inactive)

Run with: python seed_test_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soupssnacks.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from customers.models import Customer
from catalog.models import Product
from orders.models import Order, OrderItem


def create_test_customers():
    """Create 25 test customers with different profiles"""
    
    customers_data = [
        # Loyal customers (5+ orders) - 5 customers
        {"name": "TEST - Priya Sharma", "mobile": "9900000001", "apartment_name": "Prestige Lakeside", "block": "A"},
        {"name": "TEST - Rajesh Kumar", "mobile": "9900000002", "apartment_name": "Prestige Lakeside", "block": "B"},
        {"name": "TEST - Anita Reddy", "mobile": "9900000003", "apartment_name": "Brigade Gateway", "block": "Tower 1"},
        {"name": "TEST - Suresh Menon", "mobile": "9900000004", "apartment_name": "Brigade Gateway", "block": "Tower 2"},
        {"name": "TEST - Lakshmi Iyer", "mobile": "9900000005", "apartment_name": "Sobha Dream Acres", "block": "Phase 1"},
        
        # Repeat customers (2-4 orders) - 8 customers
        {"name": "TEST - Vikram Singh", "mobile": "9900000006", "apartment_name": "Sobha Dream Acres", "block": "Phase 2"},
        {"name": "TEST - Meera Nair", "mobile": "9900000007", "apartment_name": "Prestige Lakeside", "block": "C"},
        {"name": "TEST - Arjun Patel", "mobile": "9900000008", "apartment_name": "Embassy Springs", "block": "Villa 1"},
        {"name": "TEST - Deepa Rao", "mobile": "9900000009", "apartment_name": "Embassy Springs", "block": "Villa 2"},
        {"name": "TEST - Karthik Murthy", "mobile": "9900000010", "apartment_name": "Mantri Serenity", "block": "A"},
        {"name": "TEST - Sunita Hegde", "mobile": "9900000011", "apartment_name": "Mantri Serenity", "block": "B"},
        {"name": "TEST - Ramesh Gowda", "mobile": "9900000012", "apartment_name": "Salarpuria Sattva", "block": "North"},
        {"name": "TEST - Kavitha Prasad", "mobile": "9900000013", "apartment_name": "Salarpuria Sattva", "block": "South"},
        
        # New customers (1 order) - 7 customers
        {"name": "TEST - Arun Krishnan", "mobile": "9900000014", "apartment_name": "Prestige Lakeside", "block": "D"},
        {"name": "TEST - Divya Shetty", "mobile": "9900000015", "apartment_name": "Brigade Gateway", "block": "Tower 3"},
        {"name": "TEST - Mohan Das", "mobile": "9900000016", "apartment_name": "Sobha Dream Acres", "block": "Phase 3"},
        {"name": "TEST - Rekha Bhat", "mobile": "9900000017", "apartment_name": "Embassy Springs", "block": "Villa 3"},
        {"name": "TEST - Ganesh Pai", "mobile": "9900000018", "apartment_name": "Mantri Serenity", "block": "C"},
        {"name": "TEST - Shwetha Kamath", "mobile": "9900000019", "apartment_name": "Salarpuria Sattva", "block": "East"},
        {"name": "TEST - Venkat Rao", "mobile": "9900000020", "apartment_name": "Prestige Lakeside", "block": "E"},
        
        # Prospects (0 orders) - 5 customers
        {"name": "TEST - Nandini Kulkarni", "mobile": "9900000021", "apartment_name": "Brigade Gateway", "block": "Tower 4"},
        {"name": "TEST - Ashok Joshi", "mobile": "9900000022", "apartment_name": "Sobha Dream Acres", "block": "Phase 4"},
        {"name": "TEST - Pooja Srinivas", "mobile": "9900000023", "apartment_name": "Embassy Springs", "block": "Villa 4"},
        {"name": "TEST - Ravi Shankar", "mobile": "9900000024", "apartment_name": "Mantri Serenity", "block": "D"},
        {"name": "TEST - Uma Mahesh", "mobile": "9900000025", "apartment_name": "Salarpuria Sattva", "block": "West"},
    ]
    
    created_customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            mobile=data["mobile"],
            defaults={
                "name": data["name"],
                "apartment_name": data["apartment_name"],
                "block": data["block"],
                "is_active": True
            }
        )
        if created:
            print(f"  Created customer: {customer.name}")
        else:
            print(f"  Customer exists: {customer.name}")
        created_customers.append(customer)
    
    return created_customers


def get_or_create_products():
    """Get existing products or create test products"""
    
    products = list(Product.objects.filter(is_active=True)[:10])
    
    if len(products) < 5:
        # Create some test products
        test_products = [
            {"name": "TEST - Tomato Soup 250ml", "category": "soups", "unit": "250ml", "selling_price": 80, "unit_cost": 35},
            {"name": "TEST - Samosa (2 pcs)", "category": "snacks", "unit": "2 pcs", "selling_price": 40, "unit_cost": 18},
            {"name": "TEST - Gulab Jamun (4 pcs)", "category": "sweets", "unit": "4 pcs", "selling_price": 60, "unit_cost": 25},
            {"name": "TEST - Veg Biryani", "category": "lunch", "unit": "1 plate", "selling_price": 150, "unit_cost": 65},
            {"name": "TEST - Mango Pickle 200g", "category": "pickle", "unit": "200g", "selling_price": 120, "unit_cost": 50},
        ]
        
        for data in test_products:
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "category": data["category"],
                    "unit": data["unit"],
                    "selling_price": Decimal(str(data["selling_price"])),
                    "unit_cost": Decimal(str(data["unit_cost"])),
                    "is_active": True
                }
            )
            if created:
                print(f"  Created product: {product.name}")
            products.append(product)
    
    return products


def create_order_for_customer(customer, order_date, products):
    """Create a single order with random items"""
    
    order = Order.objects.create(
        customer=customer,
        order_date=order_date,
        status='delivered',
        payment_status='paid',
        order_type='delivery',
        delivery_address=f"{customer.block}, {customer.apartment_name}",
        notes="TEST ORDER - Delete before production"
    )
    
    # Add 1-4 random items
    num_items = random.randint(1, 4)
    selected_products = random.sample(products, min(num_items, len(products)))
    
    for i, product in enumerate(selected_products):
        quantity = random.randint(1, 3)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.selling_price,
            unit_cost_snapshot=product.unit_cost,
            display_order=i
        )
    
    return order


def create_orders_for_customers(customers, products):
    """Create orders with realistic patterns for different customer segments"""
    
    today = date.today()
    
    # Order patterns for different customer types
    order_patterns = {
        # Loyal customers (5+ orders) - first 5 customers
        # Mix of active, at-risk, and one inactive
        0: {"num_orders": 8, "recency": "active", "frequency": "weekly"},      # Very loyal, active
        1: {"num_orders": 6, "recency": "active", "frequency": "biweekly"},    # Loyal, active
        2: {"num_orders": 7, "recency": "at_risk", "frequency": "monthly"},    # Loyal but at-risk
        3: {"num_orders": 5, "recency": "active", "frequency": "monthly"},     # Loyal, active
        4: {"num_orders": 10, "recency": "inactive", "frequency": "monthly"},  # Was very loyal, now inactive
        
        # Repeat customers (2-4 orders) - customers 5-12
        5: {"num_orders": 4, "recency": "active", "frequency": "biweekly"},
        6: {"num_orders": 3, "recency": "active", "frequency": "monthly"},
        7: {"num_orders": 2, "recency": "at_risk", "frequency": "occasional"},
        8: {"num_orders": 4, "recency": "at_risk", "frequency": "occasional"},
        9: {"num_orders": 3, "recency": "inactive", "frequency": "rare"},
        10: {"num_orders": 2, "recency": "active", "frequency": "monthly"},
        11: {"num_orders": 4, "recency": "active", "frequency": "weekly"},
        12: {"num_orders": 3, "recency": "at_risk", "frequency": "monthly"},
        
        # New customers (1 order) - customers 13-19
        13: {"num_orders": 1, "recency": "active", "frequency": None},
        14: {"num_orders": 1, "recency": "active", "frequency": None},
        15: {"num_orders": 1, "recency": "at_risk", "frequency": None},
        16: {"num_orders": 1, "recency": "at_risk", "frequency": None},
        17: {"num_orders": 1, "recency": "inactive", "frequency": None},
        18: {"num_orders": 1, "recency": "inactive", "frequency": None},
        19: {"num_orders": 1, "recency": "active", "frequency": None},
        
        # Prospects (0 orders) - customers 20-24
        # No orders for these
    }
    
    total_orders = 0
    
    for idx, customer in enumerate(customers):
        if idx not in order_patterns:
            print(f"  {customer.name}: Prospect (no orders)")
            continue
        
        pattern = order_patterns[idx]
        num_orders = pattern["num_orders"]
        recency = pattern["recency"]
        
        # Determine last order date based on recency
        if recency == "active":
            last_order_days_ago = random.randint(1, 25)
        elif recency == "at_risk":
            last_order_days_ago = random.randint(35, 85)
        else:  # inactive
            last_order_days_ago = random.randint(95, 150)
        
        # Generate order dates
        order_dates = []
        
        if num_orders == 1:
            order_dates = [today - timedelta(days=last_order_days_ago)]
        else:
            # Spread orders over time based on frequency
            frequency = pattern.get("frequency", "monthly")
            if frequency == "weekly":
                avg_gap = 7
            elif frequency == "biweekly":
                avg_gap = 14
            elif frequency == "monthly":
                avg_gap = 30
            elif frequency == "occasional":
                avg_gap = 45
            else:  # rare
                avg_gap = 60
            
            # Work backwards from last order
            current_date = today - timedelta(days=last_order_days_ago)
            order_dates.append(current_date)
            
            for _ in range(num_orders - 1):
                gap = random.randint(int(avg_gap * 0.7), int(avg_gap * 1.3))
                current_date = current_date - timedelta(days=gap)
                order_dates.append(current_date)
            
            order_dates.reverse()  # Chronological order
        
        # Create orders
        for order_date in order_dates:
            create_order_for_customer(customer, order_date, products)
            total_orders += 1
        
        print(f"  {customer.name}: {num_orders} orders ({recency})")
    
    return total_orders


def main():
    print("\n" + "="*60)
    print("SEEDING TEST DATA FOR CUSTOMER LOYALTY ANALYTICS")
    print("="*60)
    
    print("\n1. Creating test customers...")
    customers = create_test_customers()
    print(f"   Total: {len(customers)} customers")
    
    print("\n2. Getting/creating products...")
    products = get_or_create_products()
    print(f"   Total: {len(products)} products available")
    
    print("\n3. Creating orders...")
    total_orders = create_orders_for_customers(customers, products)
    print(f"   Total: {total_orders} orders created")
    
    print("\n" + "="*60)
    print("SEED DATA SUMMARY")
    print("="*60)
    print(f"""
Customers Created: 25
  - Loyal (5+ orders): 5 customers
  - Repeat (2-4 orders): 8 customers  
  - New (1 order): 7 customers
  - Prospects (0 orders): 5 customers

Recency Distribution:
  - Active (<30 days): ~10 customers
  - At-Risk (31-90 days): ~6 customers
  - Inactive (>90 days): ~4 customers

Orders Created: {total_orders}

All test data is prefixed with "TEST -" for easy identification.
Run 'python cleanup_test_data.py' to remove all test data.
""")
    
    print("="*60)
    print("SEED COMPLETE! Navigate to Analytics to test.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
