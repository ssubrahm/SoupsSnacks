"""
Core tests for Soups, Snacks & More

Tests cover:
- Product costing calculations
- Order totals and profit calculations
- Payment status updates
- Customer creation
- Import validation
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soupssnacks.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from customers.models import Customer
from catalog.models import Product, ProductCostComponent
from orders.models import Order, OrderItem
from payments.models import Payment

User = get_user_model()


class ProductCostingTests(TestCase):
    """Test product cost calculations"""
    
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Soup',
            category='soups',
            unit='500ml',
            selling_price=Decimal('100.00'),
        )
    
    def test_product_without_components_has_zero_cost(self):
        """Product with no cost components should have zero unit cost"""
        self.assertEqual(self.product.unit_cost, Decimal('0'))
    
    def test_product_cost_with_components(self):
        """Product cost should sum all components"""
        ProductCostComponent.objects.create(
            product=self.product,
            cost_type='ingredient',
            description='Vegetables',
            amount=Decimal('30.00')
        )
        ProductCostComponent.objects.create(
            product=self.product,
            cost_type='packaging',
            description='Container',
            amount=Decimal('10.00')
        )
        ProductCostComponent.objects.create(
            product=self.product,
            cost_type='labor',
            description='Preparation',
            amount=Decimal('15.00')
        )
        
        self.assertEqual(self.product.unit_cost, Decimal('55.00'))
    
    def test_product_profit_calculation(self):
        """Profit should be selling price minus unit cost"""
        ProductCostComponent.objects.create(
            product=self.product,
            cost_type='ingredient',
            description='Ingredients',
            amount=Decimal('40.00')
        )
        
        self.assertEqual(self.product.unit_profit, Decimal('60.00'))
    
    def test_product_margin_calculation(self):
        """Margin should be profit / selling price * 100"""
        ProductCostComponent.objects.create(
            product=self.product,
            cost_type='ingredient',
            description='Ingredients',
            amount=Decimal('60.00')
        )
        
        # Profit = 100 - 60 = 40
        # Margin = 40 / 100 * 100 = 40%
        self.assertEqual(self.product.margin_percent, Decimal('40.00'))
    
    def test_zero_selling_price_margin(self):
        """Zero selling price should result in zero margin"""
        self.product.selling_price = Decimal('0')
        self.product.save()
        
        self.assertEqual(self.product.margin_percent, Decimal('0'))


class OrderCalculationTests(TestCase):
    """Test order total and profit calculations"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            mobile='9876543210'
        )
        
        self.product1 = Product.objects.create(
            name='Product 1',
            category='soups',
            unit='1 pc',
            selling_price=Decimal('100.00')
        )
        ProductCostComponent.objects.create(
            product=self.product1,
            cost_type='ingredient',
            amount=Decimal('40.00')
        )
        
        self.product2 = Product.objects.create(
            name='Product 2',
            category='snacks',
            unit='1 pc',
            selling_price=Decimal('50.00')
        )
        ProductCostComponent.objects.create(
            product=self.product2,
            cost_type='ingredient',
            amount=Decimal('20.00')
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            order_date=date.today()
        )
    
    def test_empty_order_totals(self):
        """Empty order should have zero totals"""
        self.assertEqual(self.order.total_revenue, Decimal('0'))
        self.assertEqual(self.order.total_cost, Decimal('0'))
        self.assertEqual(self.order.total_profit, Decimal('0'))
    
    def test_order_revenue_calculation(self):
        """Order revenue should sum item revenues"""
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            unit_price=self.product1.selling_price,
            unit_cost_snapshot=self.product1.unit_cost
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=3,
            unit_price=self.product2.selling_price,
            unit_cost_snapshot=self.product2.unit_cost
        )
        
        # Revenue = (100 * 2) + (50 * 3) = 200 + 150 = 350
        self.assertEqual(self.order.total_revenue, Decimal('350.00'))
    
    def test_order_cost_uses_snapshot(self):
        """Order cost should use cost snapshot, not current cost"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            unit_price=self.product1.selling_price,
            unit_cost_snapshot=Decimal('50.00')  # Different from product's current cost
        )
        
        # Cost = 50 * 2 = 100 (using snapshot)
        self.assertEqual(self.order.total_cost, Decimal('100.00'))
    
    def test_order_profit_calculation(self):
        """Order profit should be revenue minus cost"""
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            unit_price=Decimal('100.00'),
            unit_cost_snapshot=Decimal('40.00')
        )
        
        # Profit = (100 * 2) - (40 * 2) = 200 - 80 = 120
        self.assertEqual(self.order.total_profit, Decimal('120.00'))
    
    def test_order_item_count(self):
        """Item count should count distinct items"""
        OrderItem.objects.create(
            order=self.order, product=self.product1, quantity=2,
            unit_price=Decimal('100.00'), unit_cost_snapshot=Decimal('40.00')
        )
        OrderItem.objects.create(
            order=self.order, product=self.product2, quantity=5,
            unit_price=Decimal('50.00'), unit_cost_snapshot=Decimal('20.00')
        )
        
        self.assertEqual(self.order.item_count, 2)
    
    def test_order_total_quantity(self):
        """Total quantity should sum all item quantities"""
        OrderItem.objects.create(
            order=self.order, product=self.product1, quantity=2,
            unit_price=Decimal('100.00'), unit_cost_snapshot=Decimal('40.00')
        )
        OrderItem.objects.create(
            order=self.order, product=self.product2, quantity=5,
            unit_price=Decimal('50.00'), unit_cost_snapshot=Decimal('20.00')
        )
        
        self.assertEqual(self.order.total_quantity, 7)


class PaymentStatusTests(TestCase):
    """Test payment status auto-updates"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            mobile='9876543210'
        )
        
        self.product = Product.objects.create(
            name='Product',
            category='soups',
            unit='1 pc',
            selling_price=Decimal('100.00')
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            order_date=date.today()
        )
        
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('100.00'),
            unit_cost_snapshot=Decimal('40.00')
        )
        # Order total = 200
    
    def test_new_order_status_is_pending(self):
        """New order should have pending payment status"""
        self.assertEqual(self.order.payment_status, 'pending')
    
    def test_full_payment_sets_paid(self):
        """Full payment should set status to paid"""
        Payment.objects.create(
            order=self.order,
            amount=Decimal('200.00'),
            method='upi',
            payment_date=date.today()
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
    
    def test_partial_payment_sets_partial(self):
        """Partial payment should set status to partial"""
        Payment.objects.create(
            order=self.order,
            amount=Decimal('100.00'),
            method='cash',
            payment_date=date.today()
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'partial')
    
    def test_multiple_payments_to_full(self):
        """Multiple partial payments adding to full should set paid"""
        Payment.objects.create(
            order=self.order,
            amount=Decimal('80.00'),
            method='cash',
            payment_date=date.today()
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'partial')
        
        Payment.objects.create(
            order=self.order,
            amount=Decimal('120.00'),
            method='upi',
            payment_date=date.today()
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
    
    def test_deleting_payment_updates_status(self):
        """Deleting a payment should recalculate status"""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('200.00'),
            method='upi',
            payment_date=date.today()
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        
        payment.delete()
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')


class CustomerTests(TestCase):
    """Test customer creation and validation"""
    
    def test_create_customer_minimal(self):
        """Create customer with minimal required fields"""
        customer = Customer.objects.create(
            name='Test User',
            mobile='9876543210'
        )
        
        self.assertEqual(customer.name, 'Test User')
        self.assertEqual(customer.mobile, '9876543210')
        self.assertTrue(customer.is_active)
    
    def test_create_customer_full(self):
        """Create customer with all fields"""
        customer = Customer.objects.create(
            name='Full User',
            mobile='9876543211',
            email='full@test.com',
            apartment_name='Test Apartments',
            block='A',
            flat_number='101',
            address='Full address here'
        )
        
        self.assertEqual(customer.apartment_name, 'Test Apartments')
        self.assertEqual(customer.block, 'A')
    
    def test_customer_unique_mobile(self):
        """Mobile number should be unique"""
        Customer.objects.create(name='User 1', mobile='9876543210')
        
        with self.assertRaises(Exception):
            Customer.objects.create(name='User 2', mobile='9876543210')


class OrderNumberTests(TestCase):
    """Test order number generation"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            mobile='9876543210'
        )
    
    def test_order_number_format(self):
        """Order number should follow ORD-YYYYMMDD-XXXX format"""
        order = Order.objects.create(
            customer=self.customer,
            order_date=date.today()
        )
        
        self.assertTrue(order.order_number.startswith('ORD-'))
        self.assertEqual(len(order.order_number), 18)  # ORD-YYYYMMDD-XXXX
    
    def test_order_numbers_are_unique(self):
        """Each order should get unique number"""
        order1 = Order.objects.create(customer=self.customer, order_date=date.today())
        order2 = Order.objects.create(customer=self.customer, order_date=date.today())
        
        self.assertNotEqual(order1.order_number, order2.order_number)


if __name__ == '__main__':
    import unittest
    unittest.main()
