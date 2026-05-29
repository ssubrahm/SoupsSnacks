# Step 4 - Product Catalog & Cost Components - Validation Guide

## ✅ Acceptance Checklist

Follow these steps to validate that Step 4 is complete and working correctly.

### Prerequisites

1. **Pull latest code and setup:**
   ```bash
   cd /Users/Srinath.Subrahmanyan/SoupsSnacks
   git pull origin main
   source SSCo/bin/activate
   python manage.py migrate
   python manage.py create_sample_products
   ```

2. **Start servers:**
   ```bash
   ./setup.sh
   ```

3. **Login as cook or admin:**
   - Open http://localhost:3000
   - Login with: `cook / cook123` or `admin / admin123`
   - Navigate to "🍛 Menu" in sidebar

---

## 🧪 Manual Validation Tests

### Test 1: Product List Loads Correctly

**Steps:**
1. Click "🍛 Menu" in the sidebar
2. Observe the product catalog page

**Expected Results:**
- ✅ Page loads without errors
- ✅ Shows 5 sample products in card grid
- ✅ Each card displays:
  - Product name and unit
  - Category badge (colored)
  - Selling price, Cost, Profit, Margin %
  - Component count
  - Status badge (Active/Inactive)
  - Edit and toggle buttons
- ✅ Margin colors: Green (>30%), Yellow (15-30%), Orange (<15%)
- ✅ Stats cards show: Total: 5, Active: 5, Inactive: 0

**Verify Sample Products:**
- Cream of Tomato Soup (250ml) - Margin: 34.2% (green)
- Cream of Tomato Soup (500ml) - Margin: 37.0% (green)
- Masala Bajji (6 pieces) - Margin: 1.8% (orange/low)
- Upma (1 plate) - Margin: 21.5% (yellow)
- Mango Pickle (200g jar) - Margin: 41.5% (green)

---

### Test 2: Create New Product - Basic

**Steps:**
1. Click "+ Add Product" button
2. Fill in basic information:
   - Product Name: `Test Soup`
   - Unit/Size: `300ml`
   - Category: `soups`
   - Selling Price: `100.00`
   - Leave description optional
   - Keep "Active product" checked
3. **Do NOT add any cost components yet**
4. Click "Create Product"

**Expected Results:**
- ✅ Product created successfully
- ✅ Redirected to product list
- ✅ New product appears in list
- ✅ Shows: Cost: ₹0.00, Profit: ₹100.00, Margin: 100.0%
- ✅ Component count shows: 0 cost items

---

### Test 3: Add Cost Components to Product

**Steps:**
1. Click "Test Soup" from the list
2. Click "✏️ Edit" button
3. In Cost Components section, click "+ Add Cost Item"
4. Fill in first component:
   - Item Name: `Vegetables`
   - Type: `Ingredient`
   - Quantity: `0.100`
   - Unit: `kg`
   - Cost/Unit: `50.00`
   - Verify Total shows: ₹5.00
5. Click "+ Add Cost Item" again
6. Fill in second component:
   - Item Name: `Cooking Labor`
   - Type: `Labor`
   - Quantity: `0.150`
   - Unit: `hours`
   - Cost/Unit: `100.00`
   - Verify Total shows: ₹15.00
7. Add third component:
   - Item Name: `Gas`
   - Type: `Fuel`
   - Quantity: `1.000`
   - Unit: `batch`
   - Cost/Unit: `10.00`
   - Verify Total shows: ₹10.00
8. Observe the Cost Summary sidebar (sticky on right)
9. Click "Update Product"

**Expected Results - During Entry:**
- ✅ Cost Summary updates in real-time as you type
- ✅ Total Cost shows: ₹30.00 (5 + 15 + 10)
- ✅ Unit Profit shows: ₹70.00 (100 - 30)
- ✅ Margin shows: 70.0%

**Expected Results - After Save:**
- ✅ Redirected to product list
- ✅ Test Soup now shows:
  - Cost: ₹30.00
  - Profit: ₹70.00
  - Margin: 70.0%
  - 3 cost items

---

### Test 4: Manual Calculation Verification

**Steps:**
1. Open calculator app
2. Verify Test Soup calculations manually:
   - Vegetables: 0.100 × 50.00 = 5.00
   - Labor: 0.150 × 100.00 = 15.00
   - Gas: 1.000 × 10.00 = 10.00
   - Total Cost: 5 + 15 + 10 = 30.00
   - Profit: 100.00 - 30.00 = 70.00
   - Margin: (70 / 100) × 100 = 70.0%

