#!/usr/bin/env python3
"""
Hackathon Expense Management - Standalone Demo
This demonstrates the key features of our Odoo module without requiring full Odoo installation
"""

import json
import os
from datetime import datetime, date
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import requests

# Mock data storage
expenses_db = []
categories_db = [
    "Travel", "Meals & Entertainment", "Accommodation", "Transportation",
    "Office Supplies", "Communication", "Training", "Marketing", "Fuel", "Other"
]
users_db = {
    "employee": {"name": "John Employee", "role": "employee"},
    "manager": {"name": "Jane Manager", "role": "manager"},
    "admin": {"name": "Admin User", "role": "admin"}
}

@dataclass
class ExpenseRecord:
    id: int
    name: str
    employee: str
    amount_source: float
    currency: str
    amount_company: float
    category: str
    date: str
    state: str
    approvers: List[str]
    receipt_info: Optional[Dict] = None

class ExpenseManager:
    def __init__(self):
        self.expenses = []
        self.next_id = 1
    
    def create_expense(self, name, employee, amount, currency, category, approvers):
        """Create a new expense"""
        # Simulate currency conversion
        amount_company = self.convert_currency(amount, currency, "USD")
        
        expense = ExpenseRecord(
            id=self.next_id,
            name=name,
            employee=employee,
            amount_source=amount,
            currency=currency,
            amount_company=amount_company,
            category=category,
            date=date.today().isoformat(),
            state="draft",
            approvers=approvers
        )
        
        self.expenses.append(expense)
        self.next_id += 1
        
        print(f"✅ Expense '{name}' created successfully!")
        print(f"   ID: {expense.id}")
        print(f"   Amount: {amount} {currency} ({amount_company:.2f} USD)")
        return expense
    
    def convert_currency(self, amount, from_curr, to_curr):
        """Convert currency using external API (with fallback)"""
        if from_curr == to_curr:
            return amount
        
        try:
            # Use the same API as in our Odoo module
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            response = requests.get(url, timeout=5)
            data = response.json()
            rate = data['rates'].get(to_curr, 1)
            return amount * rate
        except:
            # Fallback rates
            rates = {"EUR": 1.1, "GBP": 1.25, "INR": 0.012, "JPY": 0.0067}
            return amount * rates.get(to_curr, 1)
    
    def submit_expense(self, expense_id):
        """Submit expense for approval"""
        expense = self.get_expense(expense_id)
        if expense and expense.state == "draft":
            expense.state = "submitted"
            print(f"✅ Expense {expense_id} submitted for approval")
            return True
        return False
    
    def approve_expense(self, expense_id, approver):
        """Approve expense"""
        expense = self.get_expense(expense_id)
        if expense and expense.state in ["submitted", "in_progress"]:
            if approver in expense.approvers:
                expense.state = "approved"
                print(f"✅ Expense {expense_id} approved by {approver}")
                return True
        return False
    
    def get_expense(self, expense_id):
        """Get expense by ID"""
        for expense in self.expenses:
            if expense.id == expense_id:
                return expense
        return None
    
    def list_expenses(self, employee=None, state=None):
        """List expenses with filters"""
        filtered = self.expenses
        
        if employee:
            filtered = [e for e in filtered if e.employee == employee]
        if state:
            filtered = [e for e in filtered if e.state == state]
        
        return filtered
    
    def process_ocr(self, receipt_text):
        """Simulate OCR processing"""
        import re
        
        result = {
            'amount': None,
            'date': None,
            'vendor': None
        }
        
        # Extract amount
        amount_match = re.search(r'[\$€£¥₹]\s*(\d+[.,]?\d*)', receipt_text)
        if amount_match:
            result['amount'] = float(amount_match.group(1).replace(',', ''))
        
        # Extract date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', receipt_text)
        if date_match:
            result['date'] = date_match.group(1)
        
        # Extract vendor (first line)
        lines = receipt_text.strip().split('\n')
        if lines:
            result['vendor'] = lines[0][:30]
        
        return result

