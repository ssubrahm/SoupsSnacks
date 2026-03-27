import csv
from decimal import Decimal
from datetime import date, timedelta
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, F, Q, Max
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsOperator
from orders.models import Order, OrderItem
from customers.models import Customer
from catalog.models import Product
from payments.models import Payment


class DashboardView(APIView):
    """Dashboard KPIs and widgets"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        today = date.today()
        first_of_month = today.replace(day=1)
        
        # Orders today
        orders_today = Order.objects.filter(order_date=today).count()
        
        # Pending orders (not delivered/completed/cancelled)
        pending_orders = Order.objects.filter(
            status__in=['draft', 'confirmed', 'preparing', 'ready']
        ).count()
        
        # Sales today
        sales_today = Order.objects.filter(
            order_date=today
        ).exclude(status='cancelled').aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0')
        
        # Sales this month
        sales_month = Order.objects.filter(
            order_date__gte=first_of_month
        ).exclude(status='cancelled').aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0')
        
        # Profit this month
        profit_month = Order.objects.filter(
            order_date__gte=first_of_month
        ).exclude(status='cancelled').aggregate(
            total=Sum('total_profit')
        )['total'] or Decimal('0')
        
        # Unpaid amount
        unpaid_orders = Order.objects.filter(
            payment_status__in=['pending', 'partial']
        ).exclude(status='cancelled')
        
        total_unpaid = Decimal('0')
        for order in unpaid_orders:
            paid = order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_unpaid += order.total_revenue - paid
        
        # Top 5 products this month
        top_products = OrderItem.objects.filter(
            order__order_date__gte=first_of_month
        ).exclude(order__status='cancelled').values(
            'product__name', 'product__id'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total_qty')[:5]
        
        # Top 5 customers this month
        top_customers = Order.objects.filter(
            order_date__gte=first_of_month
        ).exclude(status='cancelled').values(
            'customer__name', 'customer__id'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_revenue')
        ).order_by('-total_spent')[:5]
        
        # Orders by status
        status_counts = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Payment status counts
        payment_counts = Order.objects.exclude(status='cancelled').values(
            'payment_status'
        ).annotate(count=Count('id')).order_by('payment_status')
        
        return Response({
            'orders_today': orders_today,
            'pending_orders': pending_orders,
            'sales_today': float(sales_today),
            'sales_month': float(sales_month),
            'profit_month': float(profit_month),
            'unpaid_amount': float(total_unpaid),
            'top_products': list(top_products),
            'top_customers': list(top_customers),
            'status_counts': list(status_counts),
            'payment_counts': list(payment_counts),
        })


class SalesReportView(APIView):
    """Sales report by date range"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')  # day, month
        
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
        ).exclude(status='cancelled')
        
        # Summary
        summary = orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_revenue'),
            total_profit=Sum('total_profit'),
            avg_order_value=Avg('total_revenue')
        )
        
        # Group by date
        if group_by == 'month':
            daily_data = orders.annotate(
                period=TruncMonth('order_date')
            ).values('period').annotate(
                orders=Count('id'),
                revenue=Sum('total_revenue'),
                profit=Sum('total_profit')
            ).order_by('period')
        else:
            daily_data = orders.annotate(
                period=TruncDate('order_date')
            ).values('period').annotate(
                orders=Count('id'),
                revenue=Sum('total_revenue'),
                profit=Sum('total_profit')
            ).order_by('period')
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_orders': summary['total_orders'] or 0,
                'total_revenue': float(summary['total_revenue'] or 0),
                'total_profit': float(summary['total_profit'] or 0),
                'avg_order_value': float(summary['avg_order_value'] or 0),
            },
            'data': [
                {
                    'period': d['period'].isoformat() if d['period'] else None,
                    'orders': d['orders'],
                    'revenue': float(d['revenue'] or 0),
                    'profit': float(d['profit'] or 0),
                }
                for d in daily_data
            ]
        })


