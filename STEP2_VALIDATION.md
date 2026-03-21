# Step 2 - Authentication & Roles - Validation Guide

## ✅ Acceptance Checklist

Follow these steps to validate that Step 2 is complete and working correctly.

### Prerequisites

1. **Pull latest code and start servers:**
   ```bash
   cd /Users/Srinath.Subrahmanyan/SoupsSnacks
   ./setup.sh
   ```

2. **Verify test users exist:**
   ```bash
   cd /Users/Srinath.Subrahmanyan/SoupsSnacks
   source SSCo/bin/activate
   python manage.py create_test_users
   ```

---

## 🧪 Manual Validation Tests

### Test 1: Admin Login & Access

**Steps:**
1. Open http://localhost:3000
2. You should be redirected to `/login`
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
4. Click "Sign In"

**Expected Results:**
- ✅ Login succeeds
- ✅ Redirected to Dashboard (/)
- ✅ Header shows: "Admin" name and "admin" role badge
- ✅ Sidebar shows ALL menu items:
  - 📊 Dashboard
  - 👥 Customers
  - 🥘 Orders
  - 🍛 Menu
  - 💰 Payments
  - 📈 Reports
  - 👤 Users

**Test User Management:**
5. Click "👤 Users" in sidebar
6. Verify you see the users table with 3 users
7. Click "+ Add User"
8. Create a new user:
   - Username: `test_operator`
   - Password: `test123`
   - Role: Operator
9. Click "Create User"

**Expected Results:**
- ✅ User created successfully
- ✅ New user appears in table
- ✅ Can activate/deactivate users

---

### Test 2: Invalid Login Rejection

**Steps:**
1. Logout (click "🚪 Logout" button)
2. Try to login with:
   - Username: `admin`
   - Password: `wrongpassword`

**Expected Results:**
- ✅ Login fails
- ✅ Error message displayed: "Invalid username or password"
- ✅ User stays on login page

---

### Test 3: Logout Functionality

**Steps:**
1. Login as admin (admin/admin123)
2. Click "🚪 Logout" button in header

**Expected Results:**
- ✅ User logged out
- ✅ Redirected to `/login` page
- ✅ Cannot access protected pages without logging in again

---

### Test 4: Current User API

**Steps:**
1. Login as admin
2. Open browser DevTools (F12)
3. Go to Console tab
4. Run: `fetch('/api/accounts/me/', {credentials: 'include'}).then(r => r.json()).then(console.log)`

