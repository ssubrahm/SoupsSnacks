from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Product
from customers.models import Customer
from offerings.models import DailyOffering, DailyOfferingItem
from orders.models import Order, OrderItem
from payments.models import Payment

from .export_csv import result_to_csv
from .intent_parser import parse_with_rules
from .models import ChatSession
from .services import handle_message

User = get_user_model()


class AssistantIntentTests(TestCase):
    def test_parse_orders_for_pickles(self):
        intent = parse_with_rules(
            'Show me all orders of Tender Mango Pickle both 500g and 1KG'
        )
        self.assertEqual(intent['intent'], 'list_orders')
        names = intent['params'].get('product_names', [])
        self.assertTrue(any('tender mango pickle' in n.lower() for n in names))

    def test_parse_singular_customer_query_flag(self):
        intent = parse_with_rules('who is my most valuable customer by revenue')
        self.assertTrue(intent['params'].get('singular_customer_query'))
        self.assertTrue(intent['params'].get('top_tier_only'))

    def test_parse_plural_not_singular(self):
        intent = parse_with_rules('who are my most valuable customers by revenue')
        self.assertFalse(intent['params'].get('singular_customer_query'))

    def test_parse_top_customer_profit_singular(self):
        intent = parse_with_rules(
            'Who is my most valuable customer in terms of profitability in the last 6 months'
        )
        self.assertEqual(intent['intent'], 'top_customers')
        self.assertEqual(intent['params'].get('months'), 6)
        self.assertEqual(intent['params'].get('sort_by'), 'profit')
        self.assertTrue(intent['params'].get('top_tier_only'))

    def test_parse_daily_offerings(self):
        intent = parse_with_rules("What's on today's menu?")
        self.assertEqual(intent['intent'], 'daily_offerings')
        self.assertIn('offering_date', intent['params'])

    def test_parse_payment_trends(self):
        intent = parse_with_rules('Show payment trends for the last 3 months')
        self.assertEqual(intent['intent'], 'payment_trends')
        self.assertEqual(intent['params'].get('months'), 3)


class AssistantAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='operator',
            password='operator123',
            role='operator',
        )
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(name='Test', mobile='9999999999')
        self.product = Product.objects.create(
            name='Tender Mango Pickle',
            category='pickle',
            unit='500g',
            selling_price=Decimal('200'),
        )
        order = Order.objects.create(
            customer=self.customer,
            order_date=date.today(),
            status='confirmed',
            payment_status='paid',
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('200'),
            unit_cost_snapshot=Decimal('100'),
        )

    def test_chat_list_orders(self):
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'Show orders for Tender Mango Pickle 500g'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'orders')
        self.assertGreaterEqual(response.data['data']['count'], 1)

    def test_chat_top_customer(self):
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'most profitable customer last 6 months'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'customers')
        self.assertTrue(response.data['data']['customers'])

    def _seed_tied_customers(self):
        customer2 = Customer.objects.create(name='Second Customer', mobile='8888888888')
        order2 = Order.objects.create(
            customer=customer2,
            order_date=date.today(),
            status='confirmed',
            payment_status='paid',
        )
        OrderItem.objects.create(
            order=order2,
            product=self.product,
            quantity=1,
            unit_price=Decimal('700'),
            unit_cost_snapshot=Decimal('350'),
        )
        OrderItem.objects.filter(order__customer=self.customer).update(
            quantity=1, unit_price=Decimal('700')
        )

    def test_chat_followup_show_me_all_12(self):
        self._seed_tied_customers()
        r1 = self.client.post(
            '/api/assistant/chat/',
            {'message': 'who is my most valuable customer by revenue'},
            format='json',
        )
        self.assertEqual(r1.data['type'], 'clarification')
        ctx = r1.data.get('clarification_context')
        r2 = self.client.post(
            '/api/assistant/chat/',
            {
                'message': 'now show me all 12',
                'clarification_context': ctx,
                'history': [
                    {'role': 'user', 'content': 'who is my most valuable customer by revenue'},
                    {'role': 'assistant', 'content': r1.data['message']},
                ],
            },
            format='json',
        )
        self.assertEqual(r2.data['type'], 'customers')
        self.assertGreaterEqual(len(r2.data['data']['customers']), 2)

    def test_chat_followup_all_12_now_phrase(self):
        self._seed_tied_customers()
        r1 = self.client.post(
            '/api/assistant/chat/',
            {'message': 'who is my most valuable customer by revenue'},
            format='json',
        )
        ctx = r1.data.get('clarification_context')
        r2 = self.client.post(
            '/api/assistant/chat/',
            {
                'message': 'all 12 now',
                'history': [
                    {'role': 'user', 'content': 'who is my most valuable customer by revenue'},
                    {
                        'role': 'assistant',
                        'content': r1.data['message'],
                        'pending_context': ctx,
                    },
                ],
            },
            format='json',
        )
        self.assertEqual(r2.data['type'], 'customers', r2.data.get('message'))
        self.assertGreaterEqual(len(r2.data['data']['customers']), 2)

    def test_chat_followup_from_history_only(self):
        """Works even if clarification_context omitted but history retained."""
        self._seed_tied_customers()
        r1 = self.client.post(
            '/api/assistant/chat/',
            {'message': 'who is my most valuable customer by revenue'},
            format='json',
        )
        r2 = self.client.post(
            '/api/assistant/chat/',
            {
                'message': 'now show me all 12',
                'history': [
                    {'role': 'user', 'content': 'who is my most valuable customer by revenue'},
                    {'role': 'assistant', 'content': r1.data['message']},
                ],
            },
            format='json',
        )
        self.assertEqual(r2.data['type'], 'customers')
        self.assertGreaterEqual(len(r2.data['data']['customers']), 2)

    def test_chat_show_all_after_tie_clarification(self):
        self._seed_tied_customers()
        self.client.post(
            '/api/assistant/chat/',
            {'message': 'who is my most valuable customer by revenue'},
            format='json',
        )
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'Show all tied customers'},
            format='json',
        )
        self.assertEqual(response.data['type'], 'customers')
        self.assertGreaterEqual(len(response.data['data']['customers']), 2)

    def test_chat_singular_customer_tie_asks_to_show_all(self):
        self._seed_tied_customers()
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'who is my most valuable customer by revenue'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'clarification')
        self.assertIn("isn't just one", response.data['message'].lower())
        self.assertTrue(len(response.data['data']['options']) >= 1)

    def test_chat_plural_shows_all_tied_immediately(self):
        self._seed_tied_customers()
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'who are my most valuable customers by revenue'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'customers')
        self.assertGreaterEqual(len(response.data['data']['customers']), 2)

    def test_starters_endpoint(self):
        response = self.client.get('/api/assistant/chat/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['starters']) >= 1)
        self.assertIn('session_id', response.data)

    def test_chat_daily_offerings(self):
        offering = DailyOffering.objects.create(offering_date=date.today(), is_active=True)
        DailyOfferingItem.objects.create(
            daily_offering=offering,
            product=self.product,
            available_quantity=10,
        )
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': "What's on today's menu?"},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'offerings')
        self.assertGreaterEqual(response.data['data']['count'], 1)

    def test_chat_payment_trends(self):
        order = Order.objects.first()
        Payment.objects.create(
            order=order,
            payment_date=date.today(),
            amount=Decimal('200'),
            method='upi',
        )
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'Show payment trends for the last 3 months'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'payment_trends')
        self.assertGreaterEqual(response.data['data']['total_count'], 1)

    def test_chat_persists_to_database(self):
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'Show unpaid orders'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        session_id = response.data['session_id']
        session = ChatSession.objects.get(id=session_id, user=self.user)
        self.assertEqual(session.messages.count(), 2)
        self.assertEqual(session.messages.filter(role='user').first().content, 'Show unpaid orders')

    def test_load_session_history(self):
        self.client.post(
            '/api/assistant/chat/',
            {'message': 'Show unpaid orders'},
            format='json',
        )
        session = ChatSession.objects.filter(user=self.user).first()
        response = self.client.get(f'/api/assistant/chat/?session_id={session.id}')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['messages']), 2)

    def test_export_csv_orders(self):
        data = {
            'orders': [
                {
                    'order_number': 'ORD-1',
                    'customer': {'name': 'Test', 'mobile': '999'},
                    'order_date': '2025-01-01',
                    'status': 'confirmed',
                    'payment_status': 'paid',
                    'total_revenue': 100,
                    'total_profit': 50,
                    'matching_items': [],
                }
            ]
        }
        csv_text = result_to_csv('orders', data)
        self.assertIn('ORD-1', csv_text)
        self.assertIn('order_number', csv_text)

    def test_transcribe_requires_audio(self):
        response = self.client.post('/api/assistant/transcribe/')
        self.assertEqual(response.status_code, 400)

    def test_transcribe_without_api_key(self):
        with self.settings(OPENAI_API_KEY=''):
            response = self.client.post(
                '/api/assistant/transcribe/',
                {
                    'audio': SimpleUploadedFile(
                        'test.webm', b'fake-audio', content_type='audio/webm'
                    ),
                },
                format='multipart',
            )
            self.assertEqual(response.status_code, 503)

    def test_export_endpoint(self):
        response = self.client.post(
            '/api/assistant/export/',
            {
                'type': 'payment_trends',
                'data': {
                    'by_method': {
                        'upi': {'count': 2, 'amount': 500, 'label': 'UPI'},
                    },
                    'total_amount': 500,
                },
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn(b'upi', response.content.lower())
