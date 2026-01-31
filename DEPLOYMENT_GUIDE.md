"""
DEPLOYMENT & SETUP GUIDE
=========================

Complete guide for setting up and running the Rental Management System


PREREQUISITES
=============

Required Software:
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

Optional but Recommended:
- Git (for version control)
- VS Code or PyCharm (for development)
- PostgreSQL GUI (pgAdmin, DBeaver)


STEP-BY-STEP SETUP
==================

1. CLONE/DOWNLOAD PROJECT
-------------------------
Navigate to project directory:
    cd "c:\Users\hp\Desktop\Odoo Gcet"


2. CREATE VIRTUAL ENVIRONMENT
------------------------------
Create venv:
    python -m venv venv

Activate (Windows):
    venv\Scripts\activate

Activate (Mac/Linux):
    source venv/bin/activate

You should see (venv) in your terminal prompt.


3. INSTALL DEPENDENCIES
------------------------
    pip install -r requirements.txt

This installs:
- Django 4.2.7
- psycopg2-binary (PostgreSQL)
- python-decouple (config)
- Pillow (images)
- reportlab (PDF)


4. SETUP POSTGRESQL DATABASE
-----------------------------

A. Install PostgreSQL:
   - Windows: Download from postgresql.org
   - Mac: brew install postgresql
   - Linux: sudo apt-get install postgresql

B. Start PostgreSQL service:
   - Windows: Start via Services or pg_ctl
   - Mac/Linux: sudo service postgresql start

C. Create database:
   
   Open PostgreSQL terminal:
   Windows: psql -U postgres
   Mac/Linux: sudo -u postgres psql
   
   Run these SQL commands:
   
   CREATE DATABASE rental_db;
   CREATE USER rental_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE rental_user SET client_encoding TO 'utf8';
   ALTER ROLE rental_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE rental_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE rental_db TO rental_user;
   \q

   Note: Remember your password!


5. CONFIGURE ENVIRONMENT VARIABLES
-----------------------------------

A. Copy example env file:
   Windows: copy .env.example .env
   Mac/Linux: cp .env.example .env

B. Edit .env file:
   Open .env in text editor and update:
   
   SECRET_KEY=your-long-random-secret-key-here
   DEBUG=True
   DATABASE_NAME=rental_db
   DATABASE_USER=rental_user
   DATABASE_PASSWORD=your_secure_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432

   Generate SECRET_KEY at: https://djecrety.ir/
   Or use: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"


6. RUN DATABASE MIGRATIONS
---------------------------

Create migration files:
    python manage.py makemigrations accounts
    python manage.py makemigrations products
    python manage.py makemigrations rentals
    python manage.py makemigrations billing

Apply migrations:
    python manage.py migrate

This creates all database tables.


7. CREATE SUPERUSER (ADMIN)
----------------------------
    python manage.py createsuperuser

Enter:
- Username: admin (or your choice)
- Email: admin@example.com
- Password: (choose a strong password)
- Password (again): (confirm)

This creates your admin account.


8. LOAD SAMPLE DATA (OPTIONAL)
-------------------------------
To populate with test users and products:
    python manage.py shell < setup_data.py

This creates:
- Admin: username=admin, password=admin123
- Vendor: username=vendor1, password=vendor123
- Customer: username=customer1, password=customer123
- 5 sample products

Skip this if you want to start with empty database.


9. COLLECT STATIC FILES
------------------------
    python manage.py collectstatic

Type 'yes' when prompted.


10. RUN DEVELOPMENT SERVER
---------------------------
    python manage.py runserver

You should see:
    Starting development server at http://127.0.0.1:8000/

Access the application:
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin


VERIFICATION CHECKLIST
======================

✓ Virtual environment activated
✓ Dependencies installed (no errors)
✓ PostgreSQL running
✓ Database created
✓ .env file configured
✓ Migrations applied successfully
✓ Superuser created
✓ Server starts without errors
✓ Can access homepage
✓ Can login to admin panel


FIRST LOGIN
===========

Test the system:

1. Open browser: http://localhost:8000

2. Register new user:
   - Click "Register"
   - Choose role: Customer
   - Fill form and submit

3. Browse products:
   - Click "Products"
   - View product details
   - Configure rental dates

4. Create quotation:
   - Add product to cart
   - Review quotation
   - Confirm order

5. Admin panel:
   - Go to: http://localhost:8000/admin
   - Login with superuser credentials
   - Explore models


TROUBLESHOOTING
===============

Problem: "Module not found" error
Solution: 
    - Make sure venv is activated
    - Run: pip install -r requirements.txt

Problem: "Database connection error"
Solution:
    - Check PostgreSQL is running
    - Verify DATABASE_* settings in .env
    - Test connection: psql -U rental_user -d rental_db

Problem: "No such table" error
Solution:
    - Run: python manage.py migrate
    - Check migrations created: python manage.py showmigrations

Problem: "Static files not loading"
Solution:
    - Run: python manage.py collectstatic
    - Check STATIC_ROOT and STATIC_URL in settings

Problem: "Authentication error"
Solution:
    - Clear browser cache
    - Check user exists: python manage.py shell
      >>> from accounts.models import User
      >>> User.objects.all()

Problem: Port 8000 already in use
Solution:
    - Use different port: python manage.py runserver 8080
    - Or stop other process using port 8000


PRODUCTION DEPLOYMENT
=====================

For production deployment, make these changes:

1. Security Settings (rental_system/settings.py):
   
   DEBUG = False
   
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   
   # Generate new SECRET_KEY
   SECRET_KEY = 'new-production-secret-key'
   
   # Add security middleware
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True

2. Database:
   - Use production PostgreSQL instance
   - Regular backups
   - Connection pooling (pgBouncer)

3. Static/Media Files:
   - Use CDN (Cloudflare, AWS CloudFront)
   - Or serve via Nginx
   - Configure AWS S3 for media uploads

4. Web Server:
   - Use Gunicorn: pip install gunicorn
   - Run: gunicorn rental_system.wsgi:application
   - Configure Nginx as reverse proxy

5. Process Management:
   - Use Supervisor or systemd
   - Auto-restart on crashes

6. Environment Variables:
   - Never commit .env to git
   - Use environment-specific configs

7. Monitoring:
   - Setup Sentry for error tracking
   - Use New Relic or DataDog for performance
   - Configure logging properly

8. Email:
   - Configure SMTP settings
   - Use SendGrid, Mailgun, or AWS SES
   - Add email notifications for orders

9. Caching:
   - Setup Redis for session storage
   - Cache frequent queries
   - Use CDN for static assets

10. Backups:
    - Automated database backups
    - Backup media files
    - Test restoration process


DOCKER DEPLOYMENT (OPTIONAL)
=============================

Create Dockerfile:

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "rental_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Create docker-compose.yml:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: rental_db
      POSTGRES_USER: rental_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn rental_system.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_HOST=db

volumes:
  postgres_data:
```

Run:
    docker-compose up --build


RUNNING TESTS
=============

Run all tests:
    python manage.py test

Run specific app tests:
    python manage.py test rentals

Run with coverage:
    pip install coverage
    coverage run --source='.' manage.py test
    coverage report


COMMON TASKS
============

Create new superuser:
    python manage.py createsuperuser

Change user password:
    python manage.py changepassword username

Clear all data:
    python manage.py flush

Create backup:
    pg_dump rental_db > backup.sql

Restore backup:
    psql rental_db < backup.sql

Check for issues:
    python manage.py check

Open Django shell:
    python manage.py shell


MAINTENANCE MODE
================

To enable maintenance:

1. Create maintenance.html template
2. Add middleware to return maintenance page
3. Or use Nginx to serve static maintenance page


PROJECT STRUCTURE REFERENCE
============================

rental_system/
├── accounts/          # User management
├── products/          # Product catalog
├── rentals/           # Core rental logic ⭐
├── billing/           # Invoicing & payments
├── dashboards/        # Analytics
├── templates/         # HTML templates
├── static/            # CSS, JS, images
├── media/             # User uploads
├── rental_system/     # Project settings
└── manage.py          # Django CLI


NEXT STEPS
==========

After successful setup:

1. Customize branding (logo, colors)
2. Add more product categories
3. Configure email settings
4. Setup payment gateway (Stripe, PayPal)
5. Add automated tests
6. Configure CI/CD pipeline
7. Setup monitoring and logging
8. Create user documentation
9. Plan scaling strategy
10. Launch! 🚀


SUPPORT
=======

For issues:
1. Check this guide
2. Review README.md
3. Check Django documentation
4. Review code comments
5. Search Stack Overflow


CREDITS
=======

Built with:
- Django 4.2.7
- Bootstrap 5.3
- PostgreSQL
- Love and caffeine ☕


Good luck with your rental business! 🎉
"""
