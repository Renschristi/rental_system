# PostgreSQL Setup Guide

## Option 1: Quick Install (Recommended)

### Download PostgreSQL:
1. Go to: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Download PostgreSQL 16.x (latest version)
4. Run the installer

### During Installation:
- **Password**: Set a password (remember it!) - suggest: `postgres123`
- **Port**: Keep default `5432`
- **Locale**: Default
- Components: Install all (PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools)

### After Installation:
PostgreSQL will be installed at: `C:\Program Files\PostgreSQL\16\bin`

---

## Option 2: Create Database Using pgAdmin

1. Open **pgAdmin 4** (installed with PostgreSQL)
2. Connect to PostgreSQL (use the password you set)
3. Right-click "Databases" → "Create" → "Database"
4. Database name: `rental_db`
5. Owner: `postgres`
6. Click "Save"

---

## Option 3: Create Database Using Command Line

After installing PostgreSQL, add to PATH then run:

```powershell
# Add PostgreSQL to PATH (replace version number if different)
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"

# Create database
psql -U postgres -c "CREATE DATABASE rental_db;"
```

When prompted, enter your PostgreSQL password.

---

## Configure Django to Use PostgreSQL

Once database is created, I'll update your Django settings automatically.

You'll need:
- Database name: `rental_db`
- Username: `postgres`
- Password: (the password you set during installation)
- Host: `localhost`
- Port: `5432`

---

## Quick Start After PostgreSQL is Installed:

Just tell me your PostgreSQL password and I'll:
1. Create the .env file with correct credentials
2. Update settings.py to use PostgreSQL
3. Run migrations to create tables
4. Migrate existing SQLite data to PostgreSQL (optional)

---

## Installation Link:
**https://www.postgresql.org/download/windows/**

Click "Download the installer" and follow the steps above.