**Expected Results:**
- ✅ Response contains user object:
  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@soupssnacks.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "is_active": true
  }
  ```

---

### Test 5: Operator Role - Limited Access

**Steps:**
1. Logout if logged in
2. Login with:
   - Username: `operator`
   - Password: `operator123`

**Expected Results:**
- ✅ Login succeeds
- ✅ Header shows "Operator" and "operator" role
- ✅ Sidebar shows ONLY:
  - 📊 Dashboard
  - 👥 Customers
  - 🥘 Orders
  - 💰 Payments
- ✅ Does NOT show:
  - 🍛 Menu (cook only)
  - 📈 Reports (admin only)
  - 👤 Users (admin only)

**Test Access Denial:**
3. Try to access admin page directly: http://localhost:3000/users

**Expected Results:**
- ✅ Shows "Access Denied" page
- ✅ Message: "You don't have permission to access this page"
- ✅ Shows: "Your role: operator"

---

### Test 6: Cook Role - Menu Access Only

**Steps:**
1. Logout if logged in
2. Login with:
   - Username: `cook`
   - Password: `cook123`

**Expected Results:**
- ✅ Login succeeds
- ✅ Header shows "Cook" and "cook" role
- ✅ Sidebar shows ONLY:
  - 📊 Dashboard
  - 🍛 Menu
- ✅ Does NOT show:
  - 👥 Customers
  - 🥘 Orders
  - 💰 Payments
  - 📈 Reports
  - 👤 Users

**Test Access Denial:**
3. Try to access: http://localhost:3000/customers

**Expected Results:**
- ✅ Shows "Access Denied" page
- ✅ Cannot access operator/admin pages

---

### Test 7: Protected API Endpoints

**Steps:**
1. Logout completely
2. Open browser DevTools Console
3. Try to access API without authentication:
   ```javascript
   fetch('http://localhost:8000/api/accounts/users/')
     .then(r => r.json())
     .then(console.log)
   ```

**Expected Results:**
- ✅ Request fails or returns authentication error
- ✅ 403 Forbidden or requires login

**As Operator:**
4. Login as operator
5. Try to access users API:
   ```javascript
   fetch('http://localhost:8000/api/accounts/users/', {credentials: 'include'})
     .then(r => r.json())
     .then(console.log)
   ```

**Expected Results:**
- ✅ Returns 403 Forbidden (operators can't manage users)

**As Admin:**
6. Login as admin
7. Try the same request

**Expected Results:**
- ✅ Returns list of users successfully

---

### Test 8: Browser Refresh - Auth State Persistence

**Steps:**
1. Login as any user
2. Navigate to Dashboard
3. Press F5 to refresh browser
4. Wait for page to reload

**Expected Results:**
- ✅ User stays logged in
- ✅ No redirect to login page
- ✅ User info still shows in header
- ✅ Role-based navigation preserved

---

### Test 9: Direct URL Access (Unauthenticated)

**Steps:**
1. Logout completely
2. Try to access: http://localhost:3000/

**Expected Results:**
- ✅ Redirected to `/login` page
- ✅ Cannot access dashboard without authentication

---

### Test 10: Role Hierarchy Validation

**Create test matrix:**

| Page        | Admin | Operator | Cook |
|-------------|-------|----------|------|
| Dashboard   | ✅    | ✅       | ✅   |
| Customers   | ✅    | ✅       | ❌   |
| Orders      | ✅    | ✅       | ❌   |
| Menu        | ✅    | ❌       | ✅   |
| Payments    | ✅    | ✅       | ❌   |
| Reports     | ✅    | ❌       | ❌   |
| Users       | ✅    | ❌       | ❌   |

**Steps:**
1. Test each role accessing each page
2. Verify the matrix above is correct

---

## 🎯 Exit Criteria - All Must Pass

Before moving to Step 3, verify ALL of these are TRUE:

### Authentication
- [ ] Admin can log in successfully
- [ ] Operator can log in successfully  
- [ ] Cook can log in successfully
- [ ] Invalid credentials are rejected with clear error
- [ ] Logout works and redirects to login
- [ ] Browser refresh maintains auth state

### API Endpoints
- [ ] `/api/accounts/login/` - works with valid credentials
- [ ] `/api/accounts/logout/` - works when authenticated
- [ ] `/api/accounts/me/` - returns current user data
- [ ] `/api/accounts/users/` - admin only (403 for others)
- [ ] Protected endpoints require authentication

### Frontend Guards
- [ ] Unauthenticated users redirected to login
- [ ] Login redirects to dashboard on success
- [ ] Role-based navigation changes correctly
- [ ] Access denied page shows for unauthorized access

### Role Permissions - UI
- [ ] Admin sees all 7 menu items
- [ ] Operator sees 4 menu items (no Menu, Reports, Users)
- [ ] Cook sees 2 menu items (only Dashboard, Menu)
- [ ] Menu visibility matches role exactly

### Role Permissions - Access
- [ ] Admin can access all pages
- [ ] Operator CANNOT access /users
- [ ] Operator CANNOT access /reports  
- [ ] Operator CANNOT access /catalog
- [ ] Cook CANNOT access /customers
- [ ] Cook CANNOT access /orders
- [ ] Cook CANNOT access /payments
- [ ] Cook CANNOT access /reports
- [ ] Cook CANNOT access /users

### User Management (Admin Only)
- [ ] Admin can view users list
- [ ] Admin can create new users
- [ ] Admin can activate/deactivate users
- [ ] Admin cannot deactivate themselves
- [ ] Non-admin users cannot access user management

---

## 📸 Visual Confirmation Screenshots

Take screenshots of:
1. Login page
2. Admin dashboard with full sidebar
3. Operator dashboard with limited sidebar
4. Cook dashboard with minimal sidebar
5. Access denied page (operator trying to access /users)
6. Users management page (admin view)

---

## 🔧 Troubleshooting

### Can't login
```bash
# Recreate test users
python manage.py create_test_users
```

### Database issues
```bash
# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
python manage.py create_test_users
```

### API not working
- Check Django server is running on port 8000
- Check browser console for CORS errors
- Verify CORS settings in settings.py

### Session issues
- Clear browser cookies
- Restart Django server
- Check SESSION_COOKIE_SAMESITE settings

---

## ✅ Sign-Off

Once ALL tests pass and exit criteria are met, Step 2 is complete.

**Validated by:** _________________  
**Date:** _________________  
**Ready for Step 3:** ☐ YES  ☐ NO

---

## 🚀 Next: Step 3 - Customers

Once validated, proceed to customer management implementation.