**Expected Results:**
- ✅ All calculations match exactly
- ✅ No rounding errors
- ✅ Decimals display correctly (2 places for currency, 1 for percentage)

---

### Test 5: Edit Cost Component and Verify Totals Update

**Steps:**
1. Edit "Test Soup" again
2. Change the first component (Vegetables):
   - Quantity: Change from `0.100` to `0.200`
   - Observe sidebar
3. Verify new calculation:
   - Vegetables: 0.200 × 50.00 = 10.00
   - Total Cost: 10 + 15 + 10 = 35.00
   - Profit: 100 - 35 = 65.00
   - Margin: 65.0%
4. Click "Update Product"

**Expected Results:**
- ✅ Sidebar updates immediately when quantity changes
- ✅ New Total Cost: ₹35.00
- ✅ New Profit: ₹65.00
- ✅ New Margin: 65.0%
- ✅ After save, product list shows updated values

---

### Test 6: Remove Cost Component

**Steps:**
1. Edit "Test Soup"
2. Click "🗑️ Remove" on the Gas component
3. Observe sidebar updates
4. Verify calculation:
   - Vegetables: 0.200 × 50.00 = 10.00
   - Labor: 0.150 × 100.00 = 15.00
   - Total Cost: 10 + 15 = 25.00
   - Profit: 75.00
   - Margin: 75.0%
5. Save product

**Expected Results:**
- ✅ Gas component removed
- ✅ Sidebar recalculates immediately
- ✅ Total Cost: ₹25.00
- ✅ Component count: 2 cost items

---

### Test 7: Product Categories (Including Pickle & Other)

**Steps:**
1. Create new product:
   - Name: `Lemon Pickle`
   - Unit: `250g jar`
   - Category: `pickle`
   - Selling Price: `150.00`
2. Create another product:
   - Name: `Papad`
   - Unit: `100g pack`
   - Category: `other`
   - Selling Price: `40.00`
3. Go to product list
4. Use category filter dropdown

**Expected Results:**
- ✅ Category dropdown includes "Pickle" option
- ✅ Category dropdown includes "Other" option
- ✅ Can filter by Pickle - shows Lemon Pickle and Mango Pickle
- ✅ Can filter by Other - shows Papad
- ✅ Category badges show distinct colors for each category

---

### Test 8: Labor and Fuel Cost Components

**Steps:**
1. Review "Cream of Tomato Soup (250ml)" product
2. Click to view detail page
3. Examine cost breakdown

**Expected Results:**
- ✅ Labor component visible: "Cooking Labor" (0.100 hours @ ₹100/hour)
- ✅ Fuel component visible: "Gas/Fuel" (1.000 batch @ ₹8/batch)
- ✅ Cost breakdown grouped by type
- ✅ Ingredients section shows all ingredient items
- ✅ Labor section shows labor items
- ✅ Fuel section shows fuel items
- ✅ Each section has subtotal
- ✅ Grand total matches unit_cost

---

### Test 9: Unit Cost Calculation is Correct

**Steps:**
1. View "Cream of Tomato Soup (250ml)" detail page
2. Verify each cost component from the breakdown table
3. Manually calculate total with calculator

**Sample Calculation (from sample data):**
```
Tomatoes: 0.150 kg × ₹40.00 = ₹6.00
Cream: 0.030 L × ₹200.00 = ₹6.00
Onions: 0.020 kg × ₹30.00 = ₹0.60
Garlic: 0.005 kg × ₹100.00 = ₹0.50
Butter: 0.010 kg × ₹450.00 = ₹4.50
Spices: 1.000 batch × ₹5.00 = ₹5.00
Labor: 0.100 hours × ₹100.00 = ₹10.00
Gas: 1.000 batch × ₹8.00 = ₹8.00
Container: 1.000 piece × ₹12.00 = ₹12.00
─────────────────────────────────────
Total Cost: ₹52.60
```

**Expected Results:**
- ✅ Manual calculation matches displayed cost: ₹52.60
- ✅ Profit: ₹80.00 - ₹52.60 = ₹27.40
- ✅ Margin: (27.40 / 80.00) × 100 = 34.25% ≈ 34.2%

---

### Test 10: Unit Profit Calculation is Correct

**Steps:**
1. View "Masala Bajji (6 pieces)" detail page
2. Note Selling Price: ₹60.00
3. Note Total Cost from breakdown
4. Verify Profit calculation

**Expected Results:**
- ✅ Cost displayed: ₹58.90
- ✅ Profit: ₹60.00 - ₹58.90 = ₹1.10
- ✅ Profit displayed correctly as ₹1.10
- ✅ Profit is positive (green color)

