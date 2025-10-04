# Odoo Installation Guide for Windows

## Prerequisites Installation

### 1. Install PostgreSQL
1. Download from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for 'postgres' user
4. Default port: 5432

### 2. Install Odoo Community Edition
1. Download from: https://www.odoo.com/page/download
2. Or download directly: https://nightly.odoo.com/17.0/nightly/exe/odoo_17.0.latest.exe
3. Install with default settings

### 3. Install Python Dependencies (Already done)
```bash
pip install psycopg2-binary requests Pillow pytesseract
```

## Quick Start Method (Alternative)

### Method 1: Using Odoo.sh (Cloud - Easiest)
1. Go to https://www.odoo.com/trial
2. Sign up for free trial
3. Upload our module as a ZIP file

### Method 2: Download Portable Odoo
1. Download: https://nightly.odoo.com/17.0/nightly/exe/odoo_17.0.latest.exe
2. Install and run
3. Access: http://localhost:8069

## Running Your Module

### After Odoo Installation:
1. Copy `hackathon_expense_management` folder to Odoo addons directory
2. Start Odoo
3. Go to http://localhost:8069
4. Create database
5. Install "Hackathon Expense Management" from Apps

## Module Location
Move the module to one of these locations:
- `C:\Program Files\Odoo 17.0\server\odoo\addons\`
- Create custom addons folder and configure in odoo.conf

## Configuration File (odoo.conf)
```ini
[options]
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_postgres_password
addons_path = C:\Program Files\Odoo 17.0\server\odoo\addons,D:\EXP_Tra
```