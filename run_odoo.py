#!/usr/bin/env python3
"""
Simple Odoo runner script for development
This will help you run Odoo with your custom module
"""

import os
import sys
import subprocess

def install_odoo():
    """Install Odoo using pip"""
    print("Installing Odoo...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "odoo"])
        print("✅ Odoo installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Odoo: {e}")
        return False

def check_odoo():
    """Check if Odoo is installed"""
    try:
        import odoo
        print(f"✅ Odoo {odoo.release.version} is installed")
        return True
    except ImportError:
        print("❌ Odoo not found")
        return False

def run_odoo():
    """Run Odoo server"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Configuration
    config = {
        'addons_path': current_dir,
        'db_name': 'hackathon_expense_db',
        'db_user': 'postgres',
        'db_password': 'postgres',
        'db_host': 'localhost',
        'db_port': '5432',
        'http_port': '8069',
        'admin_passwd': 'admin123'
    }
    
    print("🚀 Starting Odoo server...")
    print(f"📁 Addons path: {config['addons_path']}")
    print(f"🌐 Access URL: http://localhost:{config['http_port']}")
    print(f"🔑 Master password: {config['admin_passwd']}")
    
    cmd = [
        sys.executable, "-m", "odoo",
        f"--addons-path={config['addons_path']}",
        f"--db-filter={config['db_name']}",
        f"--http-port={config['http_port']}",
        "--dev=all",
        "--log-level=info"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Odoo server stopped")
    except Exception as e:
        print(f"❌ Error running Odoo: {e}")

def main():
    """Main function"""
    print("🏗️  Hackathon Expense Management - Odoo Runner")
    print("=" * 50)
    
    if not check_odoo():
        print("Installing Odoo...")
        if not install_odoo():
            print("❌ Failed to install Odoo. Please install manually.")
            print("Manual installation:")
            print("1. pip install odoo")
            print("2. Install PostgreSQL")
            print("3. Run this script again")
            return
    
    print("\n📋 Before running, make sure:")
    print("1. PostgreSQL is installed and running")
    print("2. Create a database user 'postgres' with password 'postgres'")
    print("3. Or modify the config in this script")
    print("\nPress Enter to continue, or Ctrl+C to exit...")
    
    try:
        input()
        run_odoo()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()