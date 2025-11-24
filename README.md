# Cloud Kitchen Management System

Django-based cloud kitchen management system with order tracking, expense management, referral system, and multi-gateway payment integration.

## Quick Start

1. Extract this ZIP file
2. Navigate to the project directory
3. Create virtual environment: `python3.12 -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Update `.env` file with your settings
7. Run migrations: `python manage.py migrate`
8. Create superuser: `python manage.py createsuperuser`
9. Run server: `python manage.py runserver`

## Docker Setup

```bash
docker-compose up --build
```

## Project Structure

- **accounts/** - User management and authentication
- **orders/** - Order processing and management
- **menu/** - Menu items and catalog
- **expenses/** - Expense tracking
- **locations/** - Address and building management
- **payments/** - Payment gateway abstraction
- **delivery/** - Delivery provider abstraction
- **referrals/** - Referral system
- **wallet/** - Coin wallet system
- **analytics/** - Charts and reports
- **backup/** - Backup strategies

## Features

✅ User authentication (Email/Phone verification)
✅ Menu management with active/inactive toggle
✅ Order placement with QR code generation
✅ Expense tracking
✅ Referral system with token generation
✅ Coin wallet system
✅ Multi-location support
✅ Abstract payment gateway integration
✅ Abstract delivery provider system
✅ Admin analytics and charts
✅ Docker support
✅ Production-ready security settings
