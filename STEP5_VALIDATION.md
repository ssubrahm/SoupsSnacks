# Step 5 - Daily Offerings - Validation Guide

## ✅ Acceptance Checklist

Follow these steps to validate that Step 5 is complete and working correctly.

### Prerequisites

1. **Pull latest code and setup:**
   ```bash
   cd /Users/Srinath.Subrahmanyan/SoupsSnacks
   git pull origin main
   source SSCo/bin/activate
   python manage.py migrate
   python manage.py runserver
   ```

2. **In another terminal, start frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Login as operator or admin:**
   - Open http://localhost:3000
   - Login with: `operator / operator123` or `admin / admin123`
   - Navigate to "📅 Offerings" in sidebar

---

## 🧪 Manual Validation Tests

### Test 1: Daily Offerings Page Loads

**Steps:**
1. Click "📅 Offerings" in the sidebar
2. Observe the page

**Expected Results:**
- ✅ Page loads without errors
- ✅ Shows date selector with today's date pre-selected
- ✅ Shows stats cards: Total Offerings, Active, Inactive
- ✅ Shows "+ New offering" status (no offering exists for today yet)
- ✅ Shows "Select Products from Catalog" section
- ✅ Lists all active products from catalog (5 products if sample data loaded)

---

### Test 2: Create New Offering for Today

**Steps:**
1. Ensure today's date is selected
2. Add notes: `Fresh batch today! Order by 10 AM`
3. Select products:
   - Check "Cream of Tomato Soup (250ml)"
   - Check "Masala Bajji (6 pieces)"
   - Check "Upma (1 plate)"
4. For Tomato Soup, set Max Qty: `10`
5. Leave other quantities empty (unlimited)
6. Click "➕ Create Offering"

**Expected Results:**
- ✅ Offering created successfully
- ✅ Alert shows: "Offering saved successfully!"
- ✅ Date status changes to "✓ Offering exists"
- ✅ Button changes to "💾 Update Offering"
- ✅ "📥 Export for WhatsApp/Email" button appears
- ✅ Selected items summary shows 3 items
- ✅ Tomato Soup shows "Max: 10" tag

---

### Test 3: Edit Existing Offering

**Steps:**
1. With today's offering still selected
2. Uncheck "Upma"
3. Check "Mango Pickle (200g jar)"
4. Change Tomato Soup max qty to `15`
5. Update notes to: `Limited quantities today`
6. Click "💾 Update Offering"

**Expected Results:**
- ✅ Offering updated successfully
- ✅ Page reflects changes immediately
- ✅ Selected items now show: Tomato Soup, Bajji, Pickle (3 items)
- ✅ Tomato Soup max qty shows 15
- ✅ Notes updated

---

### Test 4: Create Offering for Tomorrow

**Steps:**
1. Change date selector to tomorrow's date
2. Observe page updates
3. Status should show "+ New offering"
4. Add note: `Weekend special menu`
5. Select products:
   - "Cream of Tomato Soup (500ml)" - Max Qty: 8
   - "Upma (1 plate)" - unlimited
   - "Mango Pickle (200g jar)" - Max Qty: 5
6. Click "➕ Create Offering"

**Expected Results:**
- ✅ Offering created for tomorrow
- ✅ Stats update: Total = 2
- ✅ Can switch between today and tomorrow
- ✅ Each date shows correct offering

---

### Test 5: Export Text File for WhatsApp/Email

**Steps:**
1. Select today's date (ensure offering exists)
2. Click "📥 Export for WhatsApp/Email" button
3. Save the downloaded file
4. Open the .txt file in notepad/text editor

**Expected Results:**
- ✅ File downloads as `menu_YYYYMMDD.txt`
- ✅ File contains formatted menu text
- ✅ Header shows: "🍛 MENU FOR [Day, Month DD, YYYY]"
- ✅ Notes appear below header
- ✅ Products grouped by category with emojis:
  - 🍲 SOUPS
  - 🥘 SNACKS
  - 🥒 PICKLES
- ✅ Each product shows: name, unit, price
- ✅ Limited items show: "[Limited: X available]"
- ✅ Footer includes ordering instructions
- ✅ Text is clean, readable, ready for copy-paste

