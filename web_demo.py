#!/usr/bin/env python3
"""
Web-based demo of the Hackathon Expense Management module
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from demo_app import ExpenseManager
import json
import requests

app = Flask(__name__)
manager = ExpenseManager()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hackathon Expense Management - Demo</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5; line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px;
            text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .card { 
            background: white; padding: 25px; border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: none;
        }
        .card h2 { margin: 0 0 20px 0; color: #333; font-size: 1.4em; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        .form-control { 
            width: 100%; padding: 12px; border: 2px solid #e1e5e9; 
            border-radius: 8px; font-size: 14px; transition: all 0.3s;
        }
        .form-control:focus { 
            outline: none; border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 12px 24px; 
            border-radius: 8px; cursor: pointer; font-size: 14px;
            font-weight: 600; transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .btn-secondary { background: #6c757d; }
        .btn-success { background: #28a745; }
        .btn-danger { background: #dc3545; }
        .expense-list { display: grid; gap: 15px; }
        .expense-item { 
            background: white; padding: 20px; border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid;
        }
        .expense-item.draft { border-left-color: #ffc107; }
        .expense-item.submitted { border-left-color: #17a2b8; }
        .expense-item.approved { border-left-color: #28a745; }
        .expense-item.rejected { border-left-color: #dc3545; }
        .expense-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .expense-title { font-weight: 600; color: #333; margin: 0; }
        .expense-status { 
            padding: 4px 12px; border-radius: 20px; font-size: 12px; 
            font-weight: 600; text-transform: uppercase;
        }
        .status-draft { background: #fff3cd; color: #856404; }
        .status-submitted { background: #d1ecf1; color: #0c5460; }
        .status-approved { background: #d4edda; color: #155724; }
        .status-rejected { background: #f8d7da; color: #721c24; }
        .expense-details { color: #666; font-size: 14px; }
        .expense-actions { margin-top: 15px; display: flex; gap: 10px; }
        .expense-actions button { padding: 8px 16px; font-size: 12px; }
        .stats { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; margin-bottom: 30px; 
        }
        .stat-card { 
            background: white; padding: 20px; border-radius: 10px; text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .stat-number { font-size: 2.5em; font-weight: 600; margin-bottom: 5px; }
        .stat-label { color: #666; font-size: 14px; }
        .ocr-demo { 
            background: #f8f9fa; border: 2px dashed #dee2e6; 
            border-radius: 10px; padding: 20px; text-align: center;
        }
        .alert { 
            padding: 15px; border-radius: 8px; margin-bottom: 20px;
            border: 1px solid transparent;
        }
        .alert-success { background: #d4edda; border-color: #c3e6cb; color: #155724; }
        .alert-info { background: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Hackathon Expense Management</h1>
            <p>Interactive Demo - Experience the full workflow</p>
        </div>

        {% if message %}
        <div class="alert alert-success">
            {{ message }}
        </div>
        {% endif %}

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" style="color: #667eea;">{{ stats.total }}</div>
                <div class="stat-label">Total Expenses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #28a745;">${{ "%.2f"|format(stats.approved_amount) }}</div>
                <div class="stat-label">Approved Amount</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #ffc107;">{{ stats.pending }}</div>
                <div class="stat-label">Pending Approval</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #17a2b8;">{{ stats.submitted }}</div>
                <div class="stat-label">Submitted</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📝 Create New Expense</h2>
                <form method="POST" action="/create">
                    <div class="form-group">
                        <label for="name">Expense Description</label>
                        <input type="text" id="name" name="name" class="form-control" 
                               placeholder="e.g., Business lunch with client" required>
                    </div>
                    <div class="form-group">
                        <label for="amount">Amount</label>
                        <input type="number" id="amount" name="amount" step="0.01" 
                               class="form-control" placeholder="0.00" required>
                    </div>
                    <div class="form-group">
                        <label for="currency">Currency</label>
                        <select id="currency" name="currency" class="form-control">
                            <option value="USD">USD - US Dollar</option>
                            <option value="EUR">EUR - Euro</option>
                            <option value="GBP">GBP - British Pound</option>
                            <option value="INR">INR - Indian Rupee</option>
                            <option value="JPY">JPY - Japanese Yen</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="category">Category</label>
                        <select id="category" name="category" class="form-control">
                            {% for category in categories %}
                            <option value="{{ category }}">{{ category }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="approvers">Approvers (comma-separated)</label>
                        <input type="text" id="approvers" name="approvers" class="form-control" 
                               placeholder="jane.manager, admin.user" required>
                    </div>
                    <button type="submit" class="btn">Create Expense</button>
                </form>
            </div>

            <div class="card">
                <h2>📸 OCR Receipt Demo</h2>
                <div class="ocr-demo">
                    <p><strong>Try our OCR feature!</strong></p>
                    <p>Paste receipt text below and see the magic:</p>
                    <form method="POST" action="/ocr">
                        <textarea name="receipt_text" rows="8" class="form-control" 
                                  placeholder="Paste your receipt text here...
Example:
STARBUCKS COFFEE
Store #12345
Date: 10/04/2024
Grande Latte    $5.45
Total          $5.45"></textarea>
                        <br>
                        <button type="submit" class="btn">Process OCR</button>
                    </form>
                </div>
                
                {% if ocr_result %}
                <div class="alert alert-info" style="margin-top: 20px;">
                    <strong>OCR Results:</strong><br>
                    💰 Amount: ${{ ocr_result.amount or 'Not found' }}<br>
                    📅 Date: {{ ocr_result.date or 'Not found' }}<br>
                    🏪 Vendor: {{ ocr_result.vendor or 'Not found' }}
                </div>
                {% endif %}
            </div>
        </div>

        <div class="card">
            <h2>📊 All Expenses</h2>
            <div class="expense-list">
                {% for expense in expenses %}
                <div class="expense-item {{ expense.state }}">
                    <div class="expense-header">
                        <h3 class="expense-title">{{ expense.name }}</h3>
                        <span class="expense-status status-{{ expense.state }}">{{ expense.state }}</span>
                    </div>
                    <div class="expense-details">
                        💰 {{ expense.amount_source }} {{ expense.currency }} 
                        (≈ ${{ "%.2f"|format(expense.amount_company) }})<br>
                        👤 {{ expense.employee }} • 
                        📂 {{ expense.category }} • 
                        📅 {{ expense.date }}
                        {% if expense.approvers %}
                        <br>👥 Approvers: {{ expense.approvers|join(', ') }}
                        {% endif %}
                    </div>
                    <div class="expense-actions">
                        {% if expense.state == 'draft' %}
                        <form method="POST" action="/submit/{{ expense.id }}" style="display: inline;">
                            <button type="submit" class="btn btn-secondary">Submit for Approval</button>
                        </form>
                        {% endif %}
                        {% if expense.state in ['submitted', 'in_progress'] %}
                        <form method="POST" action="/approve/{{ expense.id }}" style="display: inline;">
                            <input type="text" name="approver" placeholder="Approver name" 
                                   style="padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-right: 5px;">
                            <button type="submit" class="btn btn-success">Approve</button>
                        </form>
                        {% endif %}
                    </div>
                </div>
                {% else %}
                <div style="text-align: center; padding: 40px; color: #666;">
                    <h3>No expenses yet</h3>
                    <p>Create your first expense using the form above!</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h2>🎯 Demo Features</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 2em; margin-bottom: 10px;">💱</div>
                    <strong>Multi-Currency</strong><br>
                    <small>Real-time conversion via API</small>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 2em; margin-bottom: 10px;">📸</div>
                    <strong>OCR Processing</strong><br>
                    <small>Extract data from receipts</small>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 2em; margin-bottom: 10px;">✅</div>
                    <strong>Approval Workflow</strong><br>
                    <small>Configurable approval rules</small>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 2em; margin-bottom: 10px;">🔒</div>
                    <strong>Security</strong><br>
                    <small>Role-based access control</small>
                </div>
            </div>
        </div>

        <div style="text-align: center; margin: 40px 0; color: #666;">
            <p>🏆 <strong>Hackathon Expense Management Module</strong> - Built for Odoo</p>
            <p>This demo showcases all the key features implemented in our Odoo module</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    expenses = manager.list_expenses()
    
    # Calculate statistics
    stats = {
        'total': len(expenses),
        'pending': len([e for e in expenses if e.state in ['draft', 'submitted']]),
        'submitted': len([e for e in expenses if e.state == 'submitted']),
        'approved_amount': sum(e.amount_company for e in expenses if e.state == 'approved')
    }
    
    categories = [
        "Travel", "Meals & Entertainment", "Accommodation", "Transportation",
        "Office Supplies", "Communication", "Training", "Marketing", "Fuel", "Other"
    ]
    
    return render_template_string(HTML_TEMPLATE, 
                                  expenses=expenses, 
                                  stats=stats, 
                                  categories=categories,
                                  message=request.args.get('message'),
                                  ocr_result=None)

@app.route('/create', methods=['POST'])
def create_expense():
    name = request.form['name']
    amount = float(request.form['amount'])
    currency = request.form['currency']
    category = request.form['category']
    approvers = [a.strip() for a in request.form['approvers'].split(',') if a.strip()]
    
    manager.create_expense(name, "john.employee", amount, currency, category, approvers)
    
    return redirect(url_for('index', message=f"Expense '{name}' created successfully!"))

@app.route('/submit/<int:expense_id>', methods=['POST'])
def submit_expense(expense_id):
    if manager.submit_expense(expense_id):
        return redirect(url_for('index', message=f"Expense {expense_id} submitted for approval!"))
    return redirect(url_for('index', message="Failed to submit expense."))

@app.route('/approve/<int:expense_id>', methods=['POST'])
def approve_expense(expense_id):
    approver = request.form['approver']
    if manager.approve_expense(expense_id, approver):
        return redirect(url_for('index', message=f"Expense {expense_id} approved by {approver}!"))
    return redirect(url_for('index', message="Failed to approve expense."))

@app.route('/ocr', methods=['POST'])
def process_ocr():
    receipt_text = request.form['receipt_text']
    ocr_result = manager.process_ocr(receipt_text)
    
    expenses = manager.list_expenses()
    stats = {
        'total': len(expenses),
        'pending': len([e for e in expenses if e.state in ['draft', 'submitted']]),
        'submitted': len([e for e in expenses if e.state == 'submitted']),
        'approved_amount': sum(e.amount_company for e in expenses if e.state == 'approved')
    }
    
    categories = [
        "Travel", "Meals & Entertainment", "Accommodation", "Transportation",
        "Office Supplies", "Communication", "Training", "Marketing", "Fuel", "Other"
    ]
    
    return render_template_string(HTML_TEMPLATE, 
                                  expenses=expenses, 
                                  stats=stats, 
                                  categories=categories,
                                  message="OCR processing completed!",
                                  ocr_result=ocr_result)

if __name__ == '__main__':
    # Create some sample data
    manager.create_expense("Sample Business Lunch", "john.employee", 85.50, "USD", "Meals & Entertainment", ["jane.manager"])
    manager.create_expense("Conference Flight", "john.employee", 450.00, "EUR", "Travel", ["jane.manager"])
    
    print("🌐 Starting web demo...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)