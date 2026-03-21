# Soups, Snacks, and More - Order Management System

A web application for managing a home food business specializing in soups, Indian snacks, sweets, and small meal orders.

## Tech Stack

### Backend
- Django 5.2.12
- Django REST Framework 3.17.0
- SQLite Database
- Python 3.10+

### Frontend
- React 18
- React Router DOM
- Axios for API calls
- CSS3 with responsive design

## Project Structure

```
SoupsSnacks/
├── backend (Django apps)
│   ├── accounts/          # User accounts and authentication
│   ├── customers/         # Customer management
│   ├── catalog/           # Products and menu management
│   ├── orders/            # Order processing
│   ├── payments/          # Payment tracking
│   ├── reports/           # Analytics and reporting
│   ├── imports/           # Data import utilities
│   └── integrations/      # External integrations
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   └── services/      # API service layer
└── soupssnacks/           # Django project settings
```

## Local Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Navigate to the project directory:**
   ```bash
   cd SoupsSnacks
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```

   The backend API will be available at `http://localhost:8000/`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000/`

## Validation Steps

### Test Backend
1. Check API health endpoint:
   ```bash
   curl http://localhost:8000/api/health/
   ```
   Expected response: `{"status": "healthy", "message": "Soups, Snacks, and More API is running"}`

2. Access Django admin:
   - Navigate to `http://localhost:8000/admin/`
   - Login with superuser credentials

### Test Frontend
1. Navigate to `http://localhost:3000/`
2. Verify the layout renders with:
   - Header with app name
   - Sidebar navigation
   - Dashboard page
3. Confirm API connection shows "✓ Soups, Snacks, and More API is running"
4. Test sidebar menu items (currently show placeholder pages)

### Test Database
1. Check that SQLite database was created:
   ```bash
   ls -l db.sqlite3
   ```

2. Run test command:
   ```bash
   python manage.py seed_data
   ```
   Should show: "Seed command framework ready"

## Current Features (Step 1 - Foundation)
- ✅ Django backend with modular app structure
- ✅ Django REST Framework configured
- ✅ SQLite database
- ✅ CORS enabled for frontend-backend communication
- ✅ React frontend with routing
- ✅ Responsive layout with sidebar navigation
- ✅ API health check endpoint
- ✅ Seed command framework
- ✅ Environment-based configuration

## Next Steps
The application will be built incrementally following this sequence:
1. ✅ Project foundation (current)
2. Auth and roles
3. Customers
4. Catalog and costing
5. Daily offerings
6. Orders
7. Payments
8. Dashboard and reports
9. Customer loyalty analytics
10. Imports
11. Google Forms/Sheets integration
12. Polish and hardening

## Development Commands

### Django
```bash
python manage.py runserver              # Start server
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py createsuperuser        # Create admin user
python manage.py seed_data              # Seed database (placeholder)
```

### React
```bash
npm start                               # Start dev server
npm run build                           # Build for production
npm test                                # Run tests
```

## API Endpoints

Base URL: `http://localhost:8000/api/`

### Current Endpoints
- `GET /health/` - API health check

### Planned Endpoints (coming in future steps)
- `/accounts/` - Authentication and user management
- `/customers/` - Customer CRUD operations
- `/catalog/` - Product and menu management
- `/orders/` - Order management
- `/payments/` - Payment tracking
- `/reports/` - Analytics and reports
- `/imports/` - Data import
- `/integrations/` - External integrations

## License
Private project for Soups, Snacks, and More business.