---

### Test 11: Margin Percent Calculation is Correct

**Steps:**
1. View all 5 sample products
2. For each, verify margin calculation:
   - Margin % = (Profit / Selling Price) × 100

**Expected Results:**
| Product | Price | Cost | Profit | Margin | Verified |
|---------|-------|------|--------|--------|----------|
| Tomato Soup 250ml | ₹80.00 | ₹52.60 | ₹27.40 | 34.2% | ✅ |
| Tomato Soup 500ml | ₹140.00 | ₹88.20 | ₹51.80 | 37.0% | ✅ |
| Masala Bajji | ₹60.00 | ₹58.90 | ₹1.10 | 1.8% | ✅ |
| Upma | ₹50.00 | ₹39.25 | ₹10.75 | 21.5% | ✅ |
| Mango Pickle | ₹120.00 | ₹70.20 | ₹49.80 | 41.5% | ✅ |

- ✅ All margin percentages calculated correctly
- ✅ All match manual calculations

---

### Test 12: Product Detail Page Shows Cost Summary Clearly

**Steps:**
1. Click on any product from list
2. Observe the detail page layout

**Expected Results:**
- ✅ Page divided into clear sections:
  - Pricing Summary card (left)
  - Cost Breakdown card (right)
- ✅ Pricing Summary shows:
  - Selling Price (large, gold)
  - Total Cost (orange)
  - Unit Profit (green, large)
  - Profit Margin % (color-coded)
- ✅ Cost Breakdown shows:
  - Grouped by type (Ingredient, Labor, Fuel, etc.)
  - Table with columns: Item, Qty, Unit, Cost/Unit, Total
  - Subtotal per type
  - Grand total at bottom
- ✅ All values clearly labeled
- ✅ Easy to read and understand

---

### Test 13: Mark Product Inactive and Verify Behavior

**Steps:**
1. From product list, click "🔒" icon on "Test Soup"
2. Observe changes
3. Use status filter to select "Inactive"
4. Switch filter to "Active"

**Expected Results:**
- ✅ Status badge changes to "Inactive" (gray)
- ✅ Icon changes to "🔓"
- ✅ Stats update: Active count decreases, Inactive count increases
- ✅ Filter by Inactive shows Test Soup
- ✅ Filter by Active hides Test Soup
- ✅ Product still editable when inactive
- ✅ Can reactivate by clicking "🔓"

---

### Test 14: Invalid Required Fields Rejected Cleanly

**Steps:**
1. Click "+ Add Product"
2. Leave Name empty
3. Leave Unit empty
4. Enter Selling Price: `-10` (negative)
5. Click "Create Product"

**Expected Results:**
- ✅ Form does NOT submit
- ✅ Error shown: "Name is required"
- ✅ Error shown: "Unit is required"
- ✅ Error shown: "Selling price must be greater than 0"
- ✅ Fields highlighted in red
- ✅ Error messages clear and helpful

**Test Cost Component Validation:**
6. Fill valid name, unit, price
7. Add cost component
8. Leave Item Name empty
9. Enter Quantity: `0` (zero)
10. Click "Create Product"

**Expected Results:**
- ✅ Error: "Item name required"
- ✅ Error: "Valid quantity required"
- ✅ Cannot save with invalid cost components

---

### Test 15: Search Functionality

**Steps:**
1. Go to product list
2. Type "Tomato" in search box
3. Observe results

**Expected Results:**
- ✅ Shows both Tomato Soup products (250ml and 500ml)
- ✅ Search is case-insensitive
- ✅ Clear button (✕) appears
- ✅ Clicking ✕ clears search and shows all products

**Test Category Search:**
4. Type "pickle" in search
5. Observe results

**Expected Results:**
- ✅ Shows pickle category products
- ✅ Search includes category names

---

### Test 16: Filter by Category

**Steps:**
1. Clear any search
2. Select "Soups" from category dropdown
3. Observe results

**Expected Results:**
- ✅ Shows only soup products (2 items)
- ✅ Both Tomato Soup sizes displayed

**Test Multiple Categories:**
4. Change to "Snacks"

**Expected Results:**
- ✅ Shows Masala Bajji only

5. Change to "All Categories"

**Expected Results:**
- ✅ Shows all products again

---

### Test 17: Multiple Unit Sizes Support

**Steps:**
1. Observe that "Cream of Tomato Soup" exists in TWO sizes:
   - 250ml @ ₹80.00
   - 500ml @ ₹140.00
