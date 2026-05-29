# Step 6 - Order Management - Validation Guide

## ✅ Acceptance Checklist

Follow these steps to validate that Step 6 is complete and working correctly.

### Prerequisites

1. **Pull latest code and setup:**
   ```bash
   cd /Users/Srinath.Subrahmanyan/SoupsSnacks
   git pull origin main
   source SSCo/bin/activate
   python manage.py migrate
   ```

2. **Ensure sample data exists:**
   ```bash
   python manage.py create_test_users
   python manage.py create_sample_customers
   python manage.py create_sample_products
   ```

3. **Start servers:**
   ```bash
   ./setup.sh
   ```

4. **Login as operator or admin:**
   - Open http://localhost:3000
   - Login with: `operator / operator123` or `admin / admin123`
   - Navigate to "🥘 Orders" in sidebar

---

## 🧪 Manual Validation Tests

### Test 1: Orders List Page Loads

**Steps:**
1. Click "🥘 Orders" in the sidebar
2. Observe the page

**Expected Results:**
- ✅ Page loads without errors
- ✅ Shows empty state if no orders exist
- ✅ Shows stats cards: Total Orders, Total Revenue, Total Profit
- ✅ Shows search box and filter dropdowns
- ✅ Shows "+ Create Order" button
- ✅ Shows "📥 Import CSV" button

---

### Test 2: Create Order Manually - Single Item

**Steps:**
1. Click "+ Create Order"
2. Fill in order information:
   - Customer: Select any customer
   - Order Date: Today's date (pre-filled)
   - Fulfillment Date: Tomorrow
   - Order Type: Delivery
   - Status: Draft
   - Payment Status: Pending
3. Click "+ Add Item"
4. Select product: "Cream of Tomato Soup (250ml)"
5. Observe unit_price and unit_cost_snapshot auto-fill
6. Set Quantity: 2
7. Observe order summary sidebar updates
8. Click "Create Order"

**Expected Results:**
- ✅ Form loads with all fields
- ✅ Customers dropdown populated
- ✅ When product selected, unit_price auto-fills (₹80.00)
- ✅ unit_cost_snapshot auto-fills from product (₹52.60)
- ✅ Line total shows: ₹160.00 (2 × 80)
- ✅ Line cost shows: ₹105.20 (2 × 52.60)
- ✅ Line profit shows: ₹54.80 (160 - 105.20)
- ✅ Order summary shows same totals
- ✅ Margin shows: 34.2%
- ✅ Order created successfully
- ✅ Redirected to orders list
- ✅ New order appears with auto-generated order number (ORD-YYYYMMDD-0001)

---

### Test 3: Create Order with Multiple Items

**Steps:**
1. Click "+ Create Order"
2. Select customer
3. Click "+ Add Item" THREE times
4. Add items:
   - Item 1: Cream of Tomato Soup (250ml) × 2
   - Item 2: Masala Bajji (6 pieces) × 1
   - Item 3: Mango Pickle (200g jar) × 1
5. Observe totals update after each item
6. Click "Create Order"

**Expected Results:**
- ✅ Can add multiple items
- ✅ Each item calculates independently
- ✅ Order summary shows combined totals:
  - Revenue: ₹340.00 (160 + 60 + 120)
  - Cost: ₹233.90 (105.20 + 58.90 + 70.20)
  - Profit: ₹106.10
  - Margin: 31.2%
- ✅ All items appear in order

---

### Test 4: Verify Order Number Generation

**Steps:**
1. Create 3 orders on the same day
2. Note the order numbers

**Expected Results:**
- ✅ First order: ORD-YYYYMMDD-0001
- ✅ Second order: ORD-YYYYMMDD-0002
- ✅ Third order: ORD-YYYYMMDD-0003
- ✅ Format is consistent: ORD-{date}-{sequence}
- ✅ Sequence increments per day

---

### Test 5: Cost Snapshot Preservation (CRITICAL)