class CustomerReportView(APIView):
    """Customer-wise sales report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        sort_by = request.query_params.get('sort_by', 'total_spent')  # total_spent, order_count, avg_order
        
        # Default to last 90 days
        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)
        
        if not start_date:
            start_date = end_date - timedelta(days=90)
        else:
            start_date = date.fromisoformat(start_date)
        
        # Get customer stats
        customer_data = Order.objects.filter(
            order_date__gte=start_date,
            order_date__lte=end_date
        ).exclude(status='cancelled').values(
            'customer__id', 'customer__name', 'customer__mobile',
            'customer__apartment_name', 'customer__block'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_revenue'),
            total_profit=Sum('total_profit'),
            avg_order_value=Avg('total_revenue'),
            last_order=Max('order_date')
        )
        
        # Sort
        if sort_by == 'order_count':
            customer_data = customer_data.order_by('-order_count')
        elif sort_by == 'avg_order':
            customer_data = customer_data.order_by('-avg_order_value')
        else:
            customer_data = customer_data.order_by('-total_spent')
        
        # Calculate total for percentage
        total_revenue = sum(c['total_spent'] or 0 for c in customer_data)
        
        result = []
        for c in customer_data:
            pct = (float(c['total_spent'] or 0) / float(total_revenue) * 100) if total_revenue else 0
            result.append({
                'customer_id': c['customer__id'],
                'customer_name': c['customer__name'],
                'mobile': c['customer__mobile'],
                'apartment': c['customer__apartment_name'],
                'block': c['customer__block'],
                'order_count': c['order_count'],
                'total_spent': float(c['total_spent'] or 0),
                'total_profit': float(c['total_profit'] or 0),
                'avg_order_value': float(c['avg_order_value'] or 0),
                'last_order': c['last_order'].isoformat() if c['last_order'] else None,
                'percentage_share': round(pct, 2),
            })
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_revenue': float(total_revenue),
            'customer_count': len(result),
            'data': result
        })


class ProductReportView(APIView):
    """Product-wise sales and profitability report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
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
            'product__id', 'product__name', 'product__category',
            'product__unit_size', 'product__selling_price'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price')),
            total_cost=Sum(F('quantity') * F('unit_cost_snapshot')),
            order_count=Count('order', distinct=True)
        )
        
        # Calculate profit and sort
        result = []
        for p in product_data:
            revenue = float(p['total_revenue'] or 0)
            cost = float(p['total_cost'] or 0)
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue else 0
            
            result.append({
                'product_id': p['product__id'],
                'product_name': p['product__name'],
                'category': p['product__category'],
                'unit_size': p['product__unit_size'],
                'selling_price': float(p['product__selling_price'] or 0),
                'total_qty': p['total_qty'],
                'total_revenue': revenue,
                'total_cost': cost,
                'total_profit': profit,
                'margin_percent': round(margin, 2),
                'order_count': p['order_count'],
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


class UnpaidOrdersReportView(APIView):
    """Unpaid and partially paid orders"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        orders = Order.objects.filter(
            payment_status__in=['pending', 'partial']
        ).exclude(status='cancelled').select_related('customer')
        
        result = []
        total_outstanding = Decimal('0')
        
        for order in orders:
            paid = order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            outstanding = order.total_revenue - paid
            total_outstanding += outstanding
            
            result.append({
                'order_id': order.id,
                'order_number': order.order_number,
                'order_date': order.order_date.isoformat(),
                'customer_name': order.customer.name,
                'customer_mobile': order.customer.mobile,
                'apartment': order.customer.apartment_name,
                'order_total': float(order.total_revenue),
                'amount_paid': float(paid),
                'outstanding': float(outstanding),
                'payment_status': order.payment_status,
                'days_old': (date.today() - order.order_date).days,
            })
        
        # Sort by outstanding amount
        result.sort(key=lambda x: x['outstanding'], reverse=True)
        
        return Response({
            'total_orders': len(result),
            'total_outstanding': float(total_outstanding),
            'data': result
        })


class InactiveCustomersReportView(APIView):
    """Customers who haven't ordered recently"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        cutoff_date = date.today() - timedelta(days=days)
        
        # Get all active customers
        customers = Customer.objects.filter(is_active=True)
        
        result = []
        for customer in customers:
            last_order = Order.objects.filter(
                customer=customer
            ).exclude(status='cancelled').order_by('-order_date').first()
            
            if last_order:
                days_since = (date.today() - last_order.order_date).days
                if days_since >= days:
                    # Get total spend
                    total_spent = Order.objects.filter(
                        customer=customer
                    ).exclude(status='cancelled').aggregate(
                        total=Sum('total_revenue')
                    )['total'] or Decimal('0')
                    
                    result.append({
                        'customer_id': customer.id,
                        'customer_name': customer.name,
                        'mobile': customer.mobile,
                        'apartment': customer.apartment_name,
                        'block': customer.block,
                        'last_order_date': last_order.order_date.isoformat(),
                        'days_since_order': days_since,
                        'total_spent': float(total_spent),
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
        
        # Sort by days since order
        result.sort(key=lambda x: x['days_since_order'] or 9999, reverse=True)
        
        return Response({
            'inactive_days_threshold': days,
            'inactive_count': len(result),
            'data': result
        })


class OrderProfitabilityReportView(APIView):
    """Order-level profitability report"""
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
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
        ).exclude(status='cancelled').select_related('customer')
        
        result = []
        for order in orders:
            margin = (float(order.total_profit) / float(order.total_revenue) * 100) if order.total_revenue else 0
            
            result.append({
                'order_id': order.id,
                'order_number': order.order_number,
                'order_date': order.order_date.isoformat(),
                'customer_name': order.customer.name,
                'item_count': order.item_count,
                'total_revenue': float(order.total_revenue),
                'total_cost': float(order.total_revenue - order.total_profit),
                'total_profit': float(order.total_profit),
                'margin_percent': round(margin, 2),
            })
        
        # Sort by profit
        result.sort(key=lambda x: x['total_profit'], reverse=True)
        
        # Summary
        total_revenue = sum(r['total_revenue'] for r in result)
        total_profit = sum(r['total_profit'] for r in result)
        avg_margin = (total_profit / total_revenue * 100) if total_revenue else 0
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_orders': len(result),
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'avg_margin': round(avg_margin, 2),
            },
            'data': result
        })


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
        ).exclude(status='cancelled').select_related('customer')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Date', 'Customer', 'Mobile', 'Apartment',
            'Items', 'Revenue', 'Cost', 'Profit', 'Margin %', 'Payment Status'
        ])
        
        for order in orders:
            margin = (float(order.total_profit) / float(order.total_revenue) * 100) if order.total_revenue else 0
            writer.writerow([
                order.order_number,
                order.order_date.isoformat(),
                order.customer.name,
                order.customer.mobile,
                order.customer.apartment_name or '',
                order.item_count,
                float(order.total_revenue),
                float(order.total_revenue - order.total_profit),
                float(order.total_profit),
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
        
        customer_data = Order.objects.filter(
            order_date__gte=start_date,
            order_date__lte=end_date
        ).exclude(status='cancelled').values(
            'customer__name', 'customer__mobile', 'customer__apartment_name'
        ).annotate(
            order_count=Count('id'),
            total_spent=Sum('total_revenue'),
            total_profit=Sum('total_profit'),
            avg_order_value=Avg('total_revenue')
        ).order_by('-total_spent')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customer_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Customer', 'Mobile', 'Apartment', 'Orders', 'Total Spent',
            'Total Profit', 'Avg Order Value'
        ])
        
        for c in customer_data:
            writer.writerow([
                c['customer__name'],
                c['customer__mobile'],
                c['customer__apartment_name'] or '',
                c['order_count'],
                float(c['total_spent'] or 0),
                float(c['total_profit'] or 0),
                round(float(c['avg_order_value'] or 0), 2),
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
        
        items = OrderItem.objects.filter(
            order__order_date__gte=start_date,
            order__order_date__lte=end_date
        ).exclude(order__status='cancelled')
        
        product_data = items.values(
            'product__name', 'product__category', 'product__unit_size'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price')),
            total_cost=Sum(F('quantity') * F('unit_cost_snapshot'))
        ).order_by('-total_revenue')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="product_report_{start_date}_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Product', 'Category', 'Unit Size', 'Qty Sold', 'Revenue',
            'Cost', 'Profit', 'Margin %'
        ])
        
        for p in product_data:
            revenue = float(p['total_revenue'] or 0)
            cost = float(p['total_cost'] or 0)
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue else 0
            
            writer.writerow([
                p['product__name'],
                p['product__category'],
                p['product__unit_size'] or '',
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
        ).exclude(status='cancelled').select_related('customer')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="unpaid_orders_{date.today()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Date', 'Customer', 'Mobile', 'Apartment',
            'Order Total', 'Amount Paid', 'Outstanding', 'Days Old'
        ])
        
        for order in orders:
            paid = order.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            outstanding = order.total_revenue - paid
            days_old = (date.today() - order.order_date).days
            
            writer.writerow([
                order.order_number,
                order.order_date.isoformat(),
                order.customer.name,
                order.customer.mobile,
                order.customer.apartment_name or '',
                float(order.total_revenue),
                float(paid),
                float(outstanding),
                days_old,
            ])
        
        return response
