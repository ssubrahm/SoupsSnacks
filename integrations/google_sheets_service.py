"""
Google Sheets Integration Service

This service handles reading from and optionally writing to Google Sheets.
It uses a Service Account for authentication (no OAuth flow needed).

Setup:
1. Create a Google Cloud project
2. Enable the Google Sheets API
3. Create a Service Account and download the JSON key
4. Share your Google Sheet with the service account email
5. Save the JSON key as 'google_credentials.json' in the project root
   OR set GOOGLE_CREDENTIALS_JSON environment variable with the JSON content
"""

import os
import json
import hashlib
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from customers.models import Customer
from catalog.models import Product
from orders.models import Order, OrderItem
from .models import GoogleSheetConfig, GoogleSheetSyncLog, GoogleSheetOrderRef


def get_google_credentials():
    """Get Google credentials from file or environment variable"""
    # Try environment variable first
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        return json.loads(creds_json)
    
    # Try file
    creds_file = os.path.join(settings.BASE_DIR, 'google_credentials.json')
    if os.path.exists(creds_file):
        with open(creds_file, 'r') as f:
            return json.load(f)
    
    return None


def get_sheets_service():
    """Initialize Google Sheets API service"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "Google API libraries not installed. Run: "
            "pip install google-auth google-auth-oauthlib google-api-python-client"
        )
    
    credentials_info = get_google_credentials()
    if not credentials_info:
        raise ValueError(
            "Google credentials not found. Either set GOOGLE_CREDENTIALS_JSON "
            "environment variable or create google_credentials.json file."
        )
    
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    return service.spreadsheets()


def read_sheet_data(sheet_id, tab_name, start_row=1):
    """Read all data from a Google Sheet tab starting from a specific row"""
    sheets = get_sheets_service()
    
    # Read the entire sheet
    range_name = f"'{tab_name}'!A{start_row}:Z"
    
    result = sheets.values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()
    
    rows = result.get('values', [])
    return rows


def write_to_sheet(sheet_id, tab_name, row_num, column, value):
    """Write a value to a specific cell"""
    sheets = get_sheets_service()
    
    cell_range = f"'{tab_name}'!{column}{row_num}"
    
    body = {
        'values': [[value]]
    }
    
    sheets.values().update(
        spreadsheetId=sheet_id,
        range=cell_range,
        valueInputOption='RAW',
        body=body
    ).execute()


def compute_row_hash(row_data):
    """Compute a hash of row data for duplicate detection"""
    row_str = '|'.join(str(cell) for cell in row_data)
    return hashlib.sha256(row_str.encode()).hexdigest()[:32]


def parse_value(value, field_type='string'):
    """Parse a cell value based on expected type"""
    if value is None or str(value).strip() == '':
        return None
    
    value = str(value).strip()
    
    if field_type == 'string':
        return value
    elif field_type == 'integer':
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    elif field_type == 'decimal':
        try:
            return Decimal(value.replace(',', ''))
        except (InvalidOperation, ValueError):
            return None
    elif field_type == 'date':
        # Try various formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%m/%d/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        # Try Excel serial date
        try:
            serial = float(value)
            if 1 < serial < 100000:
                from datetime import timedelta
                excel_epoch = datetime(1899, 12, 30)
                return (excel_epoch + timedelta(days=serial)).date()
        except (ValueError, TypeError):
            pass
        return None
    
    return value


def get_cell_value(row, column_letter, headers=None):
    """Get value from a row by column letter (A, B, C...) or header name"""
    if not column_letter:
        return None
    
    # Convert column letter to index (A=0, B=1, etc.)
    col_index = ord(column_letter.upper()) - ord('A')
    
    if col_index < 0 or col_index >= len(row):
        return None
    
    return row[col_index]


def find_or_create_customer(name, mobile, apartment=None, block=None):
    """Find existing customer by mobile or create new one"""
    if not mobile:
        return None, "Mobile number is required"
    
    # Clean mobile number
    mobile = str(mobile).strip().replace(' ', '').replace('-', '')
    
    # Try to find existing customer
    customer = Customer.objects.filter(mobile=mobile).first()
    if customer:
        return customer, None
    
    # Create new customer
    if not name:
        name = f"Customer {mobile[-4:]}"
    
    customer = Customer.objects.create(
        name=name.strip(),
        mobile=mobile,
        apartment_name=apartment,
        block=block,
        is_active=True
    )
    return customer, None


def sync_google_sheet(config_id, user=None):
    """
    Sync orders from a Google Sheet.
    
    Returns:
        GoogleSheetSyncLog: The sync log with results
    """
    config = GoogleSheetConfig.objects.get(id=config_id)
    
    # Create sync log
    sync_log = GoogleSheetSyncLog.objects.create(
        config=config,
        status='running',
        started_at=timezone.now(),
        synced_by=user
    )
    
    errors = []
    created_order_ids = []
    rows_processed = 0
    rows_created = 0
    rows_skipped = 0
    rows_failed = 0
    
    try:
        # Get field mapping
        mapping = config.field_mapping
        if not mapping:
            raise ValueError("Field mapping is not configured")
        
        # Read sheet data (skip header row)
        all_rows = read_sheet_data(config.sheet_id, config.tab_name, start_row=1)
        
        if not all_rows:
            sync_log.status = 'completed'
            sync_log.completed_at = timezone.now()
            sync_log.save()
            return sync_log
        
        # First row is headers
        headers = all_rows[0] if all_rows else []
        data_rows = all_rows[1:] if len(all_rows) > 1 else []
        
        # Get existing row references for this config
        existing_refs = set(
            GoogleSheetOrderRef.objects.filter(config=config)
            .values_list('sheet_row', flat=True)
        )
        
        # Get product for orders
        default_product = None
        if config.default_product_id:
            default_product = Product.objects.filter(id=config.default_product_id).first()
        
        # Process each row
        for i, row in enumerate(data_rows):
            row_num = i + 2  # +2 because we skip header and rows are 1-indexed
            rows_processed += 1
            
            try:
                # Skip already synced rows
                if row_num in existing_refs:
                    rows_skipped += 1
                    continue
                
                # Skip empty rows
                if not any(cell for cell in row if cell):
                    rows_skipped += 1
                    continue
                
                # Extract data based on mapping
                customer_name = get_cell_value(row, mapping.get('customer_name'))
                mobile = get_cell_value(row, mapping.get('mobile'))
                apartment = get_cell_value(row, mapping.get('apartment'))
                block = get_cell_value(row, mapping.get('block'))
                product_name = get_cell_value(row, mapping.get('product_name'))
                quantity = get_cell_value(row, mapping.get('quantity'))  # Can be "500g", "1 KG", or a number
                size = get_cell_value(row, mapping.get('size'))  # Optional separate size field
                order_date = get_cell_value(row, mapping.get('order_date'))
                notes = get_cell_value(row, mapping.get('notes'))
                
                # If size field is mapped separately, use it; otherwise quantity might contain size
                if size:
                    quantity = size  # Size takes precedence for product matching
                
                # Validate required fields
                if not mobile:
                    errors.append(f"Row {row_num}: Missing mobile number")
                    rows_failed += 1
                    continue
                
                # Parse order date
                parsed_date = parse_value(order_date, 'date')
                if not parsed_date:
                    parsed_date = date.today()
                
                # Find or create customer
                customer, error = find_or_create_customer(
                    customer_name, mobile, apartment, block
                )
                if error:
                    errors.append(f"Row {row_num}: {error}")
                    rows_failed += 1
                    continue
                
                # Find product - smart matching for size/variant selection
                # The "quantity" field from form might be "500g" or "1 KG" (text, not number)
                product = None
                qty = 1  # Default quantity is always 1 when using size variants
                
                # Clean up the values
                product_search = (product_name or '').strip()
                size_selection = (quantity or '').strip()
                
                # Strategy 1: Try matching "product_name size" (e.g., "Tender Mango Pickle 500g")
                if product_search and size_selection:
                    combined_search = f"{product_search} {size_selection}"
                    product = Product.objects.filter(
                        name__icontains=combined_search,
                        is_active=True
                    ).first()
                
                # Strategy 2: Try matching just the size in product name (e.g., "500g" matches "Tender Mango Pickle 500g")
                if not product and size_selection:
                    product = Product.objects.filter(
                        name__icontains=size_selection,
                        is_active=True
                    ).first()
                
                # Strategy 3: Try matching product name alone
                if not product and product_search:
                    product = Product.objects.filter(
                        name__icontains=product_search,
                        is_active=True
                    ).first()
                
                # Strategy 4: Try matching size in product's unit field
                if not product and size_selection:
                    product = Product.objects.filter(
                        unit__icontains=size_selection,
                        is_active=True
                    ).first()
                
                # Strategy 5: Fall back to default product
                if not product:
                    product = default_product
                
                # If quantity looks like a number, use it as actual quantity
                if not product and size_selection:
                    # Last resort: try parsing as integer quantity with default product
                    parsed_qty = parse_value(size_selection, 'integer')
                    if parsed_qty and parsed_qty > 0 and default_product:
                        product = default_product
                        qty = parsed_qty
                
                if not product:
                    search_terms = f"product='{product_search}', size='{size_selection}'"
                    errors.append(f"Row {row_num}: Product not found ({search_terms})")
                    rows_failed += 1
                    continue
                
                # Create order
                with transaction.atomic():
                    order = Order.objects.create(
                        customer=customer,
                        order_date=parsed_date,
                        order_type=config.default_order_type,
                        status='confirmed',
                        payment_status='pending',
                        notes=f"Imported from Google Form. {notes or ''}"
                    )
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        unit_price=product.selling_price,
                        unit_cost_snapshot=product.unit_cost,
                        display_order=0
                    )
                    
                    # Create reference to prevent duplicates
                    row_hash = compute_row_hash(row)
                    GoogleSheetOrderRef.objects.create(
                        config=config,
                        sheet_row=row_num,
                        row_hash=row_hash,
                        order=order
                    )
                    
                    created_order_ids.append(order.id)
                    rows_created += 1
                    
                    # Write back if enabled
                    if config.write_back_enabled:
                        try:
                            if config.order_number_column:
                                write_to_sheet(
                                    config.sheet_id,
                                    config.tab_name,
                                    row_num,
                                    config.order_number_column,
                                    order.order_number
                                )
                            if config.status_column:
                                write_to_sheet(
                                    config.sheet_id,
                                    config.tab_name,
                                    row_num,
                                    config.status_column,
                                    order.status
                                )
                        except Exception as wb_error:
                            errors.append(f"Row {row_num}: Write-back failed: {str(wb_error)}")
                
            except Exception as row_error:
                errors.append(f"Row {row_num}: {str(row_error)}")
                rows_failed += 1
        
        # Update config with last synced info
        config.last_synced_row = len(all_rows)
        config.save()
        
        sync_log.status = 'completed'
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        errors.append(f"Sync error: {str(e)}")
        sync_log.status = 'failed'
    
    # Save sync log
    sync_log.rows_processed = rows_processed
    sync_log.rows_created = rows_created
    sync_log.rows_skipped = rows_skipped
    sync_log.rows_failed = rows_failed
    sync_log.errors = errors
    sync_log.created_order_ids = created_order_ids
    sync_log.completed_at = timezone.now()
    sync_log.save()
    
    return sync_log


def test_connection(sheet_id, tab_name):
    """Test connection to a Google Sheet"""
    try:
        rows = read_sheet_data(sheet_id, tab_name, start_row=1)
        headers = rows[0] if rows else []
        row_count = len(rows) - 1 if rows else 0
        
        return {
            'success': True,
            'headers': headers,
            'row_count': row_count,
            'message': f"Successfully connected. Found {row_count} data rows."
        }
    except Exception as e:
        return {
            'success': False,
            'headers': [],
            'row_count': 0,
            'message': str(e)
        }