**Steps:**
1. Create an order with "Cream of Tomato Soup (250ml)"
2. Note the unit_cost_snapshot (should be ₹52.60)
3. Note the order profit
4. Go to Menu → Edit "Cream of Tomato Soup (250ml)"
5. Change a cost component to increase total cost
6. Save product (new cost might be ₹60.00)
7. Return to the order detail page
8. Check unit_cost_snapshot value

**Expected Results:**
- ✅ Order still shows unit_cost_snapshot: ₹52.60 (OLD cost)
- ✅ Order profit unchanged
- ✅ Cost snapshot is IMMUTABLE after order creation
- ✅ New orders will use new cost (₹60.00)
- ✅ Historical orders preserve their snapshot

**This is CRITICAL for accurate profit tracking!**

---

### Test 6: Manual Calculation Verification

**Steps:**
1. Create order with known products
2. Use calculator to verify each calculation

**Example Order:**
- Product: Cream of Tomato Soup (250ml) × 2
- Unit Price: ₹80.00
- Unit Cost: ₹52.60

**Manual Calculations:**
```
Line Total = 2 × 80.00 = ₹160.00
Line Cost = 2 × 52.60 = ₹105.20
Line Profit = 160.00 - 105.20 = ₹54.80
Line Margin = (54.80 / 160.00) × 100 = 34.25% ≈ 34.2%
```

**Expected Results:**
- ✅ All calculations match manual verification
- ✅ No rounding errors
- ✅ Decimals correct (2 places for currency, 1 for %)

---

### Test 7: Order Detail Page

**Steps:**
1. Click on any order from the list
2. Observe the detail page

**Expected Results:**
- ✅ Shows order number and status badges
- ✅ Customer information displayed
- ✅ Order dates shown
- ✅ Items table with all columns:
  - Product, Unit, Qty, Unit Price, Unit Cost
  - Line Total, Line Cost, Line Profit, Margin
- ✅ Footer row shows order totals
- ✅ Order summary card with revenue/cost/profit
- ✅ Status management buttons visible
- ✅ Payment status buttons visible
- ✅ Edit button works
- ✅ Back button returns to list

---

### Test 8: Change Order Status

**Steps:**
1. Open any order detail page
2. Current status: "draft"
3. Click "confirmed" button in status section
4. Observe page updates

**Expected Results:**
- ✅ Status badge changes to "confirmed" (blue)
- ✅ Active button is highlighted
- ✅ Status updates immediately
- ✅ Can change through all statuses:
  - draft → confirmed → preparing → ready → delivered → completed
- ✅ Can also set to cancelled

---

### Test 9: Change Payment Status

**Steps:**
1. Open any order detail page
2. Current payment status: "pending"
3. Click "paid" button in payment section
4. Observe update

**Expected Results:**
- ✅ Payment badge changes to "paid" (green)
- ✅ Updates immediately
- ✅ Can change between: pending, partial, paid, refunded

---

### Test 10: Edit Existing Order

**Steps:**
1. Click edit on an order
2. Change quantity of an item from 2 to 3
3. Add a new item
4. Remove an existing item
5. Click "Update Order"

**Expected Results:**
- ✅ Form loads with existing data
- ✅ All items show correctly
- ✅ Can modify quantities
- ✅ Can add new items
- ✅ Can remove items
- ✅ Totals update in real-time
- ✅ Order updates successfully
- ✅ Changes reflected in detail page

---

### Test 11: Order List Filtering

**Steps:**
1. Create orders with different statuses
2. Use status filter dropdown
3. Select "Confirmed"
4. Observe results

**Expected Results:**
- ✅ Shows only confirmed orders
- ✅ Other statuses hidden
- ✅ Can filter by all status types
- ✅ Can filter by payment status
- ✅ "All Statuses" shows everything

---

### Test 12: Order Search

**Steps:**
1. Create several orders
2. Type order number in search box (e.g., "ORD-20260323-0001")
3. Try searching customer name
4. Try searching customer mobile

**Expected Results:**
- ✅ Search by order number works
- ✅ Search by customer name works
- ✅ Search by customer mobile works
- ✅ Search is case-insensitive
- ✅ Clear search shows all orders

---

### Test 13: Google Sheets Import - Prepare Template

