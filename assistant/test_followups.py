"""Unit and integration tests for conversational Ask follow-ups."""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Product
from customers.models import Customer
from orders.models import Order, OrderItem

from .followup import (
    FollowupResult,
    classify_top_customers_followup,
    extract_limit,
    is_show_all,
)
from .services import handle_message

User = get_user_model()


# Natural phrases humans use — each maps to expected action and optional limit
CONVERSATIONAL_LIMIT_PHRASES = [
    ('show me first 6', 6),
    ('now show me first 6', 6),
    ('only 6 now', 6),
    ('just 6', 6),
    ('only 6', 6),
    ('6 please', 6),
    ('6 now', 6),
    ('maybe 6', 6),
    ('about 6', 6),
    ('need 6', 6),
    ('want 6', 6),
    ('top 3', 3),
    ('show 5', 5),
    ('give me 4', 4),
    ('limit to 7', 7),
    ('6 of them', 6),
    ('6 customers', 6),
    ('ok 6', 6),
    ('actually 6', 6),
]

SHOW_ALL_PHRASES = [
    'now show me all 12',
    'all 12 now',
    'yes',
    'yeah',
    'show all tied customers',
    'all of them',
    'everyone',
    'the full list',
    '12 now',  # when tie_count=12
    '12 please',
]

SHOW_ONE_PHRASES = [
    'show only the first one',
    'just one',
    'only one',
    'pick one',
    'first one please',
]


class FollowupClassifierTests(TestCase):
    """Pure classification — no DB."""

    def test_limit_phrases(self):
        for phrase, expected in CONVERSATIONAL_LIMIT_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertFalse(is_show_all(phrase, tie_count=12))
                self.assertEqual(extract_limit(phrase, tie_count=12), expected)
                r = classify_top_customers_followup(phrase, tie_count=12)
                self.assertEqual(r.action, 'show_limit', msg=phrase)
                self.assertEqual(r.limit, expected, msg=phrase)

    def test_show_all_phrases(self):
        for phrase in SHOW_ALL_PHRASES:
            with self.subTest(phrase=phrase):
                r = classify_top_customers_followup(phrase, tie_count=12)
                self.assertEqual(r.action, 'show_all', msg=phrase)

    def test_show_one_phrases(self):
        for phrase in SHOW_ONE_PHRASES:
            with self.subTest(phrase=phrase):
                r = classify_top_customers_followup(phrase, tie_count=12)
                self.assertEqual(r.action, 'show_one', msg=phrase)

    def test_show_all_6_vs_first_6(self):
        r_all = classify_top_customers_followup('show all 6')
        self.assertEqual(r_all.action, 'show_all')
        r_first = classify_top_customers_followup('show first 6')
        self.assertEqual(r_first.action, 'show_limit')
        self.assertEqual(r_first.limit, 6)

    def test_bare_12_equals_tie_count_is_show_all(self):
        r = classify_top_customers_followup('12 now', tie_count=12)
        self.assertEqual(r.action, 'show_all')

    def test_bare_6_with_tie_12_is_limit(self):
        r = classify_top_customers_followup('6 now', tie_count=12)
        self.assertEqual(r.action, 'show_limit')
        self.assertEqual(r.limit, 6)

    def test_decline_phrases(self):
        for phrase in ['no', 'nope', 'nah', 'no thanks', 'never mind', 'skip']:
            with self.subTest(phrase=phrase):
                r = classify_top_customers_followup(phrase)
                self.assertEqual(r.action, 'decline', msg=phrase)


