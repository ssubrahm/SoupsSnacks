import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from accounts.permissions import IsAdmin
from .models import ImportLog
from .serializers import ImportLogSerializer
from customers.models import Customer
from catalog.models import Product, ProductCostComponent
from orders.models import Order, OrderItem
from payments.models import Payment


def parse_csv_file(file):
    """Parse uploaded CSV file and return rows"""
    try:
        # Try to decode as UTF-8
        content = file.read().decode('utf-8-sig')  # Handle BOM
    except UnicodeDecodeError:
        # Fallback to latin-1
        file.seek(0)
        content = file.read().decode('latin-1')
    
    reader = csv.DictReader(io.StringIO(content))
    headers = reader.fieldnames or []
    rows = list(reader)
    return headers, rows


def parse_excel_file(file):
    """Parse uploaded Excel file and return rows"""
    try:
        import openpyxl
    except ImportError:
        raise ValueError("Excel support requires openpyxl. Install with: pip install openpyxl")
    
    wb = openpyxl.load_workbook(file, data_only=True)
    ws = wb.active
    
    rows_iter = ws.iter_rows(values_only=True)
    headers = [str(h).strip() if h else '' for h in next(rows_iter, [])]
    
    rows = []
    for row in rows_iter:
        if any(cell is not None for cell in row):  # Skip empty rows
            row_dict = {}
            for i, header in enumerate(headers):
                if header and i < len(row):
                    value = row[i]
                    row_dict[header] = str(value).strip() if value is not None else ''
            rows.append(row_dict)
    
    return headers, rows


def validate_required_fields(row, required_fields, row_num):
    """Validate that required fields are present and not empty"""
    errors = []
    for field in required_fields:
        if field not in row or not str(row.get(field, '')).strip():
            errors.append(f"Row {row_num}: Missing required field '{field}'")
    return errors


def parse_decimal(value, field_name, row_num):
    """Parse a decimal value with error handling"""
    if not value or str(value).strip() == '':
        return None, None
    try:
        return Decimal(str(value).strip().replace(',', '')), None
    except (InvalidOperation, ValueError):
        return None, f"Row {row_num}: Invalid number for '{field_name}': {value}"


