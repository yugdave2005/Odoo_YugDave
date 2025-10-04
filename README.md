# 🏗️ Hackathon Expense Management - Odoo Module

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Odoo](https://img.shields.io/badge/Odoo-17.0-green.svg)](https://www.odoo.com/)
[![License](https://img.shields.io/badge/License-LGPL--3-yellow.svg)](https://www.gnu.org/licenses/lgpl-3.0)

A comprehensive expense management system for Odoo with advanced features including OCR receipt processing, multi-currency support, and flexible approval workflows. Built for hackathon with full PDF specification compliance.

## 🎯 Problem Statement

Companies struggle with manual expense reimbursement processes that are time-consuming, error-prone, and lack transparency. This module provides:

- ✅ **Threshold-based approval flows**
- ✅ **Multi-level approval management** 
- ✅ **Flexible approval rules**
- ✅ **OCR-powered receipt processing**
- ✅ **Multi-currency support with real-time conversion**

## 🚀 Key Features

### 📋 Core Functionality
- **Multi-currency expense claims** with real-time conversion via external API
- **OCR receipt processing** for automatic data extraction
- **Flexible approval workflows** with configurable rules
- **Three-tier user permissions** (Employee, Manager, Admin)
- **Integration with HR module** for employee records
- **Real-time notifications** and activity tracking

### 🔄 Approval Workflow (PDF Compliant)
- **Manager-first approval** when `IS_MANAGER_APPROVER = True`
- **Sequential approval**: Step 1 → Manager, Step 2 → Finance, Step 3 → Director
- **Conditional rules**:
  - **Percentage rule**: e.g., If 60% of approvers approve → Expense approved
  - **Specific approver rule**: e.g., If CFO approves → Expense auto-approved  
  - **Hybrid rule**: Combine both (e.g., 60% OR CFO approves)

### 🔐 Role-Based Permissions
- **Admin**: Create company, manage users, configure rules, view all expenses
- **Manager**: Approve/reject expenses, view team expenses, escalate per rules
- **Employee**: Submit expenses, view own expenses, check approval status

### 🤖 OCR & API Integration
- **OCR for receipts**: Auto-extract amount, date, vendor, expense type
- **Countries API**: `https://restcountries.com/v3.1/all?fields=name,currencies`
- **Currency API**: `https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}`

## 📁 Project Structure

```
hackathon_expense_management/           # Main Odoo Module
├── __init__.py
├── __manifest__.py                     # Module configuration
├── models/
│   ├── __init__.py
│   └── expense_models.py              # Core models (400+ lines)
├── views/
│   └── expense_views.xml              # UI definitions (370+ lines)
├── security/
│   ├── security.xml                   # User groups & record rules
│   └── ir.model.access.csv           # Access permissions
├── controllers/
│   ├── __init__.py
│   └── ocr_controller.py             # OCR & API endpoints (400+ lines)
└── data/
    └── expense_categories.xml         # Default categories

# Demo Applications
├── pdf_compliant_demo.py              # Full PDF-spec demo (900+ lines)
├── web_demo.py                        # Original web demo (370+ lines)  
├── demo_app.py                        # CLI demo (340+ lines)

# Setup & Documentation
├── docker-compose.yml                 # Docker deployment
├── HOW_TO_RUN.md                      # Complete setup guide
├── INSTALLATION_GUIDE.md              # Installation instructions
└── README.md                          # This file
```

## 🏗️ Models Implemented

### 1. **ExpenseClaim** (`expense.claim`)
- Multi-currency amounts with auto-conversion
- Sequential/conditional approval workflow
- OCR integration for receipt processing
- Manager-first approval logic
- Complete state management

### 2. **ExpenseApprovalRule** (`expense.approval.rule`)
- **Percentage rules**: 60% threshold approval
- **Specific approver**: CFO auto-approval
- **Hybrid rules**: 60% OR CFO logic
- **Sequential rules**: Manager → Finance → Director

### 3. **ExpenseApproverLine** (`expense.approver.line`) 
- Step-by-step approval tracking
- Comments and approval dates
- Sequential workflow management

### 4. **ExpenseCategory** (`expense.category`)
- Predefined expense categories
- OCR-based auto-categorization

### 5. **HrEmployeeInherit** (`hr.employee`)
- `IS_MANAGER_APPROVER` field
- Manager relationships
- Role-based permissions

## 🎮 Demo Applications

### 1. **PDF-Compliant Demo** (`pdf_compliant_demo.py`)
- ✅ Implements **every requirement** from PDF specification
- Role switching to test different permissions
- Complete approval workflow demonstration
- OCR processing with receipt text
- Multi-currency conversion
- **Run**: `python pdf_compliant_demo.py` → http://localhost:5001

### 2. **Web Demo** (`web_demo.py`)  
- Beautiful responsive UI
- Real-time statistics dashboard
- Interactive expense management
- **Run**: `python web_demo.py` → http://localhost:5000

### 3. **CLI Demo** (`demo_app.py`)
- Command-line interface
- Interactive and automated modes
- **Run**: `python demo_app.py`

## ⚡ Quick Start

### Method 1: PDF-Compliant Demo (Recommended)
```bash
git clone https://github.com/yugdave2005/Odoo_YugDave.git
cd Odoo_YugDave
pip install flask requests Pillow
python pdf_compliant_demo.py
```
Open http://localhost:5001 and test different user roles!

### Method 2: Full Odoo Installation
```bash
# With Docker
docker-compose up
# Access: http://localhost:8069

# Manual installation
# 1. Install Odoo 17.0
# 2. Copy hackathon_expense_management/ to addons folder  
# 3. Install module from Apps menu
```

### Method 3: Web Demo
```bash
pip install flask requests
python web_demo.py
# Access: http://localhost:5000
```

## 🧪 Testing the PDF Requirements

The `pdf_compliant_demo.py` demonstrates **all PDF requirements**:

### User Roles & Permissions
1. **Switch to Employee**: Create expenses, view own expenses
2. **Switch to Manager**: Approve team expenses, view pending approvals  
3. **Switch to Admin**: Full system access, configure rules

### Approval Workflows
1. **Sequential**: Manager → Finance → Director (step by step)
2. **Percentage**: 60% of approvers must approve
3. **Specific**: CFO can auto-approve
4. **Hybrid**: 60% OR CFO approval

### OCR Testing
Paste this receipt text to test OCR:
```
STARBUCKS COFFEE
Store #12345
Date: 10/04/2024
Grande Latte    $5.45
Total          $5.45
```

## 🛠️ Technical Implementation

### PDF Specification Compliance
- ✅ **Authentication & User Management**: Auto-created company & admin
- ✅ **Expense Submission**: Amount (multi-currency), Category, Description, Date
- ✅ **Manager Approval First**: `IS_MANAGER_APPROVER` field respected
- ✅ **Sequential Workflow**: Expense moves to next approver only after current approves
- ✅ **Conditional Approval**: All rule types implemented
- ✅ **Role Permissions**: Proper access control
- ✅ **OCR Processing**: Auto-extract receipt data
- ✅ **API Integration**: Countries & currency conversion

### Advanced Features
- **External API Integration**: Real-time currency rates
- **OCR with fallback**: Works with/without tesseract
- **Professional Odoo patterns**: Models, Views, Security, Controllers
- **Comprehensive error handling**: User-friendly messages
- **Responsive design**: Works on all devices

## 📊 Code Statistics
- **Total Lines**: ~2000+ lines of production-ready code
- **Models**: 5 comprehensive models with 25+ fields each
- **Views**: Complete XML definitions with modern UI
- **Security**: Proper groups, rules, and permissions
- **Controllers**: REST API endpoints with error handling
- **Documentation**: Extensive comments and guides

## 🏆 Hackathon Features

Perfect for demonstrating at hackathons:

1. **Visual Impact**: Beautiful web interfaces with real-time updates
2. **Technical Depth**: Professional Odoo development patterns
3. **Innovation**: OCR processing, API integration, smart workflows
4. **Completeness**: Full specification compliance
5. **Demo Ready**: Multiple ways to showcase functionality

## 🔧 Installation Requirements

### Basic Demo
```bash
pip install flask requests Pillow
```

### Full Odoo (Optional)
```bash
# For OCR (optional)
pip install pytesseract

# For full Odoo
# Install PostgreSQL
# Install Odoo 17.0
# Or use Docker: docker-compose up
```

## 📝 API Endpoints

### OCR Processing
```
POST /expense/ocr/process
Body: {"attachment_id": 123}
Response: {"success": true, "data": {"amount": 45.50, "date": "2024-10-04", "vendor": "Starbucks"}}
```

### Currency Conversion
```
POST /expense/currency/convert  
Body: {"amount": 100, "from_currency": "EUR", "to_currency": "USD"}
Response: {"success": true, "data": {"converted_amount": 118.0, "rate": 1.18}}
```

### Countries & Currencies
```
GET /expense/countries
Response: {"success": true, "data": [...]}
```

## 🎯 Demo Scenarios

### For Judges/Evaluators
1. **Start with PDF Demo** → Most impressive, shows all requirements
2. **Switch User Roles** → Demonstrate permission differences  
3. **Create Expense** → Show multi-currency conversion
4. **Process OCR** → Paste receipt, see magic happen
5. **Approval Flow** → Submit → Manager → Finance → Director
6. **Show Code** → Professional Odoo development

### For Technical Audience
1. **Code walkthrough** → Models, Views, Security patterns
2. **API integration** → External services, error handling
3. **Database design** → Normalized schema, relationships
4. **Security implementation** → Groups, rules, access control

## 🤝 Contributing

This project was built for a hackathon but is open for improvements:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under LGPL-3 License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

Built with ❤️ for the hackathon by **YugDave**

- GitHub: [@yugdave2005](https://github.com/yugdave2005)
- Project: [Odoo_YugDave](https://github.com/yugdave2005/Odoo_YugDave)

## 🙏 Acknowledgments

- **Odoo Community** for the amazing framework
- **External APIs** for currency and country data
- **Open Source Libraries** for OCR and web functionality
- **Hackathon Organizers** for the opportunity

---

**⭐ Star this repository if you found it helpful!**

**🚀 Ready for the hackathon? Let's build something amazing!**