**Steps:**
1. Open GOOGLE_SHEETS_IMPORT_TEMPLATE.csv
2. Review the format
3. Copy to Google Sheets
4. Verify column headers

**Expected Results:**
- ✅ Template has correct columns:
  - customer_name, customer_mobile, order_date, fulfillment_date
  - product_name, quantity, unit_price, order_type, delivery_address, notes
- ✅ Sample data present
- ✅ Multiple rows for same customer = grouped order

---

### Test 14: Google Sheets Import - Success Case

**Steps:**
1. Download GOOGLE_SHEETS_IMPORT_TEMPLATE.csv
2. Click "📥 Import CSV" on Orders page
3. Upload the template file
4. Wait for import to complete
5. Observe results

**Expected Results:**
- ✅ Import section expands
- ✅ File upload works
- ✅ Shows "Importing..." while processing
- ✅ Success message appears
- ✅ Shows "Orders Created: 3" (or however many in template)
- ✅ Lists any warnings/errors
- ✅ Orders appear in list
- ✅ All orders start as "Draft" status

---

### Test 15: Verify Imported Order Details

**Steps:**
1. After import, click on first imported order
2. Verify all details

**Expected Results for Sample Order (Rajesh Kumar):**
- ✅ Customer: Rajesh Kumar (matched by mobile)
- ✅ Order Date: 2026-03-23
- ✅ Fulfillment Date: 2026-03-24
- ✅ Items: 2 (Tomato Soup × 2, Bajji × 1)
- ✅ Unit prices match CSV or catalog
- ✅ unit_cost_snapshot captured from products
- ✅ Line totals calculated correctly
- ✅ Delivery address populated
- ✅ Notes included

---

### Test 16: Google Sheets Import - Error Handling

**Steps:**
1. Create a CSV with invalid data:
   - Unknown customer: "Test Person, 0000000000"
   - Unknown product: "Magic Soup"
2. Import the file
3. Observe error messages

