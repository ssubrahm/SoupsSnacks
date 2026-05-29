# Step 3 - Customer Management - Validation Guide

## ✅ Acceptance Checklist

Follow these steps to validate that Step 3 is complete and working correctly.

### Prerequisites

1. **Pull latest code and setup:**
   ```bash
   cd /Users/Srinath.Subrahmanyan/SoupsSnacks
   git pull origin main
   source SSCo/bin/activate
   python manage.py migrate
   python manage.py create_sample_customers
   ```

2. **Start servers:**
   ```bash
   ./setup.sh
   ```

3. **Login as admin or operator:**
   - Open http://localhost:3000
   - Login with: `admin / admin123` or `operator / operator123`
   - Navigate to "👥 Customers" in sidebar

---

## 🧪 Manual Validation Tests

### Test 1: Customer List Loads Correctly

**Steps:**
1. Click "👥 Customers" in the sidebar
2. Observe the page

**Expected Results:**
- ✅ Page loads without errors
- ✅ Statistics cards show:
  - Total Customers: 10
  - Active: 9
  - Inactive: 1
- ✅ Table shows 10 sample customers
- ✅ Each row shows: Name, Mobile, Email, Status, Added Date, Actions
- ✅ Status badges are color-coded (green for Active, gray for Inactive)

---

### Test 2: Create New Customer

**Steps:**
1. Click "+ Add Customer" button
2. Fill in the form:
   - Name: `Test Customer`
   - Mobile: `+919999999999`
   - Email: `test@example.com`
   - Address: `123 Test Street, Bangalore`
   - Notes: `Test notes`
   - Keep "Active customer" checked
3. Click "Create Customer"

**Expected Results:**
- ✅ Redirected to customer list
- ✅ New customer appears in the list
- ✅ Total count increases to 11
- ✅ Active count increases to 10

---

### Test 3: Form Validation - Required Fields

**Steps:**
1. Click "+ Add Customer"
2. Leave Name empty
3. Enter Mobile: `123` (invalid)
4. Click "Create Customer"

**Expected Results:**
- ✅ Form does NOT submit
- ✅ Error shown: "Name is required"
- ✅ Error shown: "Please enter a valid mobile number (9-15 digits)"
- ✅ Form fields highlighted in red

---

### Test 4: Form Validation - Email Format

**Steps:**
1. Click "+ Add Customer"
2. Fill Name: `Test`
3. Fill Mobile: `9876543210`
4. Fill Email: `invalid-email`
5. Click "Create Customer"

**Expected Results:**
- ✅ Form does NOT submit
- ✅ Error shown: "Please enter a valid email address"

---

### Test 5: Edit Customer

**Steps:**
1. From customer list, click "✏️" (edit icon) for "Priya Sharma"
2. Change name to: `Priya Sharma Updated`
3. Change notes to: `Updated notes`
4. Click "Update Customer"

**Expected Results:**
- ✅ Redirected to customer list
- ✅ Name shows as "Priya Sharma Updated"
- ✅ Changes persist after page refresh

---

### Test 6: Customer Detail Page

**Steps:**
1. From customer list, click on customer name "Rajesh Kumar"
2. Observe the detail page

**Expected Results:**
- ✅ Page shows customer's full information:
  - Name: Rajesh Kumar
  - Mobile: +919876543211 (clickable phone link)
  - Email: rajesh.kumar@example.com (clickable mailto link)
  - Address: Full address displayed
  - Notes: Customer notes displayed
  - Customer Since: Date displayed
  - Last Updated: Date displayed
- ✅ Status badge shows "Active" or "Inactive"
- ✅ Action buttons visible: Edit, Activate/Deactivate, Back

---

### Test 7: Search by Name

**Steps:**
1. Go to Customers list
2. In search box, type: `Priya`
3. Observe results

**Expected Results:**
- ✅ Only customers with "Priya" in name are shown
- ✅ Search is case-insensitive
- ✅ Clicking "✕" clears search and shows all customers

**Test Partial Search:**
4. Type: `sha` in search box

**Expected Results:**
- ✅ Shows "Priya Sharma" (matches "Sharma")

---

### Test 8: Search by Mobile

**Steps:**
1. Clear any existing search
2. Type in search box: `543210`
3. Observe results

**Expected Results:**
- ✅ Shows customer with mobile ending in 543210
- ✅ Partial mobile number search works

**Test Full Mobile:**
4. Type: `+919876543211`

**Expected Results:**
- ✅ Shows exact match for Rajesh Kumar

---

### Test 9: Search by Email

**Steps:**
1. Clear search
2. Type: `priya.sharma`
3. Observe results

**Expected Results:**
- ✅ Shows Priya Sharma
- ✅ Email search works with partial matches

---

### Test 10: Filter by Status

**Steps:**
1. Clear search
2. Click "Active" filter button

**Expected Results:**
- ✅ Only active customers shown (9 customers)
- ✅ "Active" button highlighted

**Test Inactive Filter:**
3. Click "Inactive" filter button

**Expected Results:**
- ✅ Only inactive customer shown (Vikram Singh)
- ✅ "Inactive" button highlighted

**Test All Filter:**
4. Click "All" filter button

**Expected Results:**
- ✅ All 10 customers shown
- ✅ "All" button highlighted