def parse_date(value, field_name, row_num):
    """Parse a date value with error handling"""
    if not value or str(value).strip() == '':
        return None, None
    
    value = str(value).strip()
    
    # Check if it's an Excel serial date number (e.g., 46108.22928240741)
    try:
        serial = float(value)
        if 1 < serial < 100000:  # Reasonable range for Excel dates
            # Excel epoch is 1899-12-30, add serial days
            from datetime import timedelta
            excel_epoch = datetime(1899, 12, 30)
            parsed_date = (excel_epoch + timedelta(days=serial)).date()
            return parsed_date, None
    except (ValueError, TypeError):
        pass
    
    # Try common date formats (including 2-digit year formats)
    formats = [
        '%Y-%m-%d',    # 2026-03-28
        '%d/%m/%Y',    # 28/03/2026
        '%d/%m/%y',    # 28/03/26 (2-digit year)
        '%m/%d/%Y',    # 03/28/2026
        '%m/%d/%y',    # 03/28/26 (2-digit year)
        '%d-%m-%Y',    # 28-03-2026
        '%d-%m-%y',    # 28-03-26 (2-digit year)
        '%Y/%m/%d',    # 2026/03/28
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date(), None
        except ValueError:
            continue
    
    return None, f"Row {row_num}: Invalid date for '{field_name}': {value}. Use YYYY-MM-DD format."


# =============================================================================
# CUSTOMER IMPORT
# =============================================================================

CUSTOMER_REQUIRED_FIELDS = ['name', 'mobile']
CUSTOMER_OPTIONAL_FIELDS = ['email', 'apartment_name', 'block', 'address', 'notes']


def validate_customer_row(row, row_num, existing_mobiles):
    """Validate a single customer row"""
    errors = validate_required_fields(row, CUSTOMER_REQUIRED_FIELDS, row_num)
    
    mobile = str(row.get('mobile', '')).strip()
    if mobile:
        # Basic mobile validation
        clean_mobile = mobile.replace('+', '').replace(' ', '').replace('-', '')
        if not clean_mobile.isdigit() or len(clean_mobile) < 9 or len(clean_mobile) > 15:
            errors.append(f"Row {row_num}: Invalid mobile number '{mobile}'")
        elif mobile in existing_mobiles:
            errors.append(f"Row {row_num}: Mobile '{mobile}' already exists")
    
    email = row.get('email', '').strip()
    if email and '@' not in email:
        errors.append(f"Row {row_num}: Invalid email '{email}'")
    
    return errors


def import_customer_row(row):
    """Import a single customer row"""
    customer = Customer.objects.create(
        name=row['name'].strip(),
        mobile=row['mobile'].strip(),
        email=row.get('email', '').strip() or None,
        apartment_name=row.get('apartment_name', '').strip() or None,
        block=row.get('block', '').strip() or None,
        address=row.get('address', '').strip() or None,
        notes=row.get('notes', '').strip() or None,
        is_active=True
    )
    return customer.id


# =============================================================================
# PRODUCT IMPORT
# =============================================================================

PRODUCT_REQUIRED_FIELDS = ['name', 'category', 'unit', 'selling_price']
PRODUCT_OPTIONAL_FIELDS = ['description', 'unit_cost', 'is_active']
PRODUCT_CATEGORIES = ['soups', 'snacks', 'sweets', 'lunch', 'dinner', 'pickle', 'combos', 'other']


def validate_product_row(row, row_num, existing_names):
    """Validate a single product row"""
    errors = validate_required_fields(row, PRODUCT_REQUIRED_FIELDS, row_num)
    
    name = row.get('name', '').strip()
    unit = row.get('unit', '').strip()
    name_key = f"{name}|{unit}".lower()
    if name_key in existing_names:
        errors.append(f"Row {row_num}: Product '{name}' with unit '{unit}' already exists")
    
    category = row.get('category', '').strip().lower()
    if category and category not in PRODUCT_CATEGORIES:
        errors.append(f"Row {row_num}: Invalid category '{category}'. Must be one of: {', '.join(PRODUCT_CATEGORIES)}")
    
    selling_price, err = parse_decimal(row.get('selling_price'), 'selling_price', row_num)
    if err:
        errors.append(err)
    elif selling_price is not None and selling_price <= 0:
        errors.append(f"Row {row_num}: Selling price must be greater than 0")
    
    unit_cost = row.get('unit_cost', '').strip()
    if unit_cost:
        cost, err = parse_decimal(unit_cost, 'unit_cost', row_num)
        if err:
            errors.append(err)
    
    return errors


def import_product_row(row):
    """Import a single product row"""
    selling_price, _ = parse_decimal(row['selling_price'], 'selling_price', 0)
    unit_cost, _ = parse_decimal(row.get('unit_cost', '0'), 'unit_cost', 0)
    
    is_active = row.get('is_active', 'true').strip().lower()
    is_active = is_active not in ['false', '0', 'no', 'n']
    
    # Note: unit_cost is a calculated property, not a direct field
    # We create the product first, then add a cost component if unit_cost provided
    product = Product.objects.create(
        name=row['name'].strip(),
        category=row['category'].strip().lower(),
        unit=row['unit'].strip(),
        selling_price=selling_price,
        description=row.get('description', '').strip() or None,
        is_active=is_active
    )
    
    # If unit_cost provided, create a "Base Cost" component
    if unit_cost and unit_cost > 0:
        ProductCostComponent.objects.create(
            product=product,
            item_name='Base Cost (Imported)',
            item_type='ingredient',
            quantity=Decimal('1'),
            unit_of_measure='unit',
            cost_per_unit=unit_cost
            # total_cost is auto-calculated in save()
        )
    
    return product.id


# =============================================================================
# ORDER IMPORT
# =============================================================================

ORDER_REQUIRED_FIELDS = ['customer_mobile', 'order_date', 'product_name', 'quantity', 'unit_price']
ORDER_OPTIONAL_FIELDS = ['order_type', 'delivery_address', 'notes', 'status']


def validate_order_row(row, row_num, customer_map, product_map):
    """Validate a single order row"""
    errors = validate_required_fields(row, ORDER_REQUIRED_FIELDS, row_num)
    
    mobile = str(row.get('customer_mobile', '')).strip()
    if mobile and mobile not in customer_map:
        errors.append(f"Row {row_num}: Customer with mobile '{mobile}' not found")
    
    product_name = row.get('product_name', '').strip()
    if product_name and product_name.lower() not in product_map:
        errors.append(f"Row {row_num}: Product '{product_name}' not found")
    
    order_date, err = parse_date(row.get('order_date'), 'order_date', row_num)
    if err:
        errors.append(err)
    
    quantity, err = parse_decimal(row.get('quantity'), 'quantity', row_num)
    if err:
        errors.append(err)
    elif quantity is not None and quantity <= 0:
        errors.append(f"Row {row_num}: Quantity must be greater than 0")
    
    unit_price, err = parse_decimal(row.get('unit_price'), 'unit_price', row_num)
    if err:
        errors.append(err)
    
    return errors


def import_orders_batch(rows, customer_map, product_map):
    """Import orders - groups rows by customer+date into orders"""
    # Group rows by customer+date
    order_groups = {}
    for row in rows:
        mobile = str(row['customer_mobile']).strip()
        order_date, _ = parse_date(row['order_date'], 'order_date', 0)
        key = f"{mobile}|{order_date}"
        
        if key not in order_groups:
            order_groups[key] = {
                'customer_id': customer_map[mobile],
                'order_date': order_date,
                'order_type': row.get('order_type', 'delivery').strip() or 'delivery',
                'delivery_address': row.get('delivery_address', '').strip() or None,
                'notes': row.get('notes', '').strip() or None,
                'status': row.get('status', 'confirmed').strip() or 'confirmed',
                'items': []
            }
        
        product_name = row['product_name'].strip()
        product = product_map[product_name.lower()]
        quantity, _ = parse_decimal(row['quantity'], 'quantity', 0)
        unit_price, _ = parse_decimal(row['unit_price'], 'unit_price', 0)
        
        order_groups[key]['items'].append({
            'product': product,
            'quantity': int(quantity),
            'unit_price': unit_price,
            'unit_cost_snapshot': product.unit_cost
        })
    
    # Create orders
    created_ids = []
    for group in order_groups.values():
        order = Order.objects.create(
            customer_id=group['customer_id'],
            order_date=group['order_date'],
            order_type=group['order_type'],
            delivery_address=group['delivery_address'],
            notes=group['notes'],
            status=group['status'],
            payment_status='pending'
        )
        
        for i, item in enumerate(group['items']):
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                unit_cost_snapshot=item['unit_cost_snapshot'],
                display_order=i
            )
        
        created_ids.append(order.id)
    
    return created_ids


# =============================================================================
# PAYMENT IMPORT
# =============================================================================

PAYMENT_REQUIRED_FIELDS = ['order_number', 'amount', 'payment_method', 'payment_date']
PAYMENT_OPTIONAL_FIELDS = ['reference', 'notes']
PAYMENT_METHODS = ['upi', 'cash', 'bank_transfer', 'card', 'other']


def validate_payment_row(row, row_num, order_map):
    """Validate a single payment row"""
    errors = validate_required_fields(row, PAYMENT_REQUIRED_FIELDS, row_num)
    
    order_number = row.get('order_number', '').strip()
    if order_number and order_number not in order_map:
        errors.append(f"Row {row_num}: Order '{order_number}' not found")
    
    amount, err = parse_decimal(row.get('amount'), 'amount', row_num)
    if err:
        errors.append(err)
    elif amount is not None and amount <= 0:
        errors.append(f"Row {row_num}: Amount must be greater than 0")
    
    method = row.get('payment_method', '').strip().lower()
    if method and method not in PAYMENT_METHODS:
        errors.append(f"Row {row_num}: Invalid payment method '{method}'. Must be one of: {', '.join(PAYMENT_METHODS)}")
    
    payment_date, err = parse_date(row.get('payment_date'), 'payment_date', row_num)
    if err:
        errors.append(err)
    
    return errors