2. Verify they are separate products
3. Try to create duplicate:
   - Name: `Cream of Tomato Soup`
   - Unit: `250ml`
   - Price: `90.00`
4. Try to save

**Expected Results:**
- ✅ Both sizes show as separate products in list
- ✅ Each has different cost components
- ✅ Each calculates separately
- ✅ Attempting to create duplicate (same name + unit) should fail or warn
- ✅ Can create same product with different unit (e.g., 1 liter)

---

### Test 18: Negative Profit Warning

**Steps:**
1. Edit "Masala Bajji" (which has very low margin: 1.8%)
2. Change selling price to: `50.00` (below cost of ₹58.90)
3. Observe sidebar

**Expected Results:**
- ✅ Profit shows: ₹-8.90 (negative, red color)
- ✅ Margin shows negative percentage (red)
- ✅ Warning box appears: "⚠️ Warning: Negative profit! Cost exceeds selling price."
- ✅ Can still save (system allows, but warns)

4. Change price back to `60.00`
5. Observe warning disappears

**Expected Results:**
- ✅ Warning removed when profit becomes positive

---

### Test 19: Low Margin Information

**Steps:**
1. Edit a product with margin between 0% and 15%
2. Observe sidebar

**Expected Results:**
- ✅ Info box shows: "💡 Tip: Margin is below 15%. Consider adjusting costs or price."
- ✅ Margin value displayed in orange/yellow color
- ✅ Still allows saving

---

### Test 20: Product Detail Cost Breakdown Grouped Correctly

**Steps:**
1. View "Cream of Tomato Soup (250ml)" detail
2. Examine cost breakdown sections

**Expected Results:**
- ✅ Cost components grouped by type:
  - **ingredient** section with: Tomatoes, Cream, Onions, Garlic, Butter, Spices
  - **labor** section with: Cooking Labor
  - **fuel** section with: Gas/Fuel
  - **packaging** section with: Container
- ✅ Each section has subtotal
- ✅ Subtotals add up to grand total
- ✅ Grand total = Total Cost from pricing summary

---

### Test 21: Responsive Design - Mobile View

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (mobile view)
3. Set to iPhone SE or similar small screen
4. Navigate through:
   - Product list
   - Create/edit form
   - Product detail

**Expected Results:**
- ✅ Product grid becomes single column on mobile
- ✅ Form layout stacks vertically
- ✅ Cost summary sidebar moves below form
- ✅ Tables remain scrollable/readable
- ✅ All buttons remain accessible
- ✅ No horizontal scrolling
- ✅ Touch-friendly button sizes

---

### Test 22: Operator Cannot Access Catalog

**Steps:**
1. Logout
2. Login as operator: `operator / operator123`
3. Observe sidebar
4. Try to access: http://localhost:3000/catalog

**Expected Results:**
- ✅ "🍛 Menu" link NOT visible in sidebar for operator
- ✅ Direct URL access shows "Access Denied" page
- ✅ Message: insufficient permissions
- ✅ Only Cook and Admin can access catalog

---

### Test 23: Admin Can Access Catalog

**Steps:**
1. Logout
2. Login as admin: `admin / admin123`
3. Click "🍛 Menu" in sidebar

**Expected Results:**
- ✅ "🍛 Menu" link visible in sidebar
- ✅ Can view product list
- ✅ Can create/edit products
- ✅ Full access to all catalog features

---

### Test 24: Cook Can Access Catalog

**Steps:**
1. Logout  
2. Login as cook: `cook / cook123`
3. Click "🍛 Menu" in sidebar

**Expected Results:**
- ✅ "🍛 Menu" link visible in sidebar
- ✅ Can view product list
- ✅ Can create/edit products
- ✅ Full access to all catalog features

---

## 🎯 Exit Criteria - All Must Pass

Before moving to Step 5, verify ALL of these are TRUE:

### CRUD Operations
- [ ] Can create new product with all fields
- [ ] Can edit existing product
- [ ] Can view product detail page
- [ ] Can toggle active/inactive status
- [ ] Changes persist across page reloads

### Cost Components
- [ ] Can add cost components to product
- [ ] Can edit cost components
- [ ] Can remove cost components
- [ ] Supports all 6 component types (ingredient, labor, fuel, packaging, transport, misc)
- [ ] Each component calculates total correctly (quantity × cost_per_unit)

### Calculations
- [ ] unit_cost = sum of all cost components (verified manually)
- [ ] unit_profit = selling_price - unit_cost (verified manually)
- [ ] margin_percent = (unit_profit / selling_price) × 100 (verified manually)
- [ ] All calculations accurate to 2 decimal places
- [ ] Negative profit handled correctly