**Example Expected Format:**
```
🍛 MENU FOR Saturday, March 22, 2026
==================================================

📝 Limited quantities today

🍲 SOUPS
--------------------------------------------------
• Cream of Tomato Soup (250ml) - ₹80.00 [Limited: 15 available]

🥘 SNACKS
--------------------------------------------------
• Masala Bajji (6 pieces) - ₹60.00

🥒 PICKLES
--------------------------------------------------
• Mango Pickle (200g jar) - ₹120.00

==================================================
📱 To order, reply with item names and quantities
🚚 Delivery available within Bangalore

Thank you! 🙏
```

---

### Test 6: Text Export Works for All Categories

**Steps:**
1. Create a new offering for a different date
2. Select at least one product from EACH category:
   - Soups, Snacks, Sweets, Lunch, Dinner, Pickle, Combos, Other
3. Save offering
4. Export text

**Expected Results:**
- ✅ Text file contains all 8 category sections
- ✅ Each category has correct emoji
- ✅ Categories appear in order: Soups, Snacks, Sweets, Lunch, Dinner, Pickle, Combos, Other
- ✅ Products grouped correctly under their categories

---

### Test 7: No Products Selected Validation

**Steps:**
1. Select a new date with no offering
2. Add notes but don't select any products
3. Click "➕ Create Offering"

**Expected Results:**
- ✅ Alert shows: "Please select at least one product"
- ✅ Offering NOT created
- ✅ Page remains in edit mode

---

### Test 8: Only Active Products Appear

**Steps:**
1. Go to "🍛 Menu" (Catalog)
2. Find a product and click 🔒 to deactivate it
3. Return to "📅 Offerings"
4. Create new offering for a different date

**Expected Results:**
- ✅ Deactivated product does NOT appear in selection list
- ✅ Only active products are selectable
- ✅ Previously selected inactive products (from old offerings) still display correctly when viewing those offerings

---

### Test 9: Quantity Limits Work Correctly

**Steps:**
1. Create offering with various quantity scenarios:
   - Product A: Max Qty = 5
   - Product B: Max Qty = 0 (should handle gracefully)
   - Product C: No max qty (unlimited)
   - Product D: Max Qty = 100
2. Save offering
3. View offering details
4. Export text

**Expected Results:**
- ✅ Product A shows "Max: 5" in UI
- ✅ Product B with qty=0 either rejected or shown as 0
- ✅ Product C shows no quantity indicator
- ✅ Product D shows "Max: 100"
- ✅ Text export correctly shows "[Limited: X available]" for products with limits
- ✅ Unlimited products don't show quantity note

---

### Test 10: Navigate Between Multiple Dates

**Steps:**
1. Create offerings for 5 different dates (today, tomorrow, next week, etc.)
2. Use date selector to switch between them
3. Observe page updates

**Expected Results:**
- ✅ Each date loads its specific offering instantly
- ✅ Date status updates correctly (exists vs new)
- ✅ Selected products update per date
- ✅ Notes update per date
- ✅ No lag or confusion between dates
- ✅ Export button only appears for existing offerings

---

### Test 11: Stats Update Correctly

