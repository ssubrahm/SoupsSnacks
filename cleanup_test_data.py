#!/usr/bin/env python
"""
Cleanup Test Data Script

This script removes all test data created by seed_test_data.py:
- Deletes orders with notes containing "TEST ORDER"
- Deletes customers with names starting with "TEST -"
- Deletes products with names starting with "TEST -"

Run with: python cleanup_test_data.py

IMPORTANT: Run this before deploying to production!
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soupssnacks.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from customers.models import Customer
from catalog.models import Product
from orders.models import Order, OrderItem
from payments.models import Payment


def cleanup_test_data(dry_run=False):
    """
    Remove all test data.
    
    Args:
        dry_run: If True, only shows what would be deleted without actually deleting
    """
    
    print("\n" + "="*60)
    if dry_run:
        print("CLEANUP TEST DATA - DRY RUN (no changes will be made)")
    else:
        print("CLEANUP TEST DATA - DELETING")
    print("="*60)
    
    # Find test orders (by notes or by test customers)
    test_orders = Order.objects.filter(notes__icontains="TEST ORDER")
    test_customer_mobiles = [f"990000000{i}" for i in range(1, 26)]
    test_orders_by_customer = Order.objects.filter(customer__mobile__in=test_customer_mobiles)
    
    # Combine both querysets
    all_test_order_ids = set(test_orders.values_list('id', flat=True)) | set(test_orders_by_customer.values_list('id', flat=True))
    
    print(f"\n1. Test Orders found: {len(all_test_order_ids)}")
    
    # Find test customers
    test_customers = Customer.objects.filter(name__startswith="TEST -")
    test_customers_by_mobile = Customer.objects.filter(mobile__in=test_customer_mobiles)
    all_test_customers = test_customers | test_customers_by_mobile
    
    print(f"2. Test Customers found: {all_test_customers.count()}")
    
    # Find test products
    test_products = Product.objects.filter(name__startswith="TEST -")
    print(f"3. Test Products found: {test_products.count()}")
    
    if dry_run:
        print("\n--- DRY RUN: Showing what would be deleted ---")
        
        print("\nOrders to delete:")
        for order in Order.objects.filter(id__in=all_test_order_ids)[:10]:
            print(f"  - {order.order_number}: {order.customer.name} ({order.order_date})")
        if len(all_test_order_ids) > 10:
            print(f"  ... and {len(all_test_order_ids) - 10} more")
        
        print("\nCustomers to delete:")
        for customer in all_test_customers[:10]:
            print(f"  - {customer.name} ({customer.mobile})")
        if all_test_customers.count() > 10:
            print(f"  ... and {all_test_customers.count() - 10} more")
        
        print("\nProducts to delete:")
        for product in test_products:
            print(f"  - {product.name}")
        
        print("\n" + "="*60)
        print("DRY RUN COMPLETE - No data was deleted")
        print("Run with --execute to actually delete the data")
        print("="*60 + "\n")
        
    else:
        # Actually delete the data
        with transaction.atomic():
            # Delete order items first (cascade should handle this, but being explicit)
            order_items_deleted = OrderItem.objects.filter(order_id__in=all_test_order_ids).count()
            OrderItem.objects.filter(order_id__in=all_test_order_ids).delete()
            print(f"\n   Deleted {order_items_deleted} order items")
            
            # Delete payments for test orders
            payments_deleted = Payment.objects.filter(order_id__in=all_test_order_ids).count()
            Payment.objects.filter(order_id__in=all_test_order_ids).delete()
            print(f"   Deleted {payments_deleted} payments")
            
            # Delete orders
            orders_deleted = Order.objects.filter(id__in=all_test_order_ids).count()
            Order.objects.filter(id__in=all_test_order_ids).delete()
            print(f"   Deleted {orders_deleted} orders")
            
            # Delete customers
            customers_deleted = all_test_customers.count()
            all_test_customers.delete()
            print(f"   Deleted {customers_deleted} customers")
            
            # Delete products
            products_deleted = test_products.count()
            test_products.delete()
            print(f"   Deleted {products_deleted} products")
        
        print("\n" + "="*60)
        print("CLEANUP COMPLETE!")
        print("="*60)
        print(f"""
Summary of deleted data:
  - Order Items: {order_items_deleted}
  - Payments: {payments_deleted}
  - Orders: {orders_deleted}
  - Customers: {customers_deleted}
  - Products: {products_deleted}

Your database is now clean of test data.
""")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up test data from the database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_test_data.py           # Dry run - shows what would be deleted
  python cleanup_test_data.py --execute # Actually delete the test data
  python cleanup_test_data.py --force   # Delete without confirmation prompt
        """
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually delete the data (default is dry run)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt when executing'
    )
    
    args = parser.parse_args()
    
    if args.execute:
        if not args.force:
            print("\n" + "!"*60)
            print("WARNING: This will permanently delete all test data!")
            print("!"*60)
            
            confirm = input("\nType 'DELETE' to confirm: ")
            if confirm != 'DELETE':
                print("Aborted. No data was deleted.")
                return
        
        cleanup_test_data(dry_run=False)
    else:
        cleanup_test_data(dry_run=True)


if __name__ == "__main__":
    main()
