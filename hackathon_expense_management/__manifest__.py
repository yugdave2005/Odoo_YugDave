# -*- coding: utf-8 -*-
{
    'name': 'Hackathon Expense Management',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'Advanced expense management system with OCR and approval workflow',
    'description': """
        Hackathon Expense Management Module
        ==================================
        
        A comprehensive expense management system built for hackathon with the following features:
        
        **Key Features:**
        - Multi-currency expense claims with real-time currency conversion
        - OCR receipt processing for automatic data extraction
        - Flexible approval workflows with configurable rules
        - Three-tier user permissions (Employee, Manager, Admin)
        - Integration with HR employee records
        - Real-time notifications and activity tracking
        - Kanban, tree, and form views for expense management
        
        **Models:**
        - Expense Claims with approval workflow
        - Approval rules (percentage-based, specific user, hybrid)
        - Expense categories for classification
        - Approver lines for tracking approval status
        
        **OCR Features:**
        - Automatic amount extraction from receipts
        - Date recognition and parsing
        - Vendor name identification
        - Support for multiple image formats
        
        **Security:**
        - Role-based access control
        - Record-level security rules
        - Proper data isolation between users
        
        **Dependencies:**
        - HR module for employee integration
        - Mail module for notifications
        - External API integration for currency rates
        - Optional: pytesseract for OCR functionality
    """,
    'author': 'Hackathon Team',
    'website': 'https://github.com/your-repo/hackathon_expense_management',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'mail',
        'web',
        'base_setup',
    ],
    'external_dependencies': {
        'python': [
            'requests',  # For currency API calls
            # 'pytesseract',  # Optional: for OCR functionality
            # 'Pillow',  # Optional: for image processing
        ],
    },
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Views
        'views/expense_views.xml',
        
        # Data files
        'data/expense_categories.xml',
    ],
    'demo': [
        # Demo data files (if any)
        # 'demo/expense_demo.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/screenshot1.png',
        'static/description/screenshot2.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 95,
    'post_init_hook': '_post_init_hook',
    'uninstall_hook': '_uninstall_hook',
}


def _post_init_hook(cr, registry):
    """Post-installation hook"""
    import logging
    _logger = logging.getLogger(__name__)
    _logger.info("Hackathon Expense Management module installed successfully!")
    
    # You can add any post-installation logic here
    # For example: create default categories, approval rules, etc.


def _uninstall_hook(cr, registry):
    """Pre-uninstallation hook"""
    import logging
    _logger = logging.getLogger(__name__)
    _logger.info("Hackathon Expense Management module uninstalled.")
    
    # You can add any cleanup logic here
    # For example: archive records, cleanup data, etc.