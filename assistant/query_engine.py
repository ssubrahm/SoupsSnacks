"""Execute structured business queries for the conversational assistant."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Q

from catalog.models import Product
from customers.models import Customer
from offerings.models import DailyOffering
from orders.models import Order, OrderItem
from payments.models import Payment


def _float(value) -> float:
    if value is None:
        return 0.0
    return float(value)


def _order_to_dict(order: Order, matching_items: list[OrderItem] | None = None) -> dict[str, Any]:
    items = matching_items if matching_items is not None else list(order.items.all())
    return {
        'id': order.id,
        'order_number': order.order_number,
        'order_date': order.order_date.isoformat(),
        'fulfillment_date': order.fulfillment_date.isoformat() if order.fulfillment_date else None,
        'status': order.status,
        'payment_status': order.payment_status,
        'customer': {
            'id': order.customer_id,
            'name': order.customer.name,
            'mobile': order.customer.mobile,
            'apartment_name': order.customer.apartment_name,
            'block': order.customer.block,
        },
        'total_revenue': _float(order.total_revenue),
        'total_profit': _float(order.total_profit),
        'item_count': order.item_count,
        'matching_items': [
            {
                'product_name': item.product.name,
                'product_unit': item.product.unit,
                'quantity': item.quantity,
                'unit_price': _float(item.unit_price),
                'line_total': _float(item.line_total),
                'line_profit': _float(item.line_profit),
            }
            for item in items
        ],
    }


def resolve_products(
    product_names: list[str] | None = None,
    product_units: list[str] | None = None,
    product_search: str | None = None,
) -> tuple[list[Product], list[dict[str, Any]]]:
    """
    Resolve product filters to Product queryset.
    Returns (products, ambiguous_groups) where ambiguous_groups needs clarification.
    """
    names = [n.strip() for n in (product_names or []) if n and n.strip()]
    units = [u.strip() for u in (product_units or []) if u and u.strip()]
    search = (product_search or '').strip()

    qs = Product.objects.filter(is_active=True)

    if names:
        name_q = Q()
        for name in names:
            name_q |= Q(name__icontains=name)
        qs = qs.filter(name_q)

    if units:
        unit_q = Q()
        for unit in units:
            unit_q |= Q(unit__icontains=unit.replace(' ', '')) | Q(unit__icontains=unit)
        qs = qs.filter(unit_q)

    if search and not names:
        terms = [t for t in search.split() if t]
        for term in terms:
            qs = qs.filter(Q(name__icontains=term) | Q(unit__icontains=term))

    products = list(qs.order_by('name', 'unit'))

    if not products and search:
        # Broader fallback on base product name
        base = search.split()[0] if search.split() else search
        products = list(
            Product.objects.filter(is_active=True, name__icontains=base).order_by('name', 'unit')
        )

    return products, []


def list_orders(
    product_ids: list[int] | None = None,
    product_search: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    date_field: str = 'order_date',
    status: str | None = None,
    payment_status: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List orders optionally filtered by products and date range."""
    if date_field not in ('order_date', 'fulfillment_date'):
        date_field = 'order_date'

    qs = (
        Order.objects.select_related('customer')
        .prefetch_related('items__product')
        .exclude(status='cancelled')
        .order_by('-order_date', '-id')
    )

    if start_date:
        qs = qs.filter(**{f'{date_field}__gte': start_date})
    if end_date:
        qs = qs.filter(**{f'{date_field}__lte': end_date})
    if status:
        qs = qs.filter(status=status)
    if payment_status:
        qs = qs.filter(payment_status=payment_status)

    if product_ids:
        qs = qs.filter(items__product_id__in=product_ids).distinct()

    if product_search:
        terms = [t for t in product_search.split() if t]
        for term in terms:
            qs = qs.filter(
                Q(items__product__name__icontains=term) | Q(items__product__unit__icontains=term)
            )
        qs = qs.distinct()

    orders = list(qs[:limit])
    product_id_set = set(product_ids or [])

    rows = []
    total_revenue = Decimal('0')
    total_profit = Decimal('0')

    for order in orders:
        if product_id_set:
            matching = [i for i in order.items.all() if i.product_id in product_id_set]
        elif product_search:
            terms = [t.lower() for t in product_search.split() if t]
            matching = [
                i
                for i in order.items.all()
                if all(
                    t in i.product.name.lower() or t in i.product.unit.lower() for t in terms
                )
            ]
        else:
            matching = list(order.items.all())

        if (product_ids or product_search) and not matching:
            continue

        rows.append(_order_to_dict(order, matching))
        total_revenue += order.total_revenue
        total_profit += order.total_profit

    return {
        'count': len(rows),
        'total_revenue': _float(total_revenue),
        'total_profit': _float(total_profit),
        'orders': rows,
        'filters': {
            'product_ids': product_ids,
            'product_search': product_search,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'date_field': date_field,
        },
    }


