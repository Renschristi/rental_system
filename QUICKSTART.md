"""
Quick Start Guide
=================

Follow these steps to get the Rental Management System running:

STEP 1: Install Dependencies
-----------------------------
Make sure you have Python 3.8+ and PostgreSQL installed.

Create virtual environment:
    python -m venv venv
    venv\Scripts\activate  (Windows)
    source venv/bin/activate  (Mac/Linux)

Install requirements:
    pip install -r requirements.txt


STEP 2: Configure Database
---------------------------
Create PostgreSQL database:
    
    Open PostgreSQL command line:
    psql -U postgres
    
    Run these commands:
    CREATE DATABASE rental_db;
    CREATE USER postgres WITH PASSWORD 'your-password';
    GRANT ALL PRIVILEGES ON DATABASE rental_db TO postgres;
    \q

Configure .env file:
    cp .env.example .env
    
    Edit .env and update:
    - SECRET_KEY (generate one at https://djecrety.ir/)
    - DATABASE_PASSWORD (your postgres password)


STEP 3: Initialize Database
----------------------------
Run migrations:
    python manage.py makemigrations
    python manage.py migrate

Create superuser (admin):
    python manage.py createsuperuser
    
    Enter:
    - Username: admin
    - Email: admin@example.com
    - Password: (your choice)


STEP 4: Load Sample Data (Optional)
------------------------------------
To populate with test users and products:
    python manage.py shell < setup_data.py

This creates:
- Admin user (username: admin, password: admin123)
- Vendor user (username: vendor1, password: vendor123)
- Customer user (username: customer1, password: customer123)
- Sample categories
- Sample products


STEP 5: Run Server
-------------------
Start development server:
    python manage.py runserver

Access at: http://localhost:8000


STEP 6: Test the System
------------------------
1. Customer Workflow:
   - Register/Login as customer
   - Browse products
   - Add product to quotation with dates
   - Confirm quotation → becomes rental order
   - View invoice and make payment

2. Vendor Workflow:
   - Login as vendor (vendor1/vendor123)
   - Add new products
   - View rental orders
   - Process pickup and return

3. Admin Workflow:
   - Login as admin
   - View system dashboard
   - Access admin panel at /admin
   - View analytics


Common Issues
-------------
Q: Migration errors?
A: Delete db.sqlite3 (if exists) and __pycache__ folders, then re-run migrations

Q: Database connection error?
A: Check PostgreSQL is running and credentials in .env are correct

Q: Static files not loading?
A: Run: python manage.py collectstatic

Q: Import errors?
A: Make sure virtual environment is activated


Project Structure
-----------------
accounts/     - User management, authentication
products/     - Rentable products and inventory
rentals/      - Quotations, reservations, orders
billing/      - Invoices and payments
dashboards/   - Analytics and reports
templates/    - Bootstrap HTML templates


Key Features to Test
--------------------
1. Reservation Logic:
   - Try to book same product for overlapping dates
   - System should prevent double booking

2. Late Fee Calculation:
   - Create rental with past end date
   - Process return
   - Check invoice for late fee

3. Partial Payments:
   - Make payment less than total
   - Invoice status → "Partially Paid"
   - Make second payment to complete


Need Help?
----------
- Check README.md for detailed documentation
- Review code comments for business logic explanation
- Django docs: https://docs.djangoproject.com/


Happy Hacking! 🚀
