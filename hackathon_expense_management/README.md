# Hackathon Expense Management Module

A comprehensive expense management system for Odoo with advanced features including OCR receipt processing, multi-currency support, and flexible approval workflows.

## 🚀 Features

### Core Functionality
- ✅ **Multi-currency expense claims** with real-time conversion via external API
- ✅ **OCR receipt processing** for automatic data extraction
- ✅ **Flexible approval workflows** with configurable rules
- ✅ **Three-tier user permissions** (Employee, Manager, Admin)
- ✅ **Integration with HR module** for employee records
- ✅ **Real-time notifications** and activity tracking
- ✅ **Multiple view types** (Kanban, Tree, Form)

### Models Implemented
- `expense.claim` - Main expense claim model
- `expense.approver.line` - Approval tracking
- `expense.approval.rule` - Configurable approval rules
- `expense.category` - Expense categorization
- `hr.employee` - Extended with manager approval flag

### OCR Capabilities
- 🔍 **Automatic amount extraction** from receipt images
- 📅 **Date recognition** and parsing
- 🏪 **Vendor name identification**
- 🖼️ **Multiple image format support** (PNG, JPG, etc.)
- 🔄 **Fallback processing** when OCR libraries unavailable

### Security Features
- 🔐 **Role-based access control**
- 🛡️ **Record-level security rules**
- 🔒 **Data isolation between users**
- 👥 **Group-based permissions**

## 📁 Module Structure

```
hackathon_expense_management/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── expense_models.py
├── views/
│   └── expense_views.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
└── controllers/
    ├── __init__.py
    └── ocr_controller.py
```

## 🛠️ Installation

### Prerequisites
1. **Odoo 15.0+** installed and running
2. **Python dependencies**:
   ```bash
   pip install requests
   # Optional for OCR functionality:
   pip install pytesseract Pillow
   ```
3. **Tesseract OCR** (optional, for receipt processing):
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

### Module Installation
1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install "Hackathon Expense Management" from Apps menu
4. Assign users to appropriate groups in Settings > Users & Companies > Groups

## 🎯 Usage Guide

### For Employees
1. **Create Expense**: Go to Expense Management > My Expenses > Create
2. **Fill Details**: Add description, amount, category, and date
3. **Upload Receipt**: Attach receipt image for automatic OCR processing
4. **Add Approvers**: Select users who should approve the expense
5. **Submit**: Click "Submit for Approval" to start the workflow

### For Managers
1. **Review Expenses**: Go to Expense Management > Pending Approval
2. **Approve/Reject**: Use the buttons in the expense form
3. **Add Comments**: Provide feedback in the approver lines
4. **Track Status**: Monitor approval progress in real-time

### For Administrators
1. **Configure Categories**: Expense Management > Configuration > Categories
2. **Setup Approval Rules**: Configure percentage/user-based rules
3. **Manage Security**: Assign users to Employee/Manager/Admin groups
4. **Monitor System**: Review all expenses and approvals

## ⚙️ Configuration

### User Groups
- **Employee: Expense Management** - Basic expense creation and viewing
- **Manager: Expense Management** - Approval rights + employee features
- **Administrator: Expense Management** - Full system access

### Approval Rules
Three types of approval rules are supported:

1. **Percentage-based**: Requires X% of approvers to approve
2. **Specific User**: Requires specific user approval
3. **Hybrid**: Combines percentage and specific user logic with OR/AND operators

### Currency Setup
- Uses external API (exchangerate-api.com) for real-time conversion
- Falls back to Odoo's built-in currency conversion if API fails
- Supports all major world currencies

## 🔧 OCR Configuration

### Installing OCR Dependencies
```bash
# Required for OCR functionality
pip install pytesseract Pillow

# Install Tesseract OCR engine
# Windows: Download installer from GitHub
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

### OCR Features
- **Amount Detection**: Recognizes currency symbols and amounts
- **Date Parsing**: Supports multiple date formats (MM/DD/YYYY, DD-MM-YYYY, etc.)
- **Vendor Extraction**: Identifies business names from receipt headers
- **Error Handling**: Graceful fallback when OCR fails

## 📊 API Endpoints

### OCR Processing
- **URL**: `/expense/ocr/process`
- **Method**: POST (JSON)
- **Auth**: Required
- **Parameters**: `attachment_id`
- **Response**: `{success: bool, data: {amount, date, vendor}}`

## 🐛 Troubleshooting

### Common Issues

1. **OCR not working**:
   - Install pytesseract and Pillow: `pip install pytesseract Pillow`
   - Install Tesseract OCR engine on your system
   - Check file permissions on uploaded images

2. **Currency conversion fails**:
   - Check internet connection
   - Verify API access to exchangerate-api.com
   - Falls back to Odoo's built-in rates automatically

3. **Permission errors**:
   - Verify user is assigned to correct security group
   - Check record rules in Security settings
   - Ensure proper access rights in CSV file

4. **Views not loading**:
   - Update module after code changes
   - Clear browser cache
   - Check Odoo logs for XML parsing errors

### Debug Mode
Enable developer mode in Odoo for additional debugging options:
- Technical menu access
- Field debugging
- View structure inspection

## 🤝 Contributing

This module was built for a hackathon. For improvements:

1. Fork the repository
2. Create feature branch
3. Make changes with proper testing
4. Submit pull request with description

## 📋 TODO / Enhancement Ideas

- [ ] Mobile app support
- [ ] Bulk expense import
- [ ] Advanced reporting dashboard
- [ ] Integration with accounting modules
- [ ] Mileage tracking
- [ ] Expense policy enforcement
- [ ] AI-powered expense categorization
- [ ] Multi-level approval workflows
- [ ] Expense budgeting and limits

## 📄 License

This project is licensed under LGPL-3 License - see the LICENSE file for details.

## 🏆 Hackathon Team

Built with ❤️ for the hackathon by an awesome team of developers!

---

**Need Help?** Check the Odoo logs, enable debug mode, or review the model/view definitions for troubleshooting.