def demo_workflow():
    """Demonstrate the expense workflow"""
    print("🏗️  Hackathon Expense Management - DEMO")
    print("=" * 50)
    
    manager = ExpenseManager()
    
    print("\n1️⃣  Creating Sample Expenses...")
    
    # Create expenses
    expense1 = manager.create_expense(
        name="Business Lunch with Client",
        employee="john.employee",
        amount=85.50,
        currency="USD",
        category="Meals & Entertainment",
        approvers=["jane.manager"]
    )
    
    expense2 = manager.create_expense(
        name="Flight to Conference",
        employee="john.employee",
        amount=450.00,
        currency="EUR",
        category="Travel",
        approvers=["jane.manager", "admin.user"]
    )
    
    print("\n2️⃣  Demonstrating OCR Processing...")
    receipt_text = """
    STARBUCKS COFFEE
    Store #12345
    123 Main St, City
    
    Date: 10/04/2024
    Time: 14:30
    
    Grande Latte        $5.45
    Blueberry Muffin    $3.25
    -------------------------
    Subtotal            $8.70
    Tax                 $0.70
    Total              $9.40
    
    Thank you for visiting!
    """
    
    ocr_data = manager.process_ocr(receipt_text)
    print(f"📸 OCR Results: {ocr_data}")
    
    # Create expense from OCR
    if ocr_data['amount']:
        expense3 = manager.create_expense(
            name=f"Coffee Meeting - {ocr_data.get('vendor', 'Unknown')}",
            employee="john.employee",
            amount=ocr_data['amount'],
            currency="USD",
            category="Meals & Entertainment",
            approvers=["jane.manager"]
        )
    
    print("\n3️⃣  Submitting Expenses for Approval...")
    manager.submit_expense(1)
    manager.submit_expense(2)
    if 'expense3' in locals():
        manager.submit_expense(3)
    
    print("\n4️⃣  Manager Approving Expenses...")
    manager.approve_expense(1, "jane.manager")
    manager.approve_expense(2, "jane.manager")
    
    print("\n5️⃣  Expense Summary:")
    print("-" * 40)
    for expense in manager.expenses:
        print(f"ID: {expense.id} | {expense.name[:30]:<30} | {expense.state.upper():<10} | ${expense.amount_company:.2f}")
    
    print("\n6️⃣  Filter Examples:")
    print("\n📋 All Draft Expenses:")
    draft_expenses = manager.list_expenses(state="draft")
    for exp in draft_expenses:
        print(f"  - {exp.name} (${exp.amount_company:.2f})")
    
    print("\n✅ All Approved Expenses:")
    approved_expenses = manager.list_expenses(state="approved")
    total_approved = sum(exp.amount_company for exp in approved_expenses)
    for exp in approved_expenses:
        print(f"  - {exp.name} (${exp.amount_company:.2f})")
    print(f"\n💰 Total Approved Amount: ${total_approved:.2f}")
    
    print("\n🎯 Demo Features Demonstrated:")
    print("  ✅ Multi-currency expense creation")
    print("  ✅ Real-time currency conversion")
    print("  ✅ OCR receipt processing")
    print("  ✅ Approval workflow")
    print("  ✅ State management")
    print("  ✅ Filtering and reporting")
    
    print("\n📊 Module Statistics:")
    print(f"  • Total Expenses: {len(manager.expenses)}")
    print(f"  • Categories Available: {len(categories_db)}")
    print(f"  • User Roles: {len(users_db)}")
    
    return manager

def interactive_demo():
    """Run interactive demo"""
    manager = ExpenseManager()
    
    print("🎮 Interactive Expense Management Demo")
    print("=" * 40)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Create new expense")
        print("2. List all expenses")
        print("3. Submit expense for approval")
        print("4. Approve expense")
        print("5. Test OCR processing")
        print("6. Show categories")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            print("\n📝 Creating New Expense")
            name = input("Expense description: ")
            employee = input("Employee (default: john.employee): ") or "john.employee"
            amount = float(input("Amount: "))
            currency = input("Currency (USD/EUR/GBP): ") or "USD"
            
            print("Available categories:", ", ".join(categories_db))
            category = input("Category: ") or "Other"
            approvers = input("Approvers (comma-separated): ").split(",")
            approvers = [a.strip() for a in approvers if a.strip()]
            
            manager.create_expense(name, employee, amount, currency, category, approvers)
        
        elif choice == "2":
            print("\n📊 All Expenses:")
            expenses = manager.list_expenses()
            if not expenses:
                print("No expenses found.")
            else:
                for exp in expenses:
                    print(f"{exp.id}: {exp.name} - ${exp.amount_company:.2f} ({exp.state})")
        
        elif choice == "3":
            expense_id = int(input("Enter expense ID to submit: "))
            manager.submit_expense(expense_id)
        
        elif choice == "4":
            expense_id = int(input("Enter expense ID to approve: "))
            approver = input("Approver name: ")
            manager.approve_expense(expense_id, approver)
        
        elif choice == "5":
            print("\n📸 OCR Demo - Enter receipt text:")
            receipt = input("Paste receipt text: ")
            result = manager.process_ocr(receipt)
            print(f"OCR Results: {result}")
        
        elif choice == "6":
            print("\n📂 Available Categories:")
            for i, cat in enumerate(categories_db, 1):
                print(f"{i}. {cat}")
        
        elif choice == "7":
            print("👋 Thanks for trying the demo!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Automated demo")
    print("2. Interactive demo")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "1":
        demo_workflow()
    elif choice == "2":
        interactive_demo()
    else:
        print("Running automated demo...")
        demo_workflow()