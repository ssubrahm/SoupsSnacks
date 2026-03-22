# Google Sheets Import Guide

## Overview

The Order Management system supports importing orders from Google Sheets via CSV export. This allows you to collect orders through Google Forms or manual Google Sheets entry, then bulk import them into the system.

---

## Google Sheets Template

Create a Google Sheet with these **exact column headers** (column order doesn't matter):

| Column Name | Required | Description | Example |
|-------------|----------|-------------|---------|
| customer_name | Yes | Customer's full name | Rajesh Kumar |
| customer_mobile | Yes | Customer's mobile number | 9876543210 |
| order_date | Yes | Date order was placed | 2026-03-23 or 23/03/2026 |
| fulfillment_date | No | Date to fulfill order | 2026-03-24 or 24/03/2026 |
| product_name | Yes | Exact product name from catalog | Cream of Tomato Soup |
| quantity | Yes | Number of units | 2 |
| unit_price | No | Price per unit (uses catalog price if empty) | 80 |
| order_type | No | delivery or pickup (default: delivery) | delivery |
| delivery_address | No | Delivery address if different from customer default | Flat 301 Tower A |
| notes | No | Order notes | Customer requested extra packaging |

---

## Template Google Sheet

**View/Copy Template:** [Create a copy of this template](https://docs.google.com/spreadsheets/d/YOUR_TEMPLATE_ID/copy)

Or create your own with this structure:

```
customer_name | customer_mobile | order_date | fulfillment_date | product_name | quantity | unit_price | order_type | delivery_address | notes
```

---

## Sample Data

```csv
customer_name,customer_mobile,order_date,fulfillment_date,product_name,quantity,unit_price,order_type,delivery_address,notes
Rajesh Kumar,9876543210,2026-03-23,2026-03-24,Cream of Tomato Soup,2,80,delivery,Flat 301 Tower A,Customer requested extra packaging
Rajesh Kumar,9876543210,2026-03-23,2026-03-24,Masala Bajji,1,60,delivery,Flat 301 Tower A,Customer requested extra packaging
Priya Sharma,9876543211,2026-03-23,2026-03-23,Upma,3,50,pickup,,Morning pickup preferred
```

---

## How It Works

### 1. Grouping Orders
Orders are **automatically grouped** by `customer_mobile` + `order_date`. Multiple rows with the same customer and date become **one order with multiple items**.

**Example:**
```
Rajesh Kumar, 9876543210, 2026-03-23 → Order #1
  - Item 1: Tomato Soup × 2
  - Item 2: Bajji × 1

Priya Sharma, 9876543211, 2026-03-23 → Order #2
  - Item 1: Upma × 3
```

### 2. Customer Matching
System finds customers by:
- Exact mobile number match, OR
- Case-insensitive name match

**If customer not found:** Row is skipped with error message.

### 3. Product Matching
System finds products by:
- Case-insensitive exact name match

**Product name must match catalog exactly!** (e.g., "Cream of Tomato Soup" not "Tomato Soup")

**If product not found:** Item is skipped with error message.

### 4. Price Handling
- If `unit_price` provided: Uses that price
- If `unit_price` empty: Uses product's current catalog price

### 5. Cost Snapshot
System **automatically captures** the product's `unit_cost` at import time. This preserves historical costs even if product costs change later.

---

## Import Process

### Step 1: Prepare Google Sheet
1. Create Google Sheet with correct column headers
2. Fill in order data (one row per product per order)
3. Validate data:
   - Customer names/mobiles match your customer list
   - Product names match catalog exactly
   - Dates in format: YYYY-MM-DD or DD/MM/YYYY
   - Quantities are positive integers

### Step 2: Export to CSV
1. In Google Sheets: File → Download → Comma-separated values (.csv)
2. Save file (e.g., `orders_2026-03-23.csv`)

### Step 3: Import in App
1. Login as Operator or Admin
2. Go to **🥘 Orders** page
3. Click **📥 Import from CSV** button
4. Select your CSV file
5. Click **Upload**
6. Review import results

### Step 4: Review Imported Orders
- Check **Orders** list for new entries
- All imported orders start as **Draft** status
- Review each order and confirm details
- Change status to **Confirmed** when ready

---

## Google Forms Integration

You can collect orders via Google Forms that feeds into a Google Sheet:

### Form Setup
1. Create Google Form with fields:
   - Name (Short answer)
   - Mobile Number (Short answer)
   - Delivery Date (Date)
   - Products (Checkboxes or Multiple choice)
   - Quantities (Short answer for each product)
   - Delivery Address (Paragraph)
   - Special Instructions (Paragraph)

2. Link form responses to Google Sheet

3. Manually format responses into import template columns

4. Export and import as above

---

## Data Validation Tips

### Before Import:
✅ **Check customers exist** in system
✅ **Product names match exactly** (including spaces, capitalization)
✅ **Dates are valid** and in correct format
✅ **Quantities are positive numbers**
✅ **Mobile numbers don't have spaces or special characters**

### Common Issues:

**❌ "Customer not found"**
- Add customer to system first via Customers page
- Check mobile number is exactly 10 digits
- Verify spelling of customer name

**❌ "Product not found"**
- Check product exists in Menu/Catalog
- Verify exact spelling and spacing
- Product must be active

**❌ "Invalid quantity"**
- Ensure quantity is a whole number
- No decimals or text

**❌ "Invalid date"**
- Use YYYY-MM-DD (2026-03-23) or DD/MM/YYYY (23/03/2026)
- Don't use slashes in YYYY-MM-DD format

---

## Import Results

After import, you'll see:
- **Orders Created:** Number of new orders
- **Errors:** List of rows that failed with reasons
- **Success Message:** Confirmation

**Example Output:**
```
✅ Successfully imported 3 orders

Errors:
- Row 5: Customer 'Unknown Person' not found. Skipping.
- Row 8: Product 'Veggie Soup' not found. Skipping item.
```

---

## Best Practices

1. **Test with small batch first** (2-3 orders)
2. **Keep original Google Sheet** as backup
3. **Add customers before importing orders**
4. **Use consistent product names** matching your catalog
5. **Review all imported orders** before confirming
6. **Update order status** after verification
7. **Mark payment status** after receiving payment

---

## Field Mapping Reference

| Google Sheet Field | App Field | Notes |
|-------------------|-----------|-------|
| customer_name | Order.customer | Matched by name or mobile |
| customer_mobile | Order.customer | Primary matching field |
| order_date | Order.order_date | Parsed flexibly |
| fulfillment_date | Order.fulfillment_date | Optional |
| product_name | OrderItem.product | Must match exactly |
| quantity | OrderItem.quantity | Integer |
| unit_price | OrderItem.unit_price | Falls back to catalog price |
| N/A (auto) | OrderItem.unit_cost_snapshot | Auto-captured from product |
| order_type | Order.order_type | delivery or pickup |
| delivery_address | Order.delivery_address | Optional |
| notes | Order.notes | Optional |

---

## Sample Use Cases

### Use Case 1: WhatsApp Order Collection
1. Customers send orders via WhatsApp
2. Manually enter into Google Sheet
3. Export and import daily
4. Confirm each order

### Use Case 2: Google Forms Order Collection
1. Share Google Form link
2. Form responses auto-populate Sheet
3. Reformat if needed
4. Export and import
5. Bulk process orders

### Use Case 3: Bulk Order Entry
1. Take phone orders throughout the day
2. Note in Google Sheet
3. Import once at end of day
4. Process all orders together

---

## Troubleshooting

### Import fails completely
- Check CSV encoding (must be UTF-8)
- Verify column headers match exactly
- Remove any special characters
- Check file is actually .csv format

### Some orders missing items
- Verify product names match catalog
- Check for typos or extra spaces
- Ensure products are active

### Wrong customer assigned
- Mobile number is primary matcher
- If mobile not found, falls back to name
- Ensure mobile numbers are unique

### Prices wrong
- Check unit_price column has values
- Verify decimal separator (use . not ,)
- Leave empty to use catalog prices

---

## Template Download

A sample CSV template is available in the project:
```
/SoupsSnacks/GOOGLE_SHEETS_IMPORT_TEMPLATE.csv
```

Import this file to see the format and test the import feature!

---

## Future Enhancements

Planned features:
- Direct Google Sheets API integration (no CSV export needed)
- Order status update via Google Sheets
- Automatic customer creation if not found
- Fuzzy product name matching
- Bulk status updates
- Import history and rollback

---

## Support

If you encounter issues:
1. Check error messages in import results
2. Verify data format matches template
3. Test with sample template first
4. Review validation guide above
5. Contact system administrator

---

**Happy Importing! 📊**
