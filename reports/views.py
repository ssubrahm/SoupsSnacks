import csv
from decimal import Decimal
from datetime import date, timedelta
from django.http import HttpResponse
from django.db import models
from django.db.models import Sum, Count, Avg, F, Q, Max, Value
from django.db.models.functions import TruncDate, TruncMonth, Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.permissions import IsOperator
from orders.models import Order, OrderItem
from customers.models import Customer
from catalog.models import Product
from payments.models import Payment


def safe_float(value):
    """Safely convert Decimal/None to float"""
    if value is None:
        return 0.0
    return float(value)


def get_order_totals(orders):
    """Calculate revenue and profit for a queryset of orders by aggregating items"""
    # Get all order items for these orders
    order_ids = list(orders.values_list('id', flat=True))
    
    if not order_ids:
        return 0.0, 0.0, 0.0
    
    totals = OrderItem.objects.filter(order_id__in=order_ids).aggregate(
        total_revenue=Sum(
            F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
            output_field=models.DecimalField()
        ),
        total_cost=Sum(
            F('quantity') * Coalesce(F('unit_cost_snapshot'), Value(Decimal('0'))),
            output_field=models.DecimalField()
        )
    )
    
    revenue = safe_float(totals['total_revenue'])
    cost = safe_float(totals['total_cost'])
    profit = revenue - cost
    
    return revenue, cost, profit


