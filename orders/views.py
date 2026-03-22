from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
import csv
import io
from accounts.permissions import IsOperator
from customers.models import Customer
from catalog.models import Product
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderCreateUpdateSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order management - Accessible by Admin and Operator
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OrderCreateUpdateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        queryset = Order.objects.select_related('customer').prefetch_related('items__product')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by order type
        order_type = self.request.query_params.get('order_type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        # Filter by fulfillment date
        fulfillment_date = self.request.query_params.get('fulfillment_date')
        if fulfillment_date:
            queryset = queryset.filter(fulfillment_date=fulfillment_date)
        
        # Search by order number or customer name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__mobile__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        by_status = {}
        for status_choice in Order.STATUS_CHOICES:
            status_code = status_choice[0]
            by_status[status_code] = queryset.filter(status=status_code).count()
        
        by_payment = {}
        for payment_choice in Order.PAYMENT_STATUS_CHOICES:
            payment_code = payment_choice[0]
            by_payment[payment_code] = queryset.filter(payment_status=payment_code).count()
        
        # Revenue stats
        total_revenue = sum(order.total_revenue for order in queryset)
        total_profit = sum(order.total_profit for order in queryset)
        
        return Response({
            'total': total,
            'by_status': by_status,
            'by_payment': by_payment,
            'total_revenue': float(total_revenue),
            'total_profit': float(total_profit),
        })
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_payment_status(self, request, pk=None):
        """Change payment status"""
        order = self.get_object()
        new_status = request.data.get('payment_status')
        
        if new_status not in dict(Order.PAYMENT_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid payment status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.payment_status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's orders"""
        today = datetime.now().date()
        queryset = self.get_queryset().filter(
            Q(order_date=today) | Q(fulfillment_date=today)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders (not completed or cancelled)"""
        queryset = self.get_queryset().exclude(
            status__in=['completed', 'cancelled']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_csv(self, request):
        """
        Import orders from CSV file (Google Sheets export)
        
        Expected CSV format:
        customer_name, customer_mobile, order_date, fulfillment_date, product_name, 
        quantity, unit_price, order_type, delivery_address, notes
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be CSV format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            orders_created = 0
            orders_updated = 0
            errors = []
            current_order = None
            current_order_key = None
            
            for row_num, row in enumerate(csv_data, start=2):
                try:
                    # Extract data with flexible field names
                    customer_name = row.get('customer_name', '').strip()
                    customer_mobile = row.get('customer_mobile', '').strip()
                    order_date = row.get('order_date', '').strip()
                    fulfillment_date = row.get('fulfillment_date', '').strip()
                    product_name = row.get('product_name', '').strip()
                    quantity = row.get('quantity', '').strip()
                    unit_price = row.get('unit_price', '').strip()
                    order_type = row.get('order_type', 'delivery').strip() or 'delivery'
                    delivery_address = row.get('delivery_address', '').strip()
                    notes = row.get('notes', '').strip()
                    
                    # Skip empty rows
                    if not customer_name and not product_name:
                        continue
                    
                    # Create order key to group items
                    order_key = f"{customer_mobile}_{order_date}"
                    
                    # Create or get order
                    if order_key != current_order_key or current_order is None:
                        # Find customer
                        customer = Customer.objects.filter(
                            Q(mobile=customer_mobile) | Q(name__iexact=customer_name)
                        ).first()
                        
                        if not customer:
                            errors.append(f"Row {row_num}: Customer '{customer_name}' not found. Skipping.")
                            continue
                        
                        # Parse order date
                        try:
                            order_date_parsed = datetime.strptime(order_date, '%Y-%m-%d').date()
                        except:
                            try:
                                order_date_parsed = datetime.strptime(order_date, '%d/%m/%Y').date()
                            except:
                                order_date_parsed = datetime.now().date()
                        
                        # Parse fulfillment date
                        fulfillment_date_parsed = None
                        if fulfillment_date:
                            try:
                                fulfillment_date_parsed = datetime.strptime(fulfillment_date, '%Y-%m-%d').date()
                            except:
                                try:
                                    fulfillment_date_parsed = datetime.strptime(fulfillment_date, '%d/%m/%Y').date()
                                except:
                                    pass
                        
                        # Create order
                        current_order = Order.objects.create(
                            customer=customer,
                            order_date=order_date_parsed,
                            fulfillment_date=fulfillment_date_parsed,
                            order_type=order_type.lower(),
                            delivery_address=delivery_address,
                            notes=notes,
                            status='draft',
                            payment_status='pending'
                        )
                        current_order_key = order_key
                        orders_created += 1
                    
                    # Add item to order
                    if product_name and quantity:
                        # Find product
                        product = Product.objects.filter(name__iexact=product_name).first()
                        
                        if not product:
                            errors.append(f"Row {row_num}: Product '{product_name}' not found. Skipping item.")
                            continue
                        
                        # Parse quantity and price
                        try:
                            qty = int(quantity)
                        except:
                            errors.append(f"Row {row_num}: Invalid quantity '{quantity}'. Skipping item.")
                            continue
                        
                        # Use provided unit_price or product's selling_price
                        if unit_price:
                            try:
                                price = float(unit_price)
                            except:
                                price = float(product.selling_price)
                        else:
                            price = float(product.selling_price)
                        
                        # Create order item with cost snapshot
                        OrderItem.objects.create(
                            order=current_order,
                            product=product,
                            quantity=qty,
                            unit_price=price,
                            unit_cost_snapshot=product.unit_cost,
                            display_order=current_order.items.count()
                        )
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return Response({
                'success': True,
                'orders_created': orders_created,
                'orders_updated': orders_updated,
                'errors': errors,
                'message': f'Successfully imported {orders_created} orders'
            })
        
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
