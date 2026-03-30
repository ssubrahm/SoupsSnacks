# Soups, Snacks & More 🍲

A modern order management system for home food businesses, built with Django and React.

## Features

- **Customer Management** - Track customers with Bangalore apartment/block filters
- **Product Catalog** - Products with detailed cost breakdown and profit margins
- **Daily Offerings** - Manage daily menus with WhatsApp/Email export
- **Order Management** - Full order lifecycle with status tracking
- **Payment Tracking** - Multiple payment methods with automatic status updates
- **Business Reports** - Sales, profitability, customer analytics
- **Google Forms Integration** - Import orders from Google Forms/Sheets
- **CSV/Excel Import** - Bulk import customers, products, orders, payments
- **Role-based Access** - Admin, Operator, Cook roles with different permissions
- **Day/Night Mode** - Indian-inspired warm color palette

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/ssubrahm/SoupsSnacks.git
cd SoupsSnacks

# Create and activate virtual environment
python -m venv SSCo
source SSCo/bin/activate  # On Windows: SSCo\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Run migrations
python manage.py migrate

# Create initial admin user
python manage.py createsuperuser

# Start the application
./setup.sh
```

### Seed Demo Data (Optional)

```bash
# Seed demo data for testing
python seed_demo_data.py

# Reset and reseed
python seed_demo_data.py --reset
```

This creates:
- 3 users (admin/operator/cook)
- 30 customers with Bangalore apartments
- 12 products with cost components
- 50 orders with items and payments
- 10 daily offerings

**Demo Credentials:**
- Admin: `admin` / `admin123`
- Operator: `operator` / `operator123`
- Cook: `cook` / `cook123`

## Usage

### Starting the Application

```bash
./setup.sh
```

This starts:
- Django backend on http://localhost:8000
- React frontend on http://localhost:3000

### Manual Start

```bash
# Terminal 1 - Backend
source SSCo/bin/activate
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm start
```

## Project Structure

```
SoupsSnacks/
├── backend/
│   ├── soupssnacks/       # Django settings
│   ├── users/             # User management
│   ├── customers/         # Customer CRUD
│   ├── catalog/           # Products & cost components
│   ├── offerings/         # Daily offerings
│   ├── orders/            # Orders & order items
│   ├── payments/          # Payment tracking
│   ├── reports/           # Dashboard & reports
│   ├── imports/           # CSV/Excel import
│   └── integrations/      # Google Sheets integration
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   ├── services/      # API services
│   │   └── styles/        # Global styles
│   └── public/
├── seed_demo_data.py      # Demo data script
├── setup.sh               # Start script
└── requirements.txt       # Python dependencies
```

## User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all features including user management, imports, and Google Sync |
| **Operator** | Customers, orders, payments, reports, analytics |
| **Cook** | Product catalog (menu items), dashboard view |

## Features Guide

### Customer Management

- Add customers with name, mobile, email
- Filter by apartment and block
- Track active/inactive status
- View order history per customer

### Product Catalog

- Categories: Soups, Snacks, Sweets, Lunch, Dinner, Pickle, Combos
- Cost components: Ingredients, Packaging, Labor, Overhead
- Auto-calculated: Unit Cost, Profit, Margin %
- Product images with category-specific placeholders

### Order Management

- Order statuses: Draft → Confirmed → Preparing → Ready → Delivered → Completed
- Payment statuses: Pending → Partial → Paid
- Order number format: ORD-YYYYMMDD-XXXX
- Cost snapshot preserves historical costs for reporting

### Payment Tracking

- Methods: UPI, Cash, Bank Transfer, Card, Other
- Automatic payment status updates
- Overpayment validation
- Quick filters for unpaid/partial/paid orders

### Daily Offerings

- Select products to offer each day
- Set optional quantity limits
- Export formatted text for WhatsApp/Email sharing

### Reports & Analytics

- Dashboard with KPIs and trends
- Sales reports by period
- Product performance analysis
- Customer analytics with segmentation
- Profitability reports
- CSV export for all reports

### Google Forms Integration

1. Create a Google Form for orders
2. Link to Google Sheets
3. Set up Google Cloud Service Account
4. Share sheet with service account email
5. Configure mapping in the app
6. Click "Sync Now" to import orders

See `GOOGLE_FORMS_SETUP.md` for detailed instructions.

### CSV/Excel Import

Import templates available for:
- Customers
- Products
- Orders
- Payments

## API Endpoints

### Authentication
- `POST /api/users/login/` - Login
- `POST /api/users/logout/` - Logout
- `GET /api/users/me/` - Current user

### Customers
- `GET/POST /api/customers/customers/` - List/Create
- `GET/PUT/DELETE /api/customers/customers/{id}/` - Detail

### Products
- `GET/POST /api/catalog/products/` - List/Create
- `GET/PUT/DELETE /api/catalog/products/{id}/` - Detail

### Orders
- `GET/POST /api/orders/orders/` - List/Create
- `GET/PUT/DELETE /api/orders/orders/{id}/` - Detail

### Payments
- `GET/POST /api/payments/payments/` - List/Create
- `GET/DELETE /api/payments/payments/{id}/` - Detail

### Reports
- `GET /api/reports/dashboard/` - Dashboard KPIs
- `GET /api/reports/sales/` - Sales report
- `GET /api/reports/customers/` - Customer report
- `GET /api/reports/products/` - Product report

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# For Google Sheets integration
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

Or place `google_credentials.json` file in project root.

### CORS Settings

For production, update `CORS_ALLOWED_ORIGINS` in `soupssnacks/settings.py`.

## Deployment

### Production Checklist

1. Set `DEBUG=False`
2. Generate new `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up proper database (PostgreSQL recommended)
5. Configure static file serving
6. Set up HTTPS
7. Build React frontend: `cd frontend && npm run build`
8. Collect static files: `python manage.py collectstatic`

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test orders.tests
```

### Code Style

- Python: Follow PEP 8
- JavaScript: ESLint with React rules
- CSS: BEM-like naming convention

## Troubleshooting

### Common Issues

**CSRF Error on Login**
- Ensure `CSRF_TRUSTED_ORIGINS` includes your frontend URL
- Check that `withCredentials: true` is set in axios

**Google Sheets Connection Failed**
- Verify `google_credentials.json` exists
- Check sheet is shared with service account email
- Ensure Google Sheets API is enabled

**Products/Orders Not Loading**
- Check Django server is running
- Verify API endpoint paths match
- Check browser console for errors

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.

---

Made with ❤️ for home food businesses in Bangalore