class DashboardView(APIView):
    """Dashboard KPIs and widgets"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            today = date.today()
            first_of_month = today.replace(day=1)
            
            # Orders today
            orders_today = Order.objects.filter(order_date=today).count()
            
            # Pending orders
            pending_orders = Order.objects.filter(
                status__in=['draft', 'confirmed', 'preparing', 'ready']
            ).count()
            
            # Sales today - calculate from items
            today_orders = Order.objects.filter(order_date=today).exclude(status='cancelled')
            sales_today, _, _ = get_order_totals(today_orders)
            
            # Sales and profit this month
            month_orders = Order.objects.filter(order_date__gte=first_of_month).exclude(status='cancelled')
            sales_month, _, profit_month = get_order_totals(month_orders)
            
            # Unpaid amount
            unpaid_orders = Order.objects.filter(
                payment_status__in=['pending', 'partial']
            ).exclude(status='cancelled')
            
            total_unpaid = Decimal('0')
            for order in unpaid_orders:
                order_revenue = sum(item.line_total for item in order.items.all())
                paid = order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
                total_unpaid += order_revenue - paid
            
            # Top 5 products this month
            top_products_qs = OrderItem.objects.filter(
                order__order_date__gte=first_of_month
            ).exclude(order__status='cancelled').values(
                'product__name', 'product__id'
            ).annotate(
                total_qty=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('unit_price'))
            ).order_by('-total_qty')[:5]
            
            top_products = []
            for p in top_products_qs:
                top_products.append({
                    'product__name': p['product__name'],
                    'product__id': p['product__id'],
                    'total_qty': p['total_qty'] or 0,
                    'total_revenue': safe_float(p['total_revenue']),
                })
            
            # Top 5 customers this month - aggregate from items
            top_customers_qs = OrderItem.objects.filter(
                order__order_date__gte=first_of_month
            ).exclude(order__status='cancelled').values(
                'order__customer__name', 'order__customer__id'
            ).annotate(
                order_count=Count('order', distinct=True),
                total_spent=Sum(F('quantity') * F('unit_price'))
            ).order_by('-total_spent')[:5]
            
            top_customers = []
            for c in top_customers_qs:
                top_customers.append({
                    'customer__name': c['order__customer__name'],
                    'customer__id': c['order__customer__id'],
                    'order_count': c['order_count'] or 0,
                    'total_spent': safe_float(c['total_spent']),
                })
            
            # Orders by status
            status_counts = list(Order.objects.values('status').annotate(
                count=Count('id')
            ).order_by('status'))
            
            # Payment status counts
            payment_counts = list(Order.objects.exclude(status='cancelled').values(
                'payment_status'
            ).annotate(count=Count('id')).order_by('payment_status'))
            
            return Response({
                'orders_today': orders_today,
                'pending_orders': pending_orders,
                'sales_today': sales_today,
                'sales_month': sales_month,
                'profit_month': profit_month,
                'unpaid_amount': safe_float(total_unpaid),
                'top_products': top_products,
                'top_customers': top_customers,
                'status_counts': status_counts,
                'payment_counts': payment_counts,
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalesReportView(APIView):
    """Sales report by date range"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            group_by = request.query_params.get('group_by', 'day')
            
            # Default to last 30 days
            if not end_date:
                end_date = date.today()
            else:
                end_date = date.fromisoformat(end_date)
            
            if not start_date:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = date.fromisoformat(start_date)
            
            # Get orders in range with prefetched items
            orders = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date
            ).exclude(status='cancelled').prefetch_related('items')
            
            # Calculate totals using Python (avoid SQLite issues)
            total_orders = 0
            total_revenue = Decimal('0')
            total_profit = Decimal('0')
            
            # Group by date using Python
            daily_stats = {}
            
            for order in orders:
                total_orders += 1
                order_date = order.order_date
                
                # Calculate order revenue and profit from items
                order_revenue = Decimal('0')
                order_cost = Decimal('0')
                for item in order.items.all():
                    price = item.unit_price or Decimal('0')
                    cost = item.unit_cost_snapshot or Decimal('0')
                    qty = item.quantity or 0
                    order_revenue += qty * price
                    order_cost += qty * cost
                
                order_profit = order_revenue - order_cost
                total_revenue += order_revenue
                total_profit += order_profit
                
                # Group by date
                if group_by == 'month':
                    period_key = order_date.replace(day=1)
                else:
                    period_key = order_date
                
                if period_key not in daily_stats:
                    daily_stats[period_key] = {
                        'orders': 0,
                        'revenue': Decimal('0'),
                        'profit': Decimal('0')
                    }
                
                daily_stats[period_key]['orders'] += 1
                daily_stats[period_key]['revenue'] += order_revenue
                daily_stats[period_key]['profit'] += order_profit
            
            # Build response data
            data = []
            for period_key in sorted(daily_stats.keys()):
                stats = daily_stats[period_key]
                data.append({
                    'period': period_key.isoformat(),
                    'orders': stats['orders'],
                    'revenue': float(stats['revenue']),
                    'profit': float(stats['profit']),
                })
            
            avg_order = float(total_revenue) / total_orders if total_orders > 0 else 0
            
            return Response({
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'summary': {
                    'total_orders': total_orders,
                    'total_revenue': float(total_revenue),
                    'total_profit': float(total_profit),
                    'avg_order_value': round(avg_order, 2),
                },
                'data': data
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerReportView(APIView):
    """Customer-wise sales report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            sort_by = request.query_params.get('sort_by', 'total_spent')
            
            # Default to last 90 days
            if not end_date:
                end_date = date.today()
            else:
                end_date = date.fromisoformat(end_date)
            
            if not start_date:
                start_date = end_date - timedelta(days=90)
            else:
                start_date = date.fromisoformat(start_date)
            
            # Get orders with items using Python calculation (avoid SQLite issues)
            orders = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date
            ).exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            # Aggregate by customer using Python
            customer_stats = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_stats:
                    customer_stats[cid] = {
                        'customer': order.customer,
                        'order_count': 0,
                        'total_spent': Decimal('0'),
                        'total_profit': Decimal('0'),
                        'last_order': None
                    }
                
                customer_stats[cid]['order_count'] += 1
                if customer_stats[cid]['last_order'] is None or order.order_date > customer_stats[cid]['last_order']:
                    customer_stats[cid]['last_order'] = order.order_date
                
                for item in order.items.all():
                    price = item.unit_price or Decimal('0')
                    cost = item.unit_cost_snapshot or Decimal('0')
                    qty = item.quantity or 0
                    customer_stats[cid]['total_spent'] += qty * price
                    customer_stats[cid]['total_profit'] += qty * (price - cost)
            
            # Calculate total for percentage
            total_revenue = sum(float(s['total_spent']) for s in customer_stats.values())
            
            # Build result list
            result = []
            for cid, stats in customer_stats.items():
                customer = stats['customer']
                spent = float(stats['total_spent'])
                order_count = stats['order_count']
                avg_order = spent / order_count if order_count > 0 else 0
                pct = (spent / total_revenue * 100) if total_revenue else 0
                result.append({
                    'customer_id': cid,
                    'customer_name': customer.name,
                    'mobile': customer.mobile,
                    'apartment': customer.apartment_name,
                    'block': customer.block,
                    'order_count': order_count,
                    'total_spent': spent,
                    'total_profit': float(stats['total_profit']),
                    'avg_order_value': round(avg_order, 2),
                    'last_order': stats['last_order'].isoformat() if stats['last_order'] else None,
                    'percentage_share': round(pct, 2),
                })
            
            # Sort
            if sort_by == 'order_count':
                result.sort(key=lambda x: x['order_count'], reverse=True)
            else:
                result.sort(key=lambda x: x['total_spent'], reverse=True)
            
            return Response({
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_revenue': total_revenue,
                'customer_count': len(result),
                'data': result
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReportView(APIView):
    """Product-wise sales and profitability report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            category = request.query_params.get('category')
            sort_by = request.query_params.get('sort_by', 'total_revenue')
            
            # Default to last 90 days
            if not end_date:
                end_date = date.today()
            else:
                end_date = date.fromisoformat(end_date)
            
            if not start_date:
                start_date = end_date - timedelta(days=90)
            else:
                start_date = date.fromisoformat(start_date)
            
            # Get order items with Python calculation (avoid SQLite issues)
            orders = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date
            ).exclude(status='cancelled').prefetch_related('items__product')
            
            if category:
                # We'll filter in Python
                pass
            
            # Aggregate by product using Python
            product_stats = {}
            order_products = {}  # Track unique orders per product
            
            for order in orders:
                for item in order.items.all():
                    if category and item.product.category != category:
                        continue
                    
                    pid = item.product_id
                    if pid not in product_stats:
                        product_stats[pid] = {
                            'product': item.product,
                            'total_qty': 0,
                            'total_revenue': Decimal('0'),
                            'total_cost': Decimal('0'),
                        }
                        order_products[pid] = set()
                    
                    price = item.unit_price or Decimal('0')
                    cost = item.unit_cost_snapshot or Decimal('0')
                    qty = item.quantity or 0
                    
                    product_stats[pid]['total_qty'] += qty
                    product_stats[pid]['total_revenue'] += qty * price
                    product_stats[pid]['total_cost'] += qty * cost
                    order_products[pid].add(order.id)
            
            # Build result
            result = []
            for pid, stats in product_stats.items():
                product = stats['product']
                revenue = float(stats['total_revenue'])
                cost = float(stats['total_cost'])
                profit = revenue - cost
                margin = (profit / revenue * 100) if revenue else 0
                
                result.append({
                    'product_id': pid,
                    'product_name': product.name,
                    'category': product.category,
                    'unit_size': product.unit,
                    'selling_price': float(product.selling_price),
                    'total_qty': stats['total_qty'],
                    'total_revenue': revenue,
                    'total_cost': cost,
                    'total_profit': profit,
                    'margin_percent': round(margin, 2),
                    'order_count': len(order_products[pid]),
                })
            
            # Sort
            if sort_by == 'total_qty':
                result.sort(key=lambda x: x['total_qty'], reverse=True)
            elif sort_by == 'total_profit':
                result.sort(key=lambda x: x['total_profit'], reverse=True)
            elif sort_by == 'margin_percent':
                result.sort(key=lambda x: x['margin_percent'], reverse=True)
            else:
                result.sort(key=lambda x: x['total_revenue'], reverse=True)
            
            return Response({
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'product_count': len(result),
                'data': result
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnpaidOrdersReportView(APIView):
    """Unpaid and partially paid orders"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            orders = Order.objects.filter(
                payment_status__in=['pending', 'partial']
            ).exclude(status='cancelled').select_related('customer').prefetch_related('items', 'payments')
            
            result = []
            total_outstanding = Decimal('0')
            
            for order in orders:
                order_revenue = sum(item.line_total for item in order.items.all())
                paid = order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
                outstanding = order_revenue - paid
                total_outstanding += outstanding
                
                result.append({
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'order_date': order.order_date.isoformat(),
                    'customer_name': order.customer.name,
                    'customer_mobile': order.customer.mobile,
                    'apartment': order.customer.apartment_name,
                    'order_total': safe_float(order_revenue),
                    'amount_paid': safe_float(paid),
                    'outstanding': safe_float(outstanding),
                    'payment_status': order.payment_status,
                    'days_old': (date.today() - order.order_date).days,
                })
            
            # Sort by outstanding amount
            result.sort(key=lambda x: x['outstanding'], reverse=True)
            
            return Response({
                'total_orders': len(result),
                'total_outstanding': safe_float(total_outstanding),
                'data': result
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InactiveCustomersReportView(APIView):
    """Customers who haven't ordered recently"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            days = int(request.query_params.get('days', 30))
            
            # Get all active customers
            customers = Customer.objects.filter(is_active=True)
            
            # Get last order and total spent for each customer from items
            customer_stats = OrderItem.objects.filter(
                order__customer__is_active=True
            ).exclude(order__status='cancelled').values('order__customer_id').annotate(
                last_order_date=Max('order__order_date'),
                total_spent=Sum(F('quantity') * F('unit_price'))
            )
            
            stats_map = {s['order__customer_id']: s for s in customer_stats}
            
            result = []
            for customer in customers:
                stats = stats_map.get(customer.id)
                
                if stats:
                    last_order_date = stats['last_order_date']
                    days_since = (date.today() - last_order_date).days if last_order_date else None
                    total_spent = safe_float(stats['total_spent'])
                    
                    if days_since is None or days_since >= days:
                        result.append({
                            'customer_id': customer.id,
                            'customer_name': customer.name,
                            'mobile': customer.mobile,
                            'apartment': customer.apartment_name,
                            'block': customer.block,
                            'last_order_date': last_order_date.isoformat() if last_order_date else None,
                            'days_since_order': days_since,
                            'total_spent': total_spent,
                        })
                else:
                    # Never ordered
                    result.append({
                        'customer_id': customer.id,
                        'customer_name': customer.name,
                        'mobile': customer.mobile,
                        'apartment': customer.apartment_name,
                        'block': customer.block,
                        'last_order_date': None,
                        'days_since_order': None,
                        'total_spent': 0,
                    })
            
            # Sort by days since order (None = never ordered, sort last)
            result.sort(key=lambda x: x['days_since_order'] if x['days_since_order'] is not None else 9999, reverse=True)
            
            return Response({
                'inactive_days_threshold': days,
                'inactive_count': len(result),
                'data': result
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderProfitabilityReportView(APIView):
    """Order-level profitability report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # Default to last 30 days
            if not end_date:
                end_date = date.today()
            else:
                end_date = date.fromisoformat(end_date)
            
            if not start_date:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = date.fromisoformat(start_date)
            
            orders = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date
            ).exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            result = []
            total_revenue = Decimal('0')
            total_profit = Decimal('0')
            
            for order in orders:
                # Calculate from items
                revenue = sum(item.line_total for item in order.items.all())
                cost = sum(item.line_cost for item in order.items.all())
                profit = revenue - cost
                margin = (float(profit) / float(revenue) * 100) if revenue else 0
                
                total_revenue += revenue
                total_profit += profit
                
                result.append({
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'order_date': order.order_date.isoformat(),
                    'customer_name': order.customer.name,
                    'item_count': order.items.count(),
                    'total_revenue': safe_float(revenue),
                    'total_cost': safe_float(cost),
                    'total_profit': safe_float(profit),
                    'margin_percent': round(margin, 2),
                })
            
            # Sort by profit descending
            result.sort(key=lambda x: x['total_profit'], reverse=True)
            
            # Summary
            avg_margin = (float(total_profit) / float(total_revenue) * 100) if total_revenue else 0
            
            return Response({
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'summary': {
                    'total_orders': len(result),
                    'total_revenue': safe_float(total_revenue),
                    'total_profit': safe_float(total_profit),
                    'avg_margin': round(avg_margin, 2),
                },
                'data': result
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CSV Export Views
class ExportSalesCSV(APIView):
    """Export sales report as CSV"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = date.fromisoformat(start_date)
        
        orders = Order.objects.filter(
            order_date__gte=start_date,
            order_date__lte=end_date
        ).exclude(status='cancelled').select_related('customer').prefetch_related('items')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Date', 'Customer', 'Mobile', 'Apartment',
            'Items', 'Revenue', 'Cost', 'Profit', 'Margin %', 'Payment Status'
        ])
        
        for order in orders:
            revenue = sum(item.line_total for item in order.items.all())
            cost = sum(item.line_cost for item in order.items.all())
            profit = revenue - cost
            margin = (float(profit) / float(revenue) * 100) if revenue else 0
            writer.writerow([
                order.order_number,
                order.order_date.isoformat(),
                order.customer.name,
                order.customer.mobile,
                order.customer.apartment_name or '',
                order.items.count(),
                safe_float(revenue),
                safe_float(cost),
                safe_float(profit),
                round(margin, 2),
                order.payment_status,
            ])
        
        return response


class ExportCustomerCSV(APIView):
    """Export customer report as CSV"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)
        
        if not start_date:
            start_date = end_date - timedelta(days=90)
        else:
            start_date = date.fromisoformat(start_date)
        
        customer_data = OrderItem.objects.filter(
            order__order_date__gte=start_date,
            order__order_date__lte=end_date
        ).exclude(order__status='cancelled').values(
            'order__customer__name', 'order__customer__mobile', 'order__customer__apartment_name'
        ).annotate(
            order_count=Count('order', distinct=True),
            total_spent=Sum(
                F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
                output_field=models.DecimalField()
            ),
            total_profit=Sum(
                F('quantity') * (Coalesce(F('unit_price'), Value(Decimal('0'))) - Coalesce(F('unit_cost_snapshot'), Value(Decimal('0')))),
                output_field=models.DecimalField()
            )
        ).order_by('-total_spent')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customer_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Customer', 'Mobile', 'Apartment', 'Orders', 'Total Spent',
            'Total Profit', 'Avg Order Value'
        ])
        
        for c in customer_data:
            spent = safe_float(c['total_spent'])
            order_count = c['order_count'] or 0
            avg = spent / order_count if order_count else 0
            writer.writerow([
                c['order__customer__name'],
                c['order__customer__mobile'],
                c['order__customer__apartment_name'] or '',
                order_count,
                spent,
                safe_float(c['total_profit']),
                round(avg, 2),
            ])
        
        return response


class ExportProductCSV(APIView):
    """Export product report as CSV"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)
        
        if not start_date:
            start_date = end_date - timedelta(days=90)
        else:
            start_date = date.fromisoformat(start_date)
        
        product_data = OrderItem.objects.filter(
            order__order_date__gte=start_date,
            order__order_date__lte=end_date
        ).exclude(order__status='cancelled').values(
            'product__name', 'product__category', 'product__unit'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(
                F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
                output_field=models.DecimalField()
            ),
            total_cost=Sum(
                F('quantity') * Coalesce(F('unit_cost_snapshot'), Value(Decimal('0'))),
                output_field=models.DecimalField()
            )
        ).order_by('-total_revenue')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="product_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Product', 'Category', 'Unit Size', 'Qty Sold', 'Revenue',
            'Cost', 'Profit', 'Margin %'
        ])
        
        for p in product_data:
            revenue = safe_float(p['total_revenue'])
            cost = safe_float(p['total_cost'])
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue else 0
            
            writer.writerow([
                p['product__name'],
                p['product__category'],
                p['product__unit'] or '',
                p['total_qty'],
                revenue,
                cost,
                profit,
                round(margin, 2),
            ])
        
        return response


class ExportUnpaidCSV(APIView):
    """Export unpaid orders as CSV"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        orders = Order.objects.filter(
            payment_status__in=['pending', 'partial']
        ).exclude(status='cancelled').select_related('customer').prefetch_related('items', 'payments')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="unpaid_orders_{date.today()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Date', 'Customer', 'Mobile', 'Apartment',
            'Order Total', 'Amount Paid', 'Outstanding', 'Days Old'
        ])
        
        for order in orders:
            order_revenue = sum(item.line_total for item in order.items.all())
            paid = order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            outstanding = order_revenue - paid
            days_old = (date.today() - order.order_date).days
            
            writer.writerow([
                order.order_number,
                order.order_date.isoformat(),
                order.customer.name,
                order.customer.mobile,
                order.customer.apartment_name or '',
                safe_float(order_revenue),
                safe_float(paid),
                safe_float(outstanding),
                days_old,
            ])
        
        return response


# ============================================================
# CUSTOMER LOYALTY ANALYTICS (Step 9)
# ============================================================

def calculate_customer_metrics(customer, orders):
    """
    Calculate loyalty metrics for a single customer.
    
    Returns dict with:
    - total_orders, total_revenue, avg_order_value
    - first_order_date, last_order_date
    - repeat_customer_flag, order_frequency
    - avg_days_between_orders, recency_days
    - loyalty_segment, recency_status
    """
    today = date.today()
    
    if not orders:
        return {
            'customer_id': customer.id,
            'customer_name': customer.name,
            'mobile': customer.mobile,
            'apartment': customer.apartment_name,
            'block': customer.block,
            'total_orders': 0,
            'total_revenue': 0.0,
            'total_profit': 0.0,
            'avg_order_value': 0.0,
            'first_order_date': None,
            'last_order_date': None,
            'repeat_customer_flag': False,
            'order_frequency': 'never',
            'avg_days_between_orders': None,
            'recency_days': None,
            'loyalty_segment': 'prospect',
            'recency_status': 'never_ordered',
        }
    
    # Sort orders by date
    sorted_orders = sorted(orders, key=lambda o: o.order_date)
    
    # Calculate revenue and profit
    total_revenue = Decimal('0')
    total_profit = Decimal('0')
    for order in orders:
        for item in order.items.all():
            price = item.unit_price or Decimal('0')
            cost = item.unit_cost_snapshot or Decimal('0')
            qty = item.quantity or 0
            total_revenue += qty * price
            total_profit += qty * (price - cost)
    
    total_orders = len(orders)
    first_order_date = sorted_orders[0].order_date
    last_order_date = sorted_orders[-1].order_date
    avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
    
    # Recency
    recency_days = (today - last_order_date).days
    
    # Average days between orders
    avg_days_between = None
    if total_orders > 1:
        total_days = (last_order_date - first_order_date).days
        avg_days_between = total_days / (total_orders - 1) if total_orders > 1 else None
    
    # Repeat customer flag
    repeat_customer_flag = total_orders >= 2
    
    # Loyalty segment: new (1 order), repeat (2-4), loyal (5+)
    if total_orders == 1:
        loyalty_segment = 'new'
    elif total_orders <= 4:
        loyalty_segment = 'repeat'
    else:
        loyalty_segment = 'loyal'
    
    # Recency status: active (<30 days), at-risk (31-90), inactive (>90)
    if recency_days <= 30:
        recency_status = 'active'
    elif recency_days <= 90:
        recency_status = 'at_risk'
    else:
        recency_status = 'inactive'
    
    # Order frequency description
    if avg_days_between is None:
        order_frequency = 'single_order'
    elif avg_days_between <= 7:
        order_frequency = 'weekly'
    elif avg_days_between <= 14:
        order_frequency = 'biweekly'
    elif avg_days_between <= 30:
        order_frequency = 'monthly'
    elif avg_days_between <= 60:
        order_frequency = 'occasional'
    else:
        order_frequency = 'rare'
    
    return {
        'customer_id': customer.id,
        'customer_name': customer.name,
        'mobile': customer.mobile,
        'apartment': customer.apartment_name,
        'block': customer.block,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'total_profit': float(total_profit),
        'avg_order_value': round(avg_order_value, 2),
        'first_order_date': first_order_date.isoformat(),
        'last_order_date': last_order_date.isoformat(),
        'repeat_customer_flag': repeat_customer_flag,
        'order_frequency': order_frequency,
        'avg_days_between_orders': round(avg_days_between, 1) if avg_days_between else None,
        'recency_days': recency_days,
        'loyalty_segment': loyalty_segment,
        'recency_status': recency_status,
    }


class CustomerLoyaltyDashboardView(APIView):
    """Customer Loyalty Analytics Dashboard with summary metrics"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            # Get all customers with their orders
            customers = Customer.objects.filter(is_active=True)
            orders = Order.objects.exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            # Group orders by customer
            customer_orders = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_orders:
                    customer_orders[cid] = []
                customer_orders[cid].append(order)
            
            # Calculate metrics for all customers
            all_metrics = []
            for customer in customers:
                cust_orders = customer_orders.get(customer.id, [])
                metrics = calculate_customer_metrics(customer, cust_orders)
                all_metrics.append(metrics)
            
            # Summary stats
            total_customers = len(all_metrics)
            customers_with_orders = len([m for m in all_metrics if m['total_orders'] > 0])
            
            # Loyalty segment counts
            segment_counts = {
                'prospect': 0,
                'new': 0,
                'repeat': 0,
                'loyal': 0
            }
            for m in all_metrics:
                segment_counts[m['loyalty_segment']] += 1
            
            # Recency status counts (only for customers with orders)
            recency_counts = {
                'active': 0,
                'at_risk': 0,
                'inactive': 0,
                'never_ordered': 0
            }
            for m in all_metrics:
                recency_counts[m['recency_status']] += 1
            
            # Top metrics
            customers_with_metrics = [m for m in all_metrics if m['total_orders'] > 0]
            
            if customers_with_metrics:
                total_revenue = sum(m['total_revenue'] for m in customers_with_metrics)
                avg_ltv = total_revenue / len(customers_with_metrics) if customers_with_metrics else 0
                repeat_rate = len([m for m in customers_with_metrics if m['repeat_customer_flag']]) / len(customers_with_metrics) * 100
                avg_orders = sum(m['total_orders'] for m in customers_with_metrics) / len(customers_with_metrics)
            else:
                total_revenue = 0
                avg_ltv = 0
                repeat_rate = 0
                avg_orders = 0
            
            # Top 10 by revenue (LTV)
            top_by_revenue = sorted(customers_with_metrics, key=lambda x: x['total_revenue'], reverse=True)[:10]
            
            # Top 10 by order count
            top_by_orders = sorted(customers_with_metrics, key=lambda x: x['total_orders'], reverse=True)[:10]
            
            # At-risk customers (need attention)
            at_risk_customers = [m for m in all_metrics if m['recency_status'] == 'at_risk']
            at_risk_customers.sort(key=lambda x: x['total_revenue'], reverse=True)
            
            return Response({
                'summary': {
                    'total_customers': total_customers,
                    'customers_with_orders': customers_with_orders,
                    'total_revenue': round(total_revenue, 2),
                    'avg_lifetime_value': round(avg_ltv, 2),
                    'repeat_rate_percent': round(repeat_rate, 1),
                    'avg_orders_per_customer': round(avg_orders, 1),
                },
                'segment_counts': segment_counts,
                'recency_counts': recency_counts,
                'top_by_revenue': top_by_revenue[:10],
                'top_by_orders': top_by_orders[:10],
                'at_risk_customers': at_risk_customers[:10],
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerLoyaltyListView(APIView):
    """Full customer loyalty list with all metrics"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            # Filters
            loyalty_segment = request.query_params.get('loyalty_segment')
            recency_status = request.query_params.get('recency_status')
            sort_by = request.query_params.get('sort_by', 'total_revenue')
            
            # Get all customers with their orders
            customers = Customer.objects.filter(is_active=True)
            orders = Order.objects.exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            # Group orders by customer
            customer_orders = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_orders:
                    customer_orders[cid] = []
                customer_orders[cid].append(order)
            
            # Calculate metrics for all customers
            all_metrics = []
            for customer in customers:
                cust_orders = customer_orders.get(customer.id, [])
                metrics = calculate_customer_metrics(customer, cust_orders)
                all_metrics.append(metrics)
            
            # Filter
            if loyalty_segment:
                all_metrics = [m for m in all_metrics if m['loyalty_segment'] == loyalty_segment]
            if recency_status:
                all_metrics = [m for m in all_metrics if m['recency_status'] == recency_status]
            
            # Sort
            if sort_by == 'total_orders':
                all_metrics.sort(key=lambda x: x['total_orders'], reverse=True)
            elif sort_by == 'avg_order_value':
                all_metrics.sort(key=lambda x: x['avg_order_value'], reverse=True)
            elif sort_by == 'recency_days':
                all_metrics.sort(key=lambda x: x['recency_days'] if x['recency_days'] is not None else 9999)
            elif sort_by == 'last_order_date':
                all_metrics.sort(key=lambda x: x['last_order_date'] or '0000-00-00', reverse=True)
            else:  # total_revenue (default)
                all_metrics.sort(key=lambda x: x['total_revenue'], reverse=True)
            
            return Response({
                'count': len(all_metrics),
                'data': all_metrics
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RepeatCustomersReportView(APIView):
    """Report on repeat vs one-time customers"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            customers = Customer.objects.filter(is_active=True)
            orders = Order.objects.exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            customer_orders = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_orders:
                    customer_orders[cid] = []
                customer_orders[cid].append(order)
            
            # Calculate metrics
            one_time = []
            repeat = []
            
            for customer in customers:
                cust_orders = customer_orders.get(customer.id, [])
                if not cust_orders:
                    continue
                    
                metrics = calculate_customer_metrics(customer, cust_orders)
                if metrics['total_orders'] == 1:
                    one_time.append(metrics)
                else:
                    repeat.append(metrics)
            
            # Summary
            total_with_orders = len(one_time) + len(repeat)
            one_time_revenue = sum(m['total_revenue'] for m in one_time)
            repeat_revenue = sum(m['total_revenue'] for m in repeat)
            
            return Response({
                'summary': {
                    'total_customers': total_with_orders,
                    'one_time_count': len(one_time),
                    'repeat_count': len(repeat),
                    'repeat_rate_percent': round(len(repeat) / total_with_orders * 100, 1) if total_with_orders else 0,
                    'one_time_revenue': round(one_time_revenue, 2),
                    'repeat_revenue': round(repeat_revenue, 2),
                    'repeat_revenue_percent': round(repeat_revenue / (one_time_revenue + repeat_revenue) * 100, 1) if (one_time_revenue + repeat_revenue) else 0,
                },
                'one_time_customers': sorted(one_time, key=lambda x: x['total_revenue'], reverse=True)[:20],
                'repeat_customers': sorted(repeat, key=lambda x: x['total_orders'], reverse=True)[:20],
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FrequencyReportView(APIView):
    """Customer purchase frequency report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            customers = Customer.objects.filter(is_active=True)
            orders = Order.objects.exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            customer_orders = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_orders:
                    customer_orders[cid] = []
                customer_orders[cid].append(order)
            
            # Group by frequency
            frequency_groups = {
                'weekly': [],
                'biweekly': [],
                'monthly': [],
                'occasional': [],
                'rare': [],
                'single_order': []
            }
            
            for customer in customers:
                cust_orders = customer_orders.get(customer.id, [])
                if not cust_orders:
                    continue
                    
                metrics = calculate_customer_metrics(customer, cust_orders)
                freq = metrics['order_frequency']
                if freq in frequency_groups:
                    frequency_groups[freq].append(metrics)
            
            # Summary for each frequency
            frequency_summary = {}
            for freq, customers_list in frequency_groups.items():
                if customers_list:
                    frequency_summary[freq] = {
                        'count': len(customers_list),
                        'total_revenue': round(sum(m['total_revenue'] for m in customers_list), 2),
                        'avg_revenue': round(sum(m['total_revenue'] for m in customers_list) / len(customers_list), 2),
                        'avg_orders': round(sum(m['total_orders'] for m in customers_list) / len(customers_list), 1),
                    }
                else:
                    frequency_summary[freq] = {
                        'count': 0,
                        'total_revenue': 0,
                        'avg_revenue': 0,
                        'avg_orders': 0,
                    }
            
            return Response({
                'frequency_summary': frequency_summary,
                'weekly_customers': sorted(frequency_groups['weekly'], key=lambda x: x['total_revenue'], reverse=True)[:10],
                'biweekly_customers': sorted(frequency_groups['biweekly'], key=lambda x: x['total_revenue'], reverse=True)[:10],
                'monthly_customers': sorted(frequency_groups['monthly'], key=lambda x: x['total_revenue'], reverse=True)[:10],
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecencyReportView(APIView):
    """Customer recency analysis report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            customers = Customer.objects.filter(is_active=True)
            orders = Order.objects.exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            customer_orders = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_orders:
                    customer_orders[cid] = []
                customer_orders[cid].append(order)
            
            # Group by recency
            recency_groups = {
                'active': [],
                'at_risk': [],
                'inactive': []
            }
            
            for customer in customers:
                cust_orders = customer_orders.get(customer.id, [])
                if not cust_orders:
                    continue
                    
                metrics = calculate_customer_metrics(customer, cust_orders)
                status = metrics['recency_status']
                if status in recency_groups:
                    recency_groups[status].append(metrics)
            
            # Summary
            recency_summary = {}
            for status, customers_list in recency_groups.items():
                if customers_list:
                    recency_summary[status] = {
                        'count': len(customers_list),
                        'total_revenue': round(sum(m['total_revenue'] for m in customers_list), 2),
                        'avg_revenue': round(sum(m['total_revenue'] for m in customers_list) / len(customers_list), 2),
                        'avg_recency_days': round(sum(m['recency_days'] for m in customers_list) / len(customers_list), 1),
                    }
                else:
                    recency_summary[status] = {
                        'count': 0,
                        'total_revenue': 0,
                        'avg_revenue': 0,
                        'avg_recency_days': 0,
                    }
            
            # Engagement insights
            insights = []
            
            # At-risk high-value customers
            at_risk_high_value = [m for m in recency_groups['at_risk'] if m['total_revenue'] > 1000]
            if at_risk_high_value:
                insights.append({
                    'type': 'at_risk_high_value',
                    'title': 'High-Value Customers at Risk',
                    'message': f"{len(at_risk_high_value)} customers with >₹1000 spend haven't ordered in 31-90 days. Consider reaching out!",
                    'customers': sorted(at_risk_high_value, key=lambda x: x['total_revenue'], reverse=True)[:5]
                })
            
            # Inactive loyal customers
            inactive_loyal = [m for m in recency_groups['inactive'] if m['loyalty_segment'] == 'loyal']
            if inactive_loyal:
                insights.append({
                    'type': 'inactive_loyal',
                    'title': 'Loyal Customers Gone Inactive',
                    'message': f"{len(inactive_loyal)} loyal customers (5+ orders) haven't ordered in >90 days. Win them back!",
                    'customers': sorted(inactive_loyal, key=lambda x: x['total_revenue'], reverse=True)[:5]
                })
            
            return Response({
                'recency_summary': recency_summary,
                'insights': insights,
                'active_customers': sorted(recency_groups['active'], key=lambda x: x['total_revenue'], reverse=True)[:15],
                'at_risk_customers': sorted(recency_groups['at_risk'], key=lambda x: x['total_revenue'], reverse=True)[:15],
                'inactive_customers': sorted(recency_groups['inactive'], key=lambda x: x['total_revenue'], reverse=True)[:15],
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LifetimeValueReportView(APIView):
    """Customer Lifetime Value (LTV) report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            customers = Customer.objects.filter(is_active=True)
            orders = Order.objects.exclude(status='cancelled').select_related('customer').prefetch_related('items')
            
            customer_orders = {}
            for order in orders:
                cid = order.customer_id
                if cid not in customer_orders:
                    customer_orders[cid] = []
                customer_orders[cid].append(order)
            
            all_metrics = []
            for customer in customers:
                cust_orders = customer_orders.get(customer.id, [])
                if cust_orders:
                    metrics = calculate_customer_metrics(customer, cust_orders)
                    all_metrics.append(metrics)
            
            if not all_metrics:
                return Response({
                    'summary': {},
                    'ltv_distribution': {},
                    'top_customers': [],
                    'bottom_customers': []
                })
            
            # LTV distribution buckets
            ltv_buckets = {
                '0-500': [],
                '501-1000': [],
                '1001-2500': [],
                '2501-5000': [],
                '5001+': []
            }
            
            for m in all_metrics:
                ltv = m['total_revenue']
                if ltv <= 500:
                    ltv_buckets['0-500'].append(m)
                elif ltv <= 1000:
                    ltv_buckets['501-1000'].append(m)
                elif ltv <= 2500:
                    ltv_buckets['1001-2500'].append(m)
                elif ltv <= 5000:
                    ltv_buckets['2501-5000'].append(m)
                else:
                    ltv_buckets['5001+'].append(m)
            
            ltv_distribution = {}
            for bucket, customers_list in ltv_buckets.items():
                ltv_distribution[bucket] = {
                    'count': len(customers_list),
                    'total_revenue': round(sum(m['total_revenue'] for m in customers_list), 2),
                }
            
            # Summary
            total_ltv = sum(m['total_revenue'] for m in all_metrics)
            avg_ltv = total_ltv / len(all_metrics)
            
            sorted_by_ltv = sorted(all_metrics, key=lambda x: x['total_revenue'], reverse=True)
            
            # Top 20% contribute what % of revenue
            top_20_count = max(1, len(all_metrics) // 5)
            top_20_revenue = sum(m['total_revenue'] for m in sorted_by_ltv[:top_20_count])
            top_20_percent = (top_20_revenue / total_ltv * 100) if total_ltv else 0
            
            return Response({
                'summary': {
                    'total_customers': len(all_metrics),
                    'total_ltv': round(total_ltv, 2),
                    'avg_ltv': round(avg_ltv, 2),
                    'median_ltv': round(sorted_by_ltv[len(sorted_by_ltv) // 2]['total_revenue'], 2),
                    'max_ltv': round(sorted_by_ltv[0]['total_revenue'], 2),
                    'top_20_revenue_percent': round(top_20_percent, 1),
                },
                'ltv_distribution': ltv_distribution,
                'top_customers': sorted_by_ltv[:20],
                'bottom_customers': sorted_by_ltv[-10:] if len(sorted_by_ltv) > 10 else sorted_by_ltv,
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CohortRetentionReportView(APIView):
    """Simple cohort retention by first order month"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        try:
            orders = Order.objects.exclude(status='cancelled').select_related('customer').order_by('order_date')
            
            # Find first order date for each customer
            customer_first_order = {}
            customer_orders_by_month = {}
            
            for order in orders:
                cid = order.customer_id
                order_month = order.order_date.replace(day=1)
                
                if cid not in customer_first_order:
                    customer_first_order[cid] = order_month
                    customer_orders_by_month[cid] = set()
                
                customer_orders_by_month[cid].add(order_month)
            
            # Group customers by cohort (first order month)
            cohorts = {}
            for cid, first_month in customer_first_order.items():
                cohort_key = first_month.isoformat()[:7]  # YYYY-MM
                if cohort_key not in cohorts:
                    cohorts[cohort_key] = {
                        'customers': [],
                        'months_active': {}
                    }
                cohorts[cohort_key]['customers'].append(cid)
            
            # Calculate retention for each cohort
            cohort_data = []
            today = date.today()
            
            for cohort_key in sorted(cohorts.keys(), reverse=True)[:6]:  # Last 6 cohorts
                cohort = cohorts[cohort_key]
                cohort_size = len(cohort['customers'])
                
                retention = {'cohort': cohort_key, 'size': cohort_size, 'months': {}}
                
                # Calculate retention for months 0, 1, 2, 3
                cohort_month = date.fromisoformat(cohort_key + '-01')
                
                for month_offset in range(4):
                    target_month = (cohort_month.replace(day=1) + timedelta(days=32 * month_offset)).replace(day=1)
                    
                    if target_month > today:
                        break
                    
                    active_count = 0
                    for cid in cohort['customers']:
                        if target_month in customer_orders_by_month.get(cid, set()):
                            active_count += 1
                    
                    retention_rate = (active_count / cohort_size * 100) if cohort_size else 0
                    retention['months'][f'M{month_offset}'] = {
                        'active': active_count,
                        'retention_percent': round(retention_rate, 1)
                    }
                
                cohort_data.append(retention)
            
            return Response({
                'cohorts': cohort_data,
                'total_cohorts': len(cohorts),
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
