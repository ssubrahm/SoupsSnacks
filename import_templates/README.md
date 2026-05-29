# Import Templates and Test Files

This folder contains CSV templates and test files for data import functionality.

## Templates (for production use)

| File | Description |
|------|-------------|
| `customers_template.csv` | Template for importing customers |
| `products_template.csv` | Template for importing products |
| `orders_template.csv` | Template for importing orders |
| `payments_template.csv` | Template for importing payments |

## Test Files (for testing import functionality)

| File | Description |
|------|-------------|
| `test_customers_valid.csv` | 5 valid customers - should import 100% |
| `test_customers_mixed.csv` | 3 valid, 3 invalid - tests error handling |
| `test_products_valid.csv` | 5 valid products - should import 100% |
| `test_products_mixed.csv` | 2 valid, 3 invalid - tests error handling |

## Field Requirements

### Customers
**Required:** name, mobile
**Optional:** email, apartment_name, block, address, notes

### Products
**Required:** name, category, unit, selling_price
**Optional:** unit_cost, description, is_active
**Valid categories:** soups, snacks, sweets, lunch, dinner, pickle, combos, other

### Orders
**Required:** customer_mobile, order_date, product_name, quantity, unit_price
**Optional:** order_type, delivery_address, notes, status
**Note:** Multiple rows with same customer_mobile + order_date are grouped into one order

### Payments
**Required:** order_number, amount, payment_method, payment_date
**Optional:** reference, notes
**Valid payment methods:** upi, cash, bank_transfer, card, other

## Date Formats Supported
- YYYY-MM-DD (recommended)
- DD/MM/YYYY
- MM/DD/YYYY
- DD-MM-YYYY

## Testing Procedure

1. Go to Import page (Admin only)
2. Select import type
3. Upload test file
4. Click Preview to see validation results
5. Click Import to execute
6. Check Import History tab for results
7. Verify imported data in respective pages

## Cleanup

All test data is prefixed with "IMPORT TEST -" for easy identification.
Use the following to delete test imports:

```python
from customers.models import Customer
from catalog.models import Product

Customer.objects.filter(name__startswith='IMPORT TEST -').delete()
Product.objects.filter(name__startswith='IMPORT TEST -').delete()
```
