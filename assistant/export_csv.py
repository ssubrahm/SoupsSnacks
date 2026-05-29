"""Export assistant result data to CSV."""

from __future__ import annotations

import csv
import io
from typing import Any


def _rows_for_type(response_type: str, data: dict[str, Any]) -> tuple[list[str], list[list[Any]]]:
    if response_type == 'orders' and data.get('orders'):
        headers = [
            'order_number', 'customer_name', 'mobile', 'order_date', 'status',
            'payment_status', 'revenue', 'profit', 'items',
        ]
        rows = []
        for order in data['orders']:
            items = '; '.join(
                f"{i.get('product_name')} {i.get('product_unit')} x{i.get('quantity')}"
                for i in (order.get('matching_items') or [])
            )
            rows.append([
                order.get('order_number'),
                order.get('customer', {}).get('name'),
                order.get('customer', {}).get('mobile'),
                order.get('order_date'),
                order.get('status'),
                order.get('payment_status'),
                order.get('total_revenue'),
                order.get('total_profit'),
                items,
            ])
        return headers, rows

    if response_type == 'customers' and data.get('customers'):
        headers = [
            'rank', 'customer_name', 'mobile', 'orders', 'revenue', 'profit',
            'apartment', 'block',
        ]
        rows = []
        for i, c in enumerate(data['customers'], start=1):
            rows.append([
                i,
                c.get('customer_name'),
                c.get('mobile'),
                c.get('order_count'),
                c.get('total_spent'),
                c.get('total_profit'),
                c.get('apartment_name'),
                c.get('block'),
            ])
        return headers, rows

    if response_type == 'products' and data.get('products'):
        headers = ['name', 'unit', 'category', 'price', 'margin_percent']
        rows = [
            [p.get('name'), p.get('unit'), p.get('category'), p.get('selling_price'), p.get('margin_percent')]
            for p in data['products']
        ]
        return headers, rows

    if response_type == 'offerings' and data.get('offerings'):
        headers = ['offering_date', 'status', 'product', 'unit', 'category', 'price', 'available_qty']
        rows = []
        for offering in data['offerings']:
            for item in offering.get('items') or []:
                rows.append([
                    offering.get('offering_date'),
                    offering.get('status'),
                    item.get('product_name'),
                    item.get('product_unit'),
                    item.get('category'),
                    item.get('selling_price'),
                    item.get('available_quantity'),
                ])
        return headers, rows

    if response_type == 'payment_trends' and data.get('by_method'):
        headers = ['method', 'count', 'amount', 'share_percent']
        total = float(data.get('total_amount') or 0)
        rows = []
        for method, stats in data['by_method'].items():
            amount = float(stats.get('amount') or 0)
            share = round(amount / total * 100, 1) if total else 0
            rows.append([method, stats.get('count'), amount, share])
        return headers, rows

    return [], []


def result_to_csv(response_type: str, data: dict[str, Any] | None) -> str:
    headers, rows = _rows_for_type(response_type, data or {})
    output = io.StringIO()
    writer = csv.writer(output)
    if headers:
        writer.writerow(headers)
        writer.writerows(rows)
    return output.getvalue()