### Categories
- [ ] All 8 categories available (soups, snacks, sweets, lunch, dinner, pickle, combos, other)
- [ ] Pickle category works
- [ ] Other category works
- [ ] Can filter by category

### Validation
- [ ] Required fields enforced (name, unit, selling_price)
- [ ] Invalid prices rejected (≤ 0)
- [ ] Invalid cost component quantities rejected (≤ 0)
- [ ] Invalid cost_per_unit rejected (≤ 0)
- [ ] Error messages clear and helpful

### UI/UX
- [ ] Product list loads quickly
- [ ] Card layout shows all key information
- [ ] Create/edit form is intuitive
- [ ] Cost summary sidebar updates in real-time
- [ ] Product detail page shows clear cost breakdown
- [ ] Warnings/alerts display appropriately
- [ ] Responsive on mobile devices

### Search & Filter
- [ ] Search by name works
- [ ] Search by description works
- [ ] Filter by status (All/Active/Inactive)
- [ ] Filter by category
- [ ] Can clear search

### Role-Based Access
- [ ] Admin can access catalog
- [ ] Cook can access catalog
- [ ] Operator CANNOT access catalog
- [ ] Unauthenticated users redirected to login

### Multiple Unit Sizes
- [ ] Can create same product with different units
- [ ] Each size has independent costing
- [ ] Each size displays separately in list
- [ ] Unique constraint on (name, unit) enforced

---

## 📸 Screenshot Checklist

Take screenshots of:
1. Product list with 5+ products
2. Product card showing all pricing details
3. Create product form - basic info section
4. Create product form - cost components section
5. Cost summary sidebar with calculations
6. Product detail page - pricing summary
7. Product detail page - cost breakdown by type
8. Negative profit warning
9. Mobile view of product list
10. Access denied for operator role

---

## 🔧 Troubleshooting

### No products showing
```bash
python manage.py create_sample_products
```

### Migration errors
```bash
python manage.py migrate catalog
```

### Calculations seem wrong
- Check browser console for JavaScript errors
- Verify API returns correct data: http://localhost:8000/api/catalog/products/1/
- Clear browser cache
- Check that cost_per_unit and quantity are numbers, not strings

### Cannot access as cook
- Verify cook user exists: `python manage.py create_test_users`
- Clear browser cookies
- Login again

---

## 🧮 Manual Calculation Examples

### Example 1: Simple Product
```
Product: Test Soup
Selling Price: ₹100.00
Components:
  - Ingredient A: 2 × ₹10 = ₹20
  - Labor: 0.5 × ₹100 = ₹50
  - Fuel: 1 × ₹5 = ₹5
  
Total Cost: ₹20 + ₹50 + ₹5 = ₹75.00
Profit: ₹100 - ₹75 = ₹25.00
Margin: (₹25 / ₹100) × 100 = 25.0%
```

### Example 2: From Sample Data (Upma)
```
Product: Upma (1 plate)
Selling Price: ₹50.00
Components:
  - Rava: 0.080 kg × ₹50.00 = ₹4.00
  - Vegetables: 0.050 kg × ₹40.00 = ₹2.00
  - Oil: 0.015 L × ₹150.00 = ₹2.25
  - Spices: 1.000 batch × ₹5.00 = ₹5.00
  - Labor: 0.100 hours × ₹100.00 = ₹10.00
  - Gas: 1.000 batch × ₹6.00 = ₹6.00
  - Container: 1.000 piece × ₹10.00 = ₹10.00

Total Cost: ₹4.00 + ₹2.00 + ₹2.25 + ₹5.00 + ₹10.00 + ₹6.00 + ₹10.00 = ₹39.25
Profit: ₹50.00 - ₹39.25 = ₹10.75
Margin: (₹10.75 / ₹50.00) × 100 = 21.5%
```

Verify this matches what the system shows!

---

## ✅ Sign-Off

Once ALL tests pass and exit criteria are met, Step 4 is complete.

**Validated by:** _________________  
**Date:** _________________  
**Costing Accuracy Verified:** ☐ YES  ☐ NO  
**Ready for Step 5:** ☐ YES  ☐ NO

---

## 🚨 CRITICAL: Costing Must Be Accurate

This is the foundation for profitability tracking. Do not move forward if:
- Any calculation is incorrect
- Manual verification doesn't match system
- Margin percentages are wrong
- Cost components don't sum correctly

**This step is too important to skip validation!**

---

## 🚀 Next: Step 5 - Daily Offerings

Once validated, proceed to daily menu offerings where customers can select from available products and sizes.
