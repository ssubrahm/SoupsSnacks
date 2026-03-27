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
            
            # Get orders in range
            orders = Order.objects.filter(
                order_date__gte=start_date,
                order_date__lte=end_date
            ).exclude(status='cancelled')
            
            # Summary - aggregate from items
            total_orders = orders.count()
            revenue, cost, profit = get_order_totals(orders)
            avg_order = revenue / total_orders if total_orders > 0 else 0
            
            # Group by date - using order items
            items = OrderItem.objects.filter(
                order__order_date__gte=start_date,
                order__order_date__lte=end_date
            ).exclude(order__status='cancelled')
            
            if group_by == 'month':
                daily_data = items.annotate(
                    period=TruncMonth('order__order_date')
                ).values('period').annotate(
                    orders=Count('order', distinct=True),
                    revenue=Sum(
                        F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
                        output_field=models.DecimalField()
                    ),
                    profit=Sum(
                        F('quantity') * (Coalesce(F('unit_price'), Value(Decimal('0'))) - Coalesce(F('unit_cost_snapshot'), Value(Decimal('0')))),
                        output_field=models.DecimalField()
                    )
                ).order_by('period')
            else:
                daily_data = items.annotate(
                    period=TruncDate('order__order_date')
                ).values('period').annotate(
                    orders=Count('order', distinct=True),
                    revenue=Sum(
                        F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
                        output_field=models.DecimalField()
                    ),
                    profit=Sum(
                        F('quantity') * (Coalesce(F('unit_price'), Value(Decimal('0'))) - Coalesce(F('unit_cost_snapshot'), Value(Decimal('0')))),
                        output_field=models.DecimalField()
                    )
                ).order_by('period')
            
            data = []
            for d in daily_data:
                data.append({
                    'period': d['period'].isoformat() if d['period'] else None,
                    'orders': d['orders'] or 0,
                    'revenue': safe_float(d['revenue']),
                    'profit': safe_float(d['profit']),
                })
            
            return Response({
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'summary': {
                    'total_orders': total_orders,
                    'total_revenue': revenue,
                    'total_profit': profit,
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
            
            # Get customer stats from order items
            customer_data = OrderItem.objects.filter(
                order__order_date__gte=start_date,
                order__order_date__lte=end_date
            ).exclude(order__status='cancelled').values(
                'order__customer_id'
            ).annotate(
                order_count=Count('order', distinct=True),
                total_spent=Sum(
                    F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
                    output_field=models.DecimalField()
                ),
                total_profit=Sum(
                    F('quantity') * (Coalesce(F('unit_price'), Value(Decimal('0'))) - Coalesce(F('unit_cost_snapshot'), Value(Decimal('0')))),
                    output_field=models.DecimalField()
                ),
                last_order=Max('order__order_date')
            )
            
            # Sort
            if sort_by == 'order_count':
                customer_data = customer_data.order_by('-order_count')
            else:
                customer_data = customer_data.order_by('-total_spent')
            
            # Get customer details
            customer_ids = [c['order__customer_id'] for c in customer_data]
            customers = {c.id: c for c in Customer.objects.filter(id__in=customer_ids)}
            
            # Calculate total for percentage
            total_revenue = sum(safe_float(c['total_spent']) for c in customer_data)
            
            result = []
            for c in customer_data:
                customer = customers.get(c['order__customer_id'])
                if customer:
                    spent = safe_float(c['total_spent'])
                    order_count = c['order_count'] or 0
                    avg_order = spent / order_count if order_count > 0 else 0
                    pct = (spent / total_revenue * 100) if total_revenue else 0
                    result.append({
                        'customer_id': c['order__customer_id'],
                        'customer_name': customer.name,
                        'mobile': customer.mobile,
                        'apartment': customer.apartment_name,
                        'block': customer.block,
                        'order_count': order_count,
                        'total_spent': spent,
                        'total_profit': safe_float(c['total_profit']),
                        'avg_order_value': round(avg_order, 2),
                        'last_order': c['last_order'].isoformat() if c['last_order'] else None,
                        'percentage_share': round(pct, 2),
                    })
            
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
            
            # Filter order items
            items = OrderItem.objects.filter(
                order__order_date__gte=start_date,
                order__order_date__lte=end_date
            ).exclude(order__status='cancelled')
            
            if category:
                items = items.filter(product__category=category)
            
            # Aggregate by product
            product_data = items.values(
                'product_id'
            ).annotate(
                total_qty=Sum('quantity'),
                total_revenue=Sum(
                    F('quantity') * Coalesce(F('unit_price'), Value(Decimal('0'))),
                    output_field=models.DecimalField()
                ),
                total_cost=Sum(
                    F('quantity') * Coalesce(F('unit_cost_snapshot'), Value(Decimal('0'))),
                    output_field=models.DecimalField()
                ),
                order_count=Count('order', distinct=True)
            )
            
            # Get product details
            product_ids = [p['product_id'] for p in product_data]
            products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
            
            # Calculate profit and build result
            result = []
            for p in product_data:
                product = products.get(p['product_id'])
                if product:
                    revenue = safe_float(p['total_revenue'])
                    cost = safe_float(p['total_cost'])
                    profit = revenue - cost
                    margin = (profit / revenue * 100) if revenue else 0
                    
                    result.append({
                        'product_id': p['product_id'],
                        'product_name': product.name,
                        'category': product.category,
                        'unit_size': product.unit,  # Fixed: use 'unit' not 'unit_size'
                        'selling_price': safe_float(product.selling_price),
                        'total_qty': p['total_qty'] or 0,
                        'total_revenue': revenue,
                        'total_cost': cost,
                        'total_profit': profit,
                        'margin_percent': round(margin, 2),
                        'order_count': p['order_count'] or 0,
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