**Steps:**
1. Note initial stats (Total, Active, Inactive)
2. Create a new offering
3. Observe stats update
4. Go to Admin panel (http://localhost:8000/admin)
5. Find a DailyOffering and mark it inactive
6. Return to offerings page
7. Refresh stats

**Expected Results:**
- ✅ Total increases when new offering created
- ✅ Active count reflects only active offerings
- ✅ Inactive count shows deactivated offerings
- ✅ Stats update after changes

---

### Test 12: Cook Cannot Access Offerings

**Steps:**
1. Logout
2. Login as cook: `cook / cook123`
3. Observe sidebar
4. Try to access: http://localhost:3000/offerings

**Expected Results:**
- ✅ "📅 Offerings" link NOT visible in sidebar for cook
- ✅ Direct URL access shows "Access Denied" page
- ✅ Only Operator and Admin can access offerings

---

### Test 13: Operator Can Access Offerings

**Steps:**
1. Logout
2. Login as operator: `operator / operator123`
3. Click "📅 Offerings"

**Expected Results:**
- ✅ "📅 Offerings" link visible in sidebar
- ✅ Can create offerings
- ✅ Can edit offerings
- ✅ Can export text
- ✅ Full access to all features

---

### Test 14: Admin Can Access Offerings

**Steps:**
1. Logout
2. Login as admin: `admin / admin123`
3. Click "📅 Offerings"

**Expected Results:**
- ✅ "📅 Offerings" link visible in sidebar
- ✅ Full access to all features
- ✅ Can manage offerings

---

### Test 15: Product Images Display (Bonus Feature)

**Steps:**
1. Go to API endpoint: http://localhost:8000/api/catalog/products/
2. Observe JSON response
3. Check for `display_image_url` field

**Expected Results:**
- ✅ Each product has `display_image_url` field
- ✅ If `image_url` is null, `display_image_url` shows Unsplash placeholder
- ✅ Placeholders are category-specific:
  - Soups: soup image
  - Snacks: snacks image
  - Sweets: dessert image
  - etc.
- ✅ URLs are valid (can open in browser)

---

### Test 16: Update Product Image URL

**Steps:**
1. Go to "🍛 Menu"
2. Edit "Cream of Tomato Soup (250ml)"
3. Add custom image URL (optional field):
   `https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400`
4. Save product
5. Check API response

**Expected Results:**
- ✅ `image_url` field stores custom URL
- ✅ `display_image_url` returns custom URL (not placeholder)
- ✅ If image_url cleared, `display_image_url` falls back to placeholder

---

### Test 17: Offerings Persist After Server Restart

**Steps:**
1. Create several offerings
2. Stop Django server (Ctrl+C)
3. Restart server: `python manage.py runserver`
4. Login and view offerings

**Expected Results:**
- ✅ All offerings still exist
- ✅ All data intact (dates, products, quantities, notes)
- ✅ Can still edit and export

---

### Test 18: Empty Catalog Handling

**Steps:**
1. Go to catalog and deactivate ALL products
2. Go to offerings page
3. Try to create offering

**Expected Results:**
- ✅ Shows message: "No active products in catalog. Add products first."
- ✅ Shows link: "+ Add Product"
- ✅ Cannot create offering without products
- ✅ Graceful handling, no errors

---

### Test 19: Date Selector Edge Cases

**Steps:**
1. Select a date far in the future (e.g., 1 year from now)
2. Create offering
3. Select a date in the past
4. Create offering

**Expected Results:**
- ✅ Future dates work fine
- ✅ Past dates work fine
- ✅ No date restrictions (system allows planning ahead or backfilling)
- ✅ Date format handled correctly

---

### Test 20: Mobile Responsive Design

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (mobile view)
3. Set to iPhone SE or similar
4. Navigate through offerings page

**Expected Results:**
- ✅ Date selector stacks vertically
- ✅ Product selection list readable
- ✅ Checkboxes touch-friendly
- ✅ Quantity inputs accessible
- ✅ Export button full-width
- ✅ No horizontal scrolling
- ✅ All features usable on mobile

---

### Test 21: Duplicate Product Prevention

**Steps:**
1. Create offering
2. Select "Tomato Soup (250ml)"
3. Try to select same product again (shouldn't be possible via UI)

**Expected Results:**
- ✅ Checkbox toggles (select/unselect)
- ✅ Cannot add same product twice
- ✅ Each product appears only once in offering

---

### Test 22: WhatsApp Copy-Paste Workflow

**Steps:**
1. Create offering with 4-5 products
2. Export text file
3. Open WhatsApp Web or app
4. Open the text file
5. Copy all content (Ctrl+A, Ctrl+C)
6. Paste into WhatsApp message box

**Expected Results:**
- ✅ Text pastes cleanly
- ✅ Emojis render correctly in WhatsApp
- ✅ Line breaks preserved
- ✅ Formatting looks good
- ✅ Ready to send as-is (no cleanup needed)

---

### Test 23: Email Copy-Paste Workflow

**Steps:**
1. Open exported text file
2. Copy content
3. Paste into Gmail/Outlook compose window

**Expected Results:**
- ✅ Text pastes as plain text
- ✅ Formatting preserved
- ✅ Emojis display correctly
- ✅ Professional appearance
- ✅ Ready to send

---

### Test 24: Google Forms Integration Workflow

**Steps:**
1. Create a Google Form for orders
2. Add description field in form
3. Copy exported text content
4. Paste into form description

**Expected Results:**
- ✅ Text displays in form description
- ✅ Menu shows nicely formatted
- ✅ Customers can see available items before filling form
- ✅ Practical for order collection

---

## 🎯 Exit Criteria - All Must Pass

Before moving to Step 6, verify ALL of these are TRUE:

### CRUD Operations
- [ ] Can create offering for any date
- [ ] Can edit existing offering
- [ ] Can view offerings by date
- [ ] Changes persist across page reloads
- [ ] Can create offerings for multiple dates

### Product Selection
- [ ] Only active products appear in selection list
- [ ] Can select/unselect products with checkboxes
- [ ] Selected products highlighted
- [ ] Summary shows all selected items
- [ ] Can select products from all 8 categories

### Quantity Limits
- [ ] Optional quantity field works
- [ ] Can leave quantity empty (unlimited)
- [ ] Quantity appears in UI correctly
- [ ] Quantity appears in text export
- [ ] Zero or negative quantities handled gracefully

### Text Export
- [ ] Export button appears only for saved offerings
- [ ] Downloads file with correct name format
- [ ] File contains formatted menu
- [ ] Products grouped by category
- [ ] Emojis display correctly
- [ ] Prices formatted correctly (₹XX.XX)
- [ ] Quantity limits shown where applicable
- [ ] Header and footer formatted nicely
- [ ] Ready for WhatsApp/Email/Google Forms

### Role-Based Access
- [ ] Operator can access offerings
- [ ] Admin can access offerings
- [ ] Cook CANNOT access offerings
- [ ] Unauthenticated redirected to login

### Data Integrity
- [ ] Multiple offerings can exist for different dates
- [ ] Each date has independent offering
- [ ] No date conflicts (unique per date)
- [ ] Data persists after server restart

### UI/UX
- [ ] Date selector intuitive
- [ ] Product selection easy to use
- [ ] Notes field works
- [ ] Stats update correctly
- [ ] Loading states shown
- [ ] Error messages clear
- [ ] Responsive on mobile

### Integration
- [ ] Uses products from catalog
- [ ] Inactive products excluded automatically
- [ ] Product details (name, unit, price) accurate
- [ ] Category grouping correct

---

## 📸 Screenshot Checklist

Take screenshots of:
1. Offerings page with date selector
2. Product selection with some items checked
3. Selected items summary with quantity limits
4. Exported text file content
5. WhatsApp with pasted menu
6. Mobile view of offerings page
7. Access denied for cook role
8. Multiple offerings for different dates

---

## 🔧 Troubleshooting

### No products showing in selection
```bash
python manage.py create_sample_products
# Ensure products are active in catalog
```

### Export button not appearing
- Save the offering first
- Offering must exist before export

### Migration errors
```bash
python manage.py migrate offerings
python manage.py migrate catalog
```

### Text export file not downloading
- Check browser pop-up blocker
- Check browser downloads folder
- Try different browser

### Date selector not working
- Clear browser cache
- Check browser console for errors
- Ensure date format is YYYY-MM-DD

---

## 📝 Real-World Usage Scenario

**Typical Daily Workflow for Operator:**

1. **Morning (8:00 AM):**
   - Login to app
   - Go to Offerings page
   - Select today's date
   - Review available products from catalog
   - Select items available today (based on ingredients)
   - Set quantity limits if needed (e.g., only 10 soups prepared)
   - Add notes (e.g., "Fresh batch, order by 11 AM")
   - Save offering

2. **Share with Customers (8:30 AM):**
   - Click "Export for WhatsApp/Email"
   - Open WhatsApp
   - Paste menu into broadcast message
   - Send to customer groups

3. **Mid-Day Updates (12:00 PM):**
   - If items selling out, edit offering
   - Update quantity limits (e.g., only 3 soups left)
   - Re-export and send update message

4. **Evening Planning (6:00 PM):**
   - Select tomorrow's date
   - Create offering for tomorrow
   - Export and schedule message for morning

---

## ✅ Sign-Off

Once ALL tests pass and exit criteria are met, Step 5 is complete.

**Validated by:** _________________  
**Date:** _________________  
**Text Export Works:** ☐ YES  ☐ NO  
**Ready for Step 6 (Orders):** ☐ YES  ☐ NO

---

## 🚨 CRITICAL: Text Export Must Be Perfect

The exported text is customer-facing. Ensure:
- Professional formatting
- No typos or errors
- Emojis appropriate
- Prices accurate
- Quantity limits clear
- Ready for immediate use

**This is a key feature for customer communication!**

---

## 🚀 Next: Step 6 - Orders

Once validated, proceed to order management where customers can place orders based on daily offerings.
