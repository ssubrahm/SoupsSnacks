from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Product
from customers.models import Customer
from orders.models import Order, OrderItem

User = get_user_model()


class OrderFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='operator',
            password='operator123',
            role='operator',
        )
        self.client.force_authenticate(user=self.user)

        self.customer = Customer.objects.create(
            name='Test Customer',
            mobile='9876543210',
        )
        self.pickles = Product.objects.create(
            name='Tender Mango Pickle',
            category='pickle',
            unit='500g',
            selling_price=Decimal('180.00'),
        )
        self.soup = Product.objects.create(
            name='Tomato Soup',
            category='soups',
            unit='250ml',
            selling_price=Decimal('80.00'),
        )

        order1 = Order.objects.create(
            customer=self.customer,
            order_date=date(2025, 5, 1),
            fulfillment_date=date(2025, 5, 2),
            status='confirmed',
            payment_status='pending',
        )
        OrderItem.objects.create(
            order=order1,
            product=self.pickles,
            quantity=1,
            unit_price=Decimal('180.00'),
            unit_cost_snapshot=Decimal('90.00'),
        )

        order2 = Order.objects.create(
            customer=self.customer,
            order_date=date(2025, 5, 10),
            fulfillment_date=date(2025, 5, 11),
            status='confirmed',
            payment_status='paid',
        )
        OrderItem.objects.create(
            order=order2,
            product=self.soup,
            quantity=2,
            unit_price=Decimal('80.00'),
            unit_cost_snapshot=Decimal('40.00'),
        )

    def test_filter_by_product_search(self):
        response = self.client.get(
            '/api/orders/orders/',
            {'product_search': 'Tender Mango Pickle 500g'},
        )
        self.assertEqual(response.status_code, 200)
        order_numbers = [o['order_number'] for o in response.data]
        self.assertEqual(len(order_numbers), 1)

    def test_filter_by_date_range_on_order_date(self):
        response = self.client.get(
            '/api/orders/orders/',
            {
                'start_date': '2025-05-01',
                'end_date': '2025-05-05',
                'date_field': 'order_date',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_fulfillment_date(self):
        response = self.client.get(
            '/api/orders/orders/',
            {
                'start_date': '2025-05-11',
                'end_date': '2025-05-11',
                'date_field': 'fulfillment_date',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