def top_customers(
    months: int = 6,
    start_date: date | None = None,
    end_date: date | None = None,
    sort_by: str = 'profit',
    limit: int = 5,
    top_tier_only: bool = False,
    include_orders: bool = True,
) -> dict[str, Any]:
    """Rank customers by profit or revenue over a period."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=months * 30)

    orders = (
        Order.objects.filter(order_date__gte=start_date, order_date__lte=end_date)
        .exclude(status='cancelled')
        .select_related('customer')
        .prefetch_related('items__product')
        .order_by('-order_date')
    )

    customer_stats: dict[int, dict[str, Any]] = {}

    for order in orders:
        cid = order.customer_id
        if cid not in customer_stats:
            customer_stats[cid] = {
                'customer_id': cid,
                'customer_name': order.customer.name,
                'mobile': order.customer.mobile,
                'apartment_name': order.customer.apartment_name,
                'block': order.customer.block,
                'order_count': 0,
                'total_spent': Decimal('0'),
                'total_profit': Decimal('0'),
                'orders': [],
            }

        stats = customer_stats[cid]
        stats['order_count'] += 1
        order_spent = Decimal('0')
        order_profit = Decimal('0')

        order_items = []
        for item in order.items.all():
            price = item.unit_price or Decimal('0')
            cost = item.unit_cost_snapshot or Decimal('0')
            qty = item.quantity or 0
            line_total = qty * price
            line_profit = qty * (price - cost)
            stats['total_spent'] += line_total
            stats['total_profit'] += line_profit
            order_spent += line_total
            order_profit += line_profit
            order_items.append(
                {
                    'product_name': item.product.name,
                    'product_unit': item.product.unit,
                    'quantity': qty,
                    'line_total': _float(line_total),
                    'line_profit': _float(line_profit),
                }
            )

        if include_orders:
            stats['orders'].append(
                {
                    'order_number': order.order_number,
                    'order_date': order.order_date.isoformat(),
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'total_spent': _float(order_spent),
                    'total_profit': _float(order_profit),
                    'items': order_items,
                }
            )

    result = list(customer_stats.values())
    metric_key = 'total_profit' if sort_by == 'profit' else 'total_spent'
    result.sort(key=lambda x: float(x[metric_key]), reverse=True)

    if top_tier_only and result:
        peak = float(result[0][metric_key])
        result = [r for r in result if abs(float(r[metric_key]) - peak) < 0.01]
    else:
        result = result[:limit]

    peak_value = _float(result[0][metric_key]) if result else 0.0

    for row in result:
        row['total_spent'] = _float(row['total_spent'])
        row['total_profit'] = _float(row['total_profit'])

    return {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'sort_by': sort_by,
        'top_tier_only': top_tier_only,
        'peak_value': peak_value,
        'customers': result,
    }


def unpaid_orders(limit: int = 50) -> dict[str, Any]:
    qs = (
        Order.objects.filter(payment_status__in=['pending', 'partial'])
        .exclude(status='cancelled')
        .select_related('customer')
        .prefetch_related('items__product')
        .order_by('-order_date')
    )
    return {
        'count': qs.count(),
        'orders': [_order_to_dict(o) for o in qs[:limit]],
    }


def product_catalog_summary(search: str | None = None) -> dict[str, Any]:
    qs = Product.objects.filter(is_active=True).order_by('name', 'unit')
    if search:
        terms = [t for t in search.split() if t]
        for term in terms:
            qs = qs.filter(Q(name__icontains=term) | Q(unit__icontains=term))
    products = [
        {
            'id': p.id,
            'name': p.name,
            'unit': p.unit,
            'category': p.category,
            'selling_price': _float(p.selling_price),
            'margin_percent': _float(p.margin_percent),
        }
        for p in qs[:50]
    ]
    return {'count': len(products), 'products': products}


def get_catalog_context() -> str:
    """Compact product list for LLM context."""
    lines = []
    for p in Product.objects.filter(is_active=True).order_by('name', 'unit')[:80]:
        lines.append(f"- {p.name} ({p.unit}) [{p.category}]")
    return '\n'.join(lines) if lines else 'No active products.'


def daily_offerings(
    offering_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    active_only: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """Fetch daily menu offerings with product items."""
    qs = DailyOffering.objects.prefetch_related('items__product').order_by('-offering_date')

    if offering_date:
        qs = qs.filter(offering_date=offering_date)
    else:
        if start_date:
            qs = qs.filter(offering_date__gte=start_date)
        if end_date:
            qs = qs.filter(offering_date__lte=end_date)
        if not start_date and not end_date:
            qs = qs.filter(offering_date__gte=date.today() - timedelta(days=7))

    if active_only:
        qs = qs.filter(is_active=True)

    offerings = []
    for offering in qs[:limit]:
        items = []
        for item in offering.items.all():
            product = item.product
            items.append(
                {
                    'product_name': product.name,
                    'product_unit': product.unit,
                    'category': product.category,
                    'selling_price': _float(product.selling_price),
                    'available_quantity': item.available_quantity,
                    'display_order': item.display_order,
                }
            )
        offerings.append(
            {
                'id': offering.id,
                'offering_date': offering.offering_date.isoformat(),
                'status': offering.status,
                'is_active': offering.is_active,
                'notes': offering.notes or '',
                'item_count': len(items),
                'items': items,
            }
        )

    return {
        'count': len(offerings),
        'offerings': offerings,
        'filters': {
            'offering_date': offering_date.isoformat() if offering_date else None,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'active_only': active_only,
        },
    }


def payment_trends(
    months: int = 6,
    start_date: date | None = None,
    end_date: date | None = None,
    method: str | None = None,
) -> dict[str, Any]:
    """Aggregate payment totals by method over a period."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=months * 30)

    qs = Payment.objects.filter(
        payment_date__gte=start_date,
        payment_date__lte=end_date,
    ).select_related('order', 'order__customer')

    if method:
        qs = qs.filter(method=method)

    total_amount = Decimal('0')
    total_count = 0
    by_method: dict[str, dict[str, Any]] = {}

    for payment in qs:
        total_count += 1
        amount = payment.amount or Decimal('0')
        total_amount += amount
        bucket = by_method.setdefault(
            payment.method,
            {'count': 0, 'amount': Decimal('0'), 'label': payment.get_method_display()},
        )
        bucket['count'] += 1
        bucket['amount'] += amount

    for stats in by_method.values():
        stats['amount'] = _float(stats['amount'])

    return {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total_count': total_count,
        'total_amount': _float(total_amount),
        'by_method': by_method,
        'method_filter': method,
    }