def import_payment_row(row, order_map):
    """Import a single payment row"""
    order_number = row['order_number'].strip()
    order = order_map[order_number]
    amount, _ = parse_decimal(row['amount'], 'amount', 0)
    payment_date, _ = parse_date(row['payment_date'], 'payment_date', 0)
    
    payment = Payment.objects.create(
        order=order,
        amount=amount,
        method=row['payment_method'].strip().lower(),  # field is 'method' not 'payment_method'
        payment_date=payment_date,
        reference=row.get('reference', '').strip() or None,
        remarks=row.get('notes', '').strip() or None  # field is 'remarks' not 'notes'
    )
    return payment.id


# =============================================================================
# API VIEWS
# =============================================================================

class ImportPreviewView(APIView):
    """Preview import data before confirming"""
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            import_type = request.data.get('import_type')
            
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not import_type:
                return Response({'error': 'No import type specified'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse file
            file_name = file.name.lower()
            if file_name.endswith('.csv'):
                headers, rows = parse_csv_file(file)
            elif file_name.endswith(('.xlsx', '.xls')):
                headers, rows = parse_excel_file(file)
            else:
                return Response({'error': 'Unsupported file type. Use CSV or Excel.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not rows:
                return Response({'error': 'File is empty or has no data rows'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate based on import type
            all_errors = []
            valid_rows = []
            
            if import_type == 'customers':
                existing_mobiles = set(Customer.objects.values_list('mobile', flat=True))
                seen_mobiles = set()
                
                for i, row in enumerate(rows, start=2):
                    errors = validate_customer_row(row, i, existing_mobiles | seen_mobiles)
                    if errors:
                        all_errors.extend(errors)
                    else:
                        valid_rows.append(row)
                        seen_mobiles.add(row.get('mobile', '').strip())
            
            elif import_type == 'products':
                existing_names = set(
                    f"{p.name}|{p.unit}".lower() 
                    for p in Product.objects.all()
                )
                seen_names = set()
                
                for i, row in enumerate(rows, start=2):
                    errors = validate_product_row(row, i, existing_names | seen_names)
                    if errors:
                        all_errors.extend(errors)
                    else:
                        valid_rows.append(row)
                        name_key = f"{row.get('name', '')}|{row.get('unit', '')}".lower()
                        seen_names.add(name_key)
            
            elif import_type == 'orders':
                customer_map = {c.mobile: c.id for c in Customer.objects.all()}
                product_map = {p.name.lower(): p for p in Product.objects.filter(is_active=True)}
                
                for i, row in enumerate(rows, start=2):
                    errors = validate_order_row(row, i, customer_map, product_map)
                    if errors:
                        all_errors.extend(errors)
                    else:
                        valid_rows.append(row)
            
            elif import_type == 'payments':
                order_map = {o.order_number: o for o in Order.objects.all()}
                
                for i, row in enumerate(rows, start=2):
                    errors = validate_payment_row(row, i, order_map)
                    if errors:
                        all_errors.extend(errors)
                    else:
                        valid_rows.append(row)
            
            else:
                return Response({'error': f'Unknown import type: {import_type}'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Build preview data (first 10 rows)
            preview_data = []
            for row in rows[:10]:
                preview_data.append({k: str(v)[:50] for k, v in row.items()})
            
            return Response({
                'headers': headers,
                'total_rows': len(rows),
                'valid_rows': len(valid_rows),
                'invalid_rows': len(rows) - len(valid_rows),
                'errors': all_errors[:50],  # Limit errors shown
                'preview_data': preview_data,
                'has_more_errors': len(all_errors) > 50
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportConfirmView(APIView):
    """Confirm and execute import"""
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            import_type = request.data.get('import_type')
            import_mode = request.data.get('import_mode', 'valid_only')  # 'valid_only' or 'all_or_nothing'
            
            if not file or not import_type:
                return Response({'error': 'File and import_type are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse file
            file_name = file.name.lower()
            original_name = file.name
            if file_name.endswith('.csv'):
                headers, rows = parse_csv_file(file)
            elif file_name.endswith(('.xlsx', '.xls')):
                headers, rows = parse_excel_file(file)
            else:
                return Response({'error': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create import log
            import_log = ImportLog.objects.create(
                import_type=import_type,
                file_name=original_name,
                status='processing',
                total_rows=len(rows),
                imported_by=request.user
            )
            
            all_errors = []
            valid_rows = []
            imported_ids = []
            
            try:
                with transaction.atomic():
                    if import_type == 'customers':
                        existing_mobiles = set(Customer.objects.values_list('mobile', flat=True))
                        seen_mobiles = set()
                        
                        for i, row in enumerate(rows, start=2):
                            errors = validate_customer_row(row, i, existing_mobiles | seen_mobiles)
                            if errors:
                                all_errors.extend(errors)
                            else:
                                valid_rows.append(row)
                                seen_mobiles.add(row.get('mobile', '').strip())
                        
                        if import_mode == 'all_or_nothing' and all_errors:
                            raise ValueError("Validation errors found")
                        
                        for row in valid_rows:
                            cid = import_customer_row(row)
                            imported_ids.append(cid)
                    
                    elif import_type == 'products':
                        existing_names = set(
                            f"{p.name}|{p.unit}".lower() 
                            for p in Product.objects.all()
                        )
                        seen_names = set()
                        
                        for i, row in enumerate(rows, start=2):
                            errors = validate_product_row(row, i, existing_names | seen_names)
                            if errors:
                                all_errors.extend(errors)
                            else:
                                valid_rows.append(row)
                                name_key = f"{row.get('name', '')}|{row.get('unit', '')}".lower()
                                seen_names.add(name_key)
                        
                        if import_mode == 'all_or_nothing' and all_errors:
                            raise ValueError("Validation errors found")
                        
                        for row in valid_rows:
                            pid = import_product_row(row)
                            imported_ids.append(pid)
                    
                    elif import_type == 'orders':
                        customer_map = {c.mobile: c.id for c in Customer.objects.all()}
                        product_map = {p.name.lower(): p for p in Product.objects.filter(is_active=True)}
                        
                        for i, row in enumerate(rows, start=2):
                            errors = validate_order_row(row, i, customer_map, product_map)
                            if errors:
                                all_errors.extend(errors)
                            else:
                                valid_rows.append(row)
                        
                        if import_mode == 'all_or_nothing' and all_errors:
                            raise ValueError("Validation errors found")
                        
                        imported_ids = import_orders_batch(valid_rows, customer_map, product_map)
                    
                    elif import_type == 'payments':
                        order_map = {o.order_number: o for o in Order.objects.all()}
                        
                        for i, row in enumerate(rows, start=2):
                            errors = validate_payment_row(row, i, order_map)
                            if errors:
                                all_errors.extend(errors)
                            else:
                                valid_rows.append(row)
                        
                        if import_mode == 'all_or_nothing' and all_errors:
                            raise ValueError("Validation errors found")
                        
                        for row in valid_rows:
                            pid = import_payment_row(row, order_map)
                            imported_ids.append(pid)
                
                # Update import log
                import_log.status = 'completed'
                import_log.successful_rows = len(imported_ids)
                import_log.failed_rows = len(rows) - len(valid_rows)
                import_log.errors = all_errors[:100]
                import_log.imported_ids = imported_ids
                import_log.completed_at = timezone.now()
                import_log.save()
                
                return Response({
                    'success': True,
                    'import_id': import_log.id,
                    'total_rows': len(rows),
                    'imported': len(imported_ids),
                    'failed': len(rows) - len(valid_rows),
                    'errors': all_errors[:50]
                })
                
            except ValueError as e:
                import_log.status = 'failed'
                import_log.errors = all_errors[:100]
                import_log.completed_at = timezone.now()
                import_log.save()
                
                return Response({
                    'success': False,
                    'import_id': import_log.id,
                    'message': 'Import failed due to validation errors',
                    'errors': all_errors[:50]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportHistoryView(APIView):
    """View import history"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        logs = ImportLog.objects.all()[:50]
        serializer = ImportLogSerializer(logs, many=True)
        return Response(serializer.data)


class ImportTemplateView(APIView):
    """Get sample import templates"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, import_type):
        templates = {
            'customers': {
                'required_fields': CUSTOMER_REQUIRED_FIELDS,
                'optional_fields': CUSTOMER_OPTIONAL_FIELDS,
                'sample_data': [
                    {'name': 'Priya Sharma', 'mobile': '9876543210', 'email': 'priya@email.com', 'apartment_name': 'Prestige Lakeside', 'block': 'A', 'address': 'Flat 101', 'notes': 'Prefers evening delivery'},
                    {'name': 'Rajesh Kumar', 'mobile': '9876543211', 'email': '', 'apartment_name': 'Brigade Gateway', 'block': 'Tower 1', 'address': 'Flat 205', 'notes': ''},
                ]
            },
            'products': {
                'required_fields': PRODUCT_REQUIRED_FIELDS,
                'optional_fields': PRODUCT_OPTIONAL_FIELDS,
                'categories': PRODUCT_CATEGORIES,
                'sample_data': [
                    {'name': 'Tomato Soup', 'category': 'soups', 'unit': '250ml', 'selling_price': '80', 'unit_cost': '35', 'description': 'Classic tomato soup', 'is_active': 'true'},
                    {'name': 'Samosa', 'category': 'snacks', 'unit': '2 pcs', 'selling_price': '40', 'unit_cost': '18', 'description': 'Crispy samosas', 'is_active': 'true'},
                ]
            },
            'orders': {
                'required_fields': ORDER_REQUIRED_FIELDS,
                'optional_fields': ORDER_OPTIONAL_FIELDS,
                'notes': 'Multiple rows with same customer_mobile and order_date will be grouped into one order',
                'sample_data': [
                    {'customer_mobile': '9876543210', 'order_date': '2026-03-27', 'product_name': 'Tomato Soup', 'quantity': '2', 'unit_price': '80', 'order_type': 'delivery', 'status': 'confirmed'},
                    {'customer_mobile': '9876543210', 'order_date': '2026-03-27', 'product_name': 'Samosa', 'quantity': '1', 'unit_price': '40', 'order_type': 'delivery', 'status': 'confirmed'},
                ]
            },
            'payments': {
                'required_fields': PAYMENT_REQUIRED_FIELDS,
                'optional_fields': PAYMENT_OPTIONAL_FIELDS,
                'payment_methods': PAYMENT_METHODS,
                'sample_data': [
                    {'order_number': 'ORD-20260327-0001', 'amount': '200', 'payment_method': 'upi', 'payment_date': '2026-03-27', 'reference': 'UPI123456', 'notes': ''},
                ]
            }
        }
        
        if import_type not in templates:
            return Response({'error': f'Unknown import type: {import_type}'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(templates[import_type])