**Expected Results:**
- ✅ Import completes (doesn't crash)
- ✅ Valid orders created
- ✅ Shows warnings section
- ✅ Lists specific errors:
  - "Row X: Customer 'Test Person' not found. Skipping."
  - "Row Y: Product 'Magic Soup' not found. Skipping item."
- ✅ Invalid rows skipped gracefully

---

### Test 17: Order Type (Delivery vs Pickup)

**Steps:**
1. Create order with Order Type: "Delivery"
2. Fill delivery address and notes
3. Create another order with Order Type: "Pickup"
4. View both order details

**Expected Results:**
- ✅ Delivery order shows delivery fields
- ✅ Pickup order hides/doesn't show delivery section
- ✅ Order type badge displayed correctly
- ✅ Conditional fields work in form

---

### Test 18: Validation - Required Fields

**Steps:**
1. Click "+ Create Order"
2. Leave customer empty
3. Don't add any items
4. Click "Create Order"

**Expected Results:**
- ✅ Error: "Customer is required"
- ✅ Error: "Add at least one item"
- ✅ Form doesn't submit
- ✅ Error messages clear and helpful

---

### Test 19: Validation - Line Item Fields

**Steps:**
1. Create order
2. Add item but leave product empty
3. Set quantity to 0
4. Try to save

**Expected Results:**
- ✅ Error: "Product required"
- ✅ Error: "Valid quantity required"
- ✅ Error: "Valid price required"
- ✅ Each item validates independently

---

### Test 20: Negative Profit Warning

**Steps:**
1. Create order
2. Add item: Masala Bajji (low margin: 1.8%)
3. Manually override unit_price to ₹50 (below cost of ₹58.90)
4. Observe sidebar

**Expected Results:**
- ✅ Line profit shows negative: -₹8.90
- ✅ Line profit in red color
- ✅ Order total profit negative
- ✅ Warning box: "⚠️ Warning: Negative profit!"
- ✅ Can still save (system allows but warns)

---

### Test 21: Order Statistics

**Steps:**
1. Create 5 orders with various statuses and amounts
2. Observe stats cards at top of Orders page

**Expected Results:**
- ✅ Total Orders count correct
- ✅ Total Revenue sum correct
- ✅ Total Profit sum correct
- ✅ Stats update after creating/editing orders

---

### Test 22: Mobile Responsiveness

**Steps:**
1. Open DevTools (F12)
2. Toggle device toolbar
3. Set to iPhone SE
4. Navigate through Orders pages

**Expected Results:**
- ✅ Orders table scrolls horizontally on mobile
- ✅ Order form stacks vertically
- ✅ Summary sidebar moves below form
- ✅ All buttons accessible
- ✅ No layout breaks

---

### Test 23: Cook Cannot Access Orders

**Steps:**
1. Logout
2. Login as cook: `cook / cook123`
3. Observe sidebar
4. Try to access: http://localhost:3000/orders

**Expected Results:**
- ✅ "🥘 Orders" link NOT visible for cook
- ✅ Direct URL shows "Access Denied"
- ✅ Only Operator and Admin can access orders

---

### Test 24: Empty State Handling

**Steps:**
1. Fresh database with no orders
2. Go to Orders page

**Expected Results:**
- ✅ Shows empty state icon and message
- ✅ "No orders found" message
- ✅ "Get started by creating your first order" text
- ✅ Shows "+ Create First Order" button
- ✅ No errors or broken UI

---

### Test 25: Date Handling in Import

**Steps:**
1. Create CSV with various date formats:
   - 2026-03-23
   - 23/03/2026
2. Import and verify

**Expected Results:**
- ✅ YYYY-MM-DD format parsed correctly
- ✅ DD/MM/YYYY format parsed correctly
- ✅ Both create orders with correct dates
- ✅ Flexible date parsing works

---

### Test 26: Order Item Display Order

**Steps:**
1. Create order with 3 items in specific order:
   - Soup, Bajji, Pickle
2. View order detail
3. Verify item order

**Expected Results:**
- ✅ Items display in order added
- ✅ display_order field preserved
- ✅ Order doesn't change after edit

---

### Test 27: Multiple Orders Same Customer

**Steps:**
1. Create 3 different orders for same customer
2. View orders list
3. View each order detail

**Expected Results:**
- ✅ All 3 orders created separately
- ✅ Each has unique order number
- ✅ All link to same customer
- ✅ Customer details correct in each

---

### Test 28: Long Order Notes

**Steps:**
1. Create order
2. Add very long text in notes field (500+ characters)
3. Save order
4. View detail

**Expected Results:**
- ✅ Long notes accepted
- ✅ Text wraps correctly
- ✅ No layout breaks
- ✅ Notes display in full on detail page

---

## 🎯 Exit Criteria - All Must Pass

Before moving to Step 7, verify ALL of these are TRUE:

### Order Creation
- [ ] Can create order with single item
- [ ] Can create order with multiple items
- [ ] Customer selection works
- [ ] Product selection from catalog works
- [ ] unit_price auto-fills from product
- [ ] unit_cost_snapshot auto-fills from product
- [ ] Manual price override works
- [ ] Delivery vs pickup type works

### Calculations
- [ ] Line total = quantity × unit_price (verified manually)
- [ ] Line cost = quantity × unit_cost_snapshot (verified manually)
- [ ] Line profit = line_total - line_cost (verified manually)
- [ ] Order total revenue sum correct
- [ ] Order total cost sum correct
- [ ] Order total profit correct
- [ ] Margin percentage accurate
- [ ] Negative profit detected and warned

### Cost Snapshots (CRITICAL)
- [ ] unit_cost_snapshot captured at order creation
- [ ] Snapshot immutable after order saved
- [ ] Product cost changes don't affect old orders
- [ ] New orders use current product cost
- [ ] Historical profit tracking accurate

### Order Management
- [ ] Can view order detail
- [ ] Can edit existing order
- [ ] Can change order status (7 statuses)
- [ ] Can change payment status (4 statuses)
- [ ] Order number auto-generated correctly
- [ ] Daily sequence increments properly

### Search & Filters
- [ ] Search by order number works
- [ ] Search by customer name works
- [ ] Search by customer mobile works
- [ ] Filter by status works
- [ ] Filter by payment status works
- [ ] Stats display correctly

### Google Sheets Import
- [ ] CSV upload works
- [ ] Template format correct
- [ ] Orders import successfully
- [ ] Customers matched correctly
- [ ] Products matched correctly
- [ ] Cost snapshots captured on import
- [ ] Order grouping works (same customer+date)
- [ ] Error handling works
- [ ] Invalid rows skipped gracefully
- [ ] Import results clear

### Validation
- [ ] Required fields enforced
- [ ] Quantity > 0 required
- [ ] Price > 0 required
- [ ] At least one item required
- [ ] Error messages helpful

### UI/UX
- [ ] Orders list displays correctly
- [ ] Order form intuitive
- [ ] Order detail comprehensive
- [ ] Real-time calculations work
- [ ] Status badges color-coded
- [ ] Responsive on mobile
- [ ] Empty states handled

### Role-Based Access
- [ ] Operator can access orders
- [ ] Admin can access orders
- [ ] Cook CANNOT access orders

---

## 📸 Screenshot Checklist

Take screenshots of:
1. Orders list with multiple orders
2. Order create form with line items
3. Order summary sidebar with calculations
4. Order detail page with items table
5. Status management buttons
6. Import CSV section
7. Import success message
8. Order with negative profit warning
9. Mobile view of orders
10. Access denied for cook role

---

## 🔧 Troubleshooting

### Orders not creating
```bash
# Check migrations
python manage.py migrate orders

# Check for errors
python manage.py shell
>>> from orders.models import Order
>>> Order.objects.count()
```

### Import failing
- Verify CSV encoding is UTF-8
- Check column headers match exactly
- Ensure customers exist in system
- Verify product names match catalog
- Test with sample template first

### Calculations wrong
- Verify product has cost components
- Check unit_cost_snapshot was captured
- Manually verify with calculator
- Check backend API response

### Cost snapshots not working
- Verify unit_cost_snapshot field has value
- Check OrderItem model save logic
- Ensure product.unit_cost is available

---

## 🧮 Manual Calculation Examples

### Example 1: Single Item Order
```
Product: Cream of Tomato Soup (250ml)
Unit Price: ₹80.00
Unit Cost: ₹52.60
Quantity: 2

Line Total = 2 × 80.00 = ₹160.00
Line Cost = 2 × 52.60 = ₹105.20
Line Profit = 160.00 - 105.20 = ₹54.80
Line Margin = (54.80 / 160.00) × 100 = 34.25% ≈ 34.2%
```

### Example 2: Multi-Item Order
```
Item 1: Tomato Soup × 2 = ₹160.00 revenue, ₹105.20 cost
Item 2: Bajji × 1 = ₹60.00 revenue, ₹58.90 cost
Item 3: Pickle × 1 = ₹120.00 revenue, ₹70.20 cost

Total Revenue = 160 + 60 + 120 = ₹340.00
Total Cost = 105.20 + 58.90 + 70.20 = ₹234.30
Total Profit = 340 - 234.30 = ₹105.70
Margin = (105.70 / 340) × 100 = 31.1%
```

Verify these match what the system shows!

---

## ✅ Sign-Off

Once ALL tests pass and exit criteria are met, Step 6 is complete.

**Validated by:** _________________  
**Date:** _________________  
**Cost Snapshots Verified:** ☐ YES  ☐ NO  
**Import Tested:** ☐ YES  ☐ NO  
**Calculations Accurate:** ☐ YES  ☐ NO  
**Ready for Step 7:** ☐ YES  ☐ NO

---

## 🚨 CRITICAL: Cost Snapshots Must Work

The `unit_cost_snapshot` feature is CRITICAL for accurate profit tracking. Do not move forward if:
- Snapshots not captured at order time
- Old orders affected by product cost changes
- Historical profits incorrect

**This is the foundation of profitability analysis!**

---

## 🚀 Next: Step 7 - Payments

Once validated, proceed to payment tracking and reconciliation.