---

### Test 11: Toggle Active/Inactive Status

**From List Page:**
1. Find "Lakshmi Venkatesh" (should be Active)
2. Click "🔒" icon
3. Observe changes

**Expected Results:**
- ✅ Status badge changes to "Inactive"
- ✅ Stats update: Active count decreases
- ✅ Icon changes to "🔓"

**From Detail Page:**
4. Click on "Lakshmi Venkatesh" name to open detail
5. Click "🔓 Activate" button

**Expected Results:**
- ✅ Status changes back to "Active"
- ✅ Button text changes to "🔒 Deactivate"

---

### Test 12: Mobile Responsiveness

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (mobile view)
3. Set to iPhone SE or similar small screen
4. Navigate through:
   - Customer list
   - Create customer form
   - Customer detail page

**Expected Results:**
- ✅ Customer list table adapts for mobile (some columns hidden)
- ✅ Statistics cards stack vertically
- ✅ Search and filter buttons stack properly
- ✅ Form fields stack vertically on mobile
- ✅ Action buttons become full-width
- ✅ All features remain functional

---

### Test 13: Empty State

**Steps:**
1. In search box, type: `nonexistentcustomer`
2. Observe the display

**Expected Results:**
- ✅ Shows empty state icon 👥
- ✅ Message: "No customers found"
- ✅ Hint: "Try adjusting your search terms"

---

### Test 14: Navigation Flow

**Steps:**
1. From Customers list → Click "+ Add Customer"
2. Click "Cancel" button

**Expected Results:**
- ✅ Returns to customer list

**Test Edit Flow:**
3. Edit any customer
4. Click "← Back to List"

**Expected Results:**
- ✅ Returns to customer list without saving

**Test Detail Flow:**
5. View customer detail
6. Click "← Back"

**Expected Results:**
- ✅ Returns to customer list

---

### Test 15: Cook Role Cannot Access

**Steps:**
1. Logout
2. Login as cook: `cook / cook123`
3. Try to access: http://localhost:3000/customers

**Expected Results:**
- ✅ Shows "Access Denied" page
- ✅ Message indicates insufficient permissions
- ✅ Customers link NOT visible in sidebar for cook

---

## 🎯 Exit Criteria - All Must Pass

Before moving to Step 4, verify ALL of these are TRUE:

### CRUD Operations
- [ ] Can create new customer with all fields
- [ ] Can edit existing customer
- [ ] Can view customer detail page
- [ ] Changes persist across page reloads
- [ ] Can toggle active/inactive status

### Validation
- [ ] Required fields (name, mobile) are enforced
- [ ] Invalid mobile numbers are rejected
- [ ] Invalid email format is rejected
- [ ] Error messages are clear and helpful
- [ ] Form highlights invalid fields

### Search & Filter
- [ ] Search by name works (partial match)
- [ ] Search by mobile works (partial match)
- [ ] Search by email works
- [ ] Search is case-insensitive
- [ ] Can clear search
- [ ] Filter by All/Active/Inactive works
- [ ] Statistics update correctly

### UI/UX
- [ ] List page loads quickly with all data
- [ ] Statistics cards show correct counts
- [ ] Table is readable and organized
- [ ] Empty states are friendly
- [ ] Loading indicators appear during API calls
- [ ] Error messages are displayed when API fails

### Responsive Design
- [ ] Desktop view (1920x1080) works perfectly
- [ ] Tablet view (768x1024) adapts correctly
- [ ] Mobile view (375x667) is usable
- [ ] Touch interactions work on mobile
- [ ] No horizontal scrolling on small screens

### Role-Based Access
- [ ] Admin can access customers
- [ ] Operator can access customers
- [ ] Cook CANNOT access customers
- [ ] Unauthenticated users redirected to login

---

## 📸 Screenshot Checklist

Take screenshots of:
1. Customer list with statistics
2. Customer create form
3. Customer detail page
4. Search results
5. Mobile view of customer list
6. Validation errors on form
7. Empty state when no results

---

## 🔧 Troubleshooting

### No customers showing
```bash
python manage.py create_sample_customers
```

### Migration errors
```bash
python manage.py migrate
```

### API errors (403/401)
- Make sure you're logged in as admin or operator
- Clear browser cache and login again
- Check Django server is running

### Search not working
- Check browser console for JavaScript errors
- Verify API endpoint: http://localhost:8000/api/customers/?search=test
- Restart both servers

---

## 📊 Test Data Summary

Sample customers created:
1. Priya Sharma - Active
2. Rajesh Kumar - Active  
3. Lakshmi Venkatesh - Active
4. Arjun Reddy - Active
5. Meera Iyer - Active (no email)
6. Suresh Patel - Active (no address)
7. Divya Nair - Active
8. Vikram Singh - **Inactive**
9. Ananya Krishnan - Active
10. Karthik Ramesh - Active

Phone numbers: +919876543210 to +919876543219

---

## ✅ Sign-Off

Once ALL tests pass and exit criteria are met, Step 3 is complete.

**Validated by:** _________________  
**Date:** _________________  
**Ready for Step 4:** ☐ YES  ☐ NO

---

## 🚀 Next: Step 4 - Catalog and Costing

Once validated, proceed to menu/product catalog with ingredient costing.