class FollowupIntegrationTests(TestCase):
    """End-to-end follow-up flows via handle_message and API."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='operator',
            password='operator123',
            role='operator',
        )
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            name='Tender Mango Pickle',
            category='pickle',
            unit='500g',
            selling_price=Decimal('700'),
        )

    def _seed_n_tied_customers(self, n: int, revenue: Decimal = Decimal('700')):
        cost = revenue / 2
        for i in range(n):
            customer = Customer.objects.create(
                name=f'Tied Customer {i + 1:02d}',
                mobile=f'9000000{i:04d}',
            )
            order = Order.objects.create(
                customer=customer,
                order_date=date.today(),
                status='confirmed',
                payment_status='paid',
            )
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=1,
                unit_price=revenue,
                unit_cost_snapshot=cost,
            )

    def _tie_clarification_turn(self, n: int = 12):
        self.client.post('/api/assistant/reset/')
        self._seed_n_tied_customers(n)
        return self.client.post(
            '/api/assistant/chat/',
            {'message': 'who is my most valuable customer by revenue'},
            format='json',
        )

    def _followup(self, message, r1, ctx=None, history=None):
        if history is None:
            history = [
                {'role': 'user', 'content': 'who is my most valuable customer by revenue'},
                {'role': 'assistant', 'content': r1.data['message']},
            ]
        payload = {'message': message, 'history': history}
        if ctx:
            payload['clarification_context'] = ctx
        return self.client.post('/api/assistant/chat/', payload, format='json')

    def _assert_limit_followup(self, phrase, expected_count, tie_n=12):
        r1 = self._tie_clarification_turn(tie_n)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup(phrase, r1, ctx=ctx)
        self.assertEqual(r2.data['type'], 'customers', f'{phrase!r}: {r2.data.get("message")}')
        self.assertEqual(len(r2.data['data']['customers']), expected_count, phrase)

    def test_only_6_now(self):
        self._assert_limit_followup('only 6 now', 6)

    def test_just_6(self):
        self._assert_limit_followup('just 6', 6)

    def test_bare_6(self):
        self._assert_limit_followup('6 please', 6)

    def test_many_limit_phrases_via_api(self):
        for phrase, expected in [
            ('show me first 6', 6),
            ('only 6 now', 6),
            ('just 6', 6),
            ('top 3', 3),
            ('6 of them', 6),
        ]:
            with self.subTest(phrase=phrase):
                self._assert_limit_followup(phrase, expected)

    def test_followup_show_all_still_works(self):
        r1 = self._tie_clarification_turn(12)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('now show me all 12', r1, ctx=ctx)
        self.assertEqual(len(r2.data['data']['customers']), 12)

    def test_followup_all_of_them(self):
        r1 = self._tie_clarification_turn(8)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('all of them', r1, ctx=ctx)
        self.assertEqual(len(r2.data['data']['customers']), 8)

    def test_followup_12_now_means_all(self):
        r1 = self._tie_clarification_turn(12)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('12 now', r1, ctx=ctx)
        self.assertEqual(len(r2.data['data']['customers']), 12)

    def test_followup_first_one(self):
        r1 = self._tie_clarification_turn(5)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('just one', r1, ctx=ctx)
        self.assertEqual(len(r2.data['data']['customers']), 1)

    def test_followup_no_thanks(self):
        r1 = self._tie_clarification_turn(5)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('no thanks', r1, ctx=ctx)
        self.assertEqual(r2.data['type'], 'text')
        self.assertIn('no problem', r2.data['message'].lower())

    def test_refine_after_showing_all(self):
        r1 = self._tie_clarification_turn(12)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('show me all 12', r1, ctx=ctx)
        self.assertEqual(len(r2.data['data']['customers']), 12)
        refine_ctx = r2.data.get('clarification_context')
        history = [
            {'role': 'user', 'content': 'who is my most valuable customer by revenue'},
            {'role': 'assistant', 'content': r1.data['message'], 'pending_context': ctx},
            {'role': 'user', 'content': 'show me all 12'},
            {'role': 'assistant', 'content': r2.data['message'], 'pending_context': refine_ctx},
        ]
        r3 = self._followup('only 6 now', r2, ctx=refine_ctx, history=history)
        self.assertEqual(len(r3.data['data']['customers']), 6)

    def test_new_query_escapes_customer_context(self):
        """User can pivot to a new topic mid-conversation."""
        r1 = self._tie_clarification_turn(5)
        ctx = r1.data.get('clarification_context')
        r2 = self._followup('show unpaid orders', r1, ctx=ctx)
        self.assertEqual(r2.data['type'], 'orders')

    def test_plural_query_no_clarification(self):
        self._seed_n_tied_customers(6)
        response = self.client.post(
            '/api/assistant/chat/',
            {'message': 'who are my most valuable customers by revenue'},
            format='json',
        )
        self.assertEqual(response.data['type'], 'customers')
        self.assertEqual(len(response.data['data']['customers']), 6)

    def test_handle_message_unit(self):
        self._seed_n_tied_customers(10)
        ctx = {
            'pending_intent': 'show_top_customers',
            'tie_count': 10,
            'query_params': {
                'months': 6,
                'sort_by': 'revenue',
                'top_tier_only': True,
                'singular_customer_query': True,
                'include_orders': True,
            },
        }
        turn = handle_message('only 6 now', [], ctx, 'operator')
        self.assertEqual(turn['response']['type'], 'customers')
        self.assertEqual(len(turn['response']['data']['customers']), 6)

    @patch('assistant.conversation.resolve_followup_with_llm')
    def test_llm_fallback_for_obscure_phrase(self, mock_llm):
        mock_llm.return_value = FollowupResult(action='show_limit', limit=4)
        self._seed_n_tied_customers(10)
        ctx = {
            'pending_intent': 'show_top_customers',
            'tie_count': 10,
            'query_params': {
                'months': 6,
                'sort_by': 'revenue',
                'top_tier_only': True,
                'singular_customer_query': True,
                'include_orders': True,
            },
        }
        turn = handle_message('hmm lets do four', [], ctx, 'operator')
        self.assertEqual(turn['response']['type'], 'customers')
        self.assertEqual(len(turn['response']['data']['customers']), 4)
        mock_llm.assert_called_once()

    def test_ambiguous_short_reply_gets_helpful_hint(self):
        self._seed_n_tied_customers(10)
        ctx = {
            'pending_intent': 'show_top_customers',
            'tie_count': 10,
            'query_params': {
                'months': 6,
                'sort_by': 'revenue',
                'top_tier_only': True,
                'singular_customer_query': True,
                'include_orders': True,
            },
        }
        turn = handle_message('hmm', [], ctx, 'operator')
        self.assertEqual(turn['response']['type'], 'text')
        self.assertIn('10 customers', turn['response']['message'])
