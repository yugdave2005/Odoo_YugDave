# -*- coding: utf-8 -*-

import requests
import logging
from datetime import date
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    """Extend company with expense management settings"""
    _inherit = 'res.company'
    
    # Auto-created on first signup with country's currency


class ExpenseCategory(models.Model):
    """Expense categories for classification"""
    _name = 'expense.category'
    _description = 'Expense Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Category name must be unique!')
    ]


class ExpenseApprovalRule(models.Model):
    """Rules for expense approval workflow as per PDF requirements"""
    _name = 'expense.approval.rule'
    _description = 'Expense Approval Rule'
    _order = 'sequence, name'

    name = fields.Char(string='Rule Name', required=True)
    
    # PDF Requirement: Support 3 types of approval rules
    rule_type = fields.Selection([
        ('percentage', 'Percentage Rule'),  # e.g., If 60% of approvers approve → Expense approved
        ('specific_approver', 'Specific Approver Rule'),  # e.g., If CFO approves → Expense auto-approved
        ('hybrid', 'Hybrid Rule'),  # Combine both (e.g., 60% OR CFO approves)
        ('sequential', 'Sequential Approval'),  # Step 1 → Manager, Step 2 → Finance, Step 3 → Director
    ], string='Rule Type', required=True, default='percentage')
    
    # Percentage rule settings
    approval_percentage = fields.Float(
        string='Approval Percentage',
        help='Percentage of approvers required to approve (e.g., 60)'
    )
    
    # Specific approver rule settings
    specific_approver_id = fields.Many2one(
        'hr.employee',
        string='Specific Approver',
        help='Specific approver who can auto-approve (e.g., CFO)'
    )
    
    # Hybrid rule settings
    hybrid_logic = fields.Selection([
        ('OR', 'OR Logic'),  # 60% OR CFO approves
        ('AND', 'AND Logic')  # 60% AND CFO approves
    ], string='Hybrid Logic', default='OR',
       help='Logic for combining percentage and specific approver rules')
    
    # Sequential approval settings
    sequence = fields.Integer(string='Sequence', default=10)
    approver_line_ids = fields.One2many(
        'expense.approval.rule.line',
        'rule_id',
        string='Sequential Approvers'
    )
    
    # Threshold-based rules
    amount_threshold = fields.Float(
        string='Amount Threshold',
        help='Apply this rule only for expenses above this amount'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    @api.constrains('rule_type', 'approval_percentage', 'specific_approver_id', 'approver_line_ids')
    def _check_rule_configuration(self):
        for rule in self:
            if rule.rule_type == 'percentage' and not rule.approval_percentage:
                raise ValidationError("Approval percentage is required for percentage-based rules.")
            if rule.rule_type == 'specific_approver' and not rule.specific_approver_id:
                raise ValidationError("Specific approver is required for specific approver rules.")
            if rule.rule_type == 'hybrid' and (not rule.approval_percentage or not rule.specific_approver_id):
                raise ValidationError("Both approval percentage and specific approver are required for hybrid rules.")
            if rule.rule_type == 'sequential' and not rule.approver_line_ids:
                raise ValidationError("Sequential approvers are required for sequential approval rules.")
            if rule.approval_percentage and (rule.approval_percentage < 0 or rule.approval_percentage > 100):
                raise ValidationError("Approval percentage must be between 0 and 100.")


class ExpenseApprovalRuleLine(models.Model):
    """Sequential approver lines for approval rules"""
    _name = 'expense.approval.rule.line'
    _description = 'Expense Approval Rule Line'
    _order = 'sequence, id'
    
    rule_id = fields.Many2one('expense.approval.rule', string='Approval Rule', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Step', default=10, required=True)
    approver_id = fields.Many2one('hr.employee', string='Approver', required=True)
    role_name = fields.Char(string='Role', help='e.g., Manager, Finance, Director')
    
    @api.model
    def create(self, vals):
        """Auto-increment sequence for new lines"""
        if not vals.get('sequence') and vals.get('rule_id'):
            max_sequence = self.search([('rule_id', '=', vals['rule_id'])], order='sequence desc', limit=1)
            vals['sequence'] = (max_sequence.sequence or 0) + 10
        return super().create(vals)


class ExpenseApproverLine(models.Model):
    """Approval lines for expense claims - PDF Requirements Implementation"""
    _name = 'expense.approver.line'
    _description = 'Expense Approver Line'
    _order = 'sequence, id'

    claim_id = fields.Many2one('expense.claim', string='Expense Claim', required=True, ondelete='cascade')
    approver_id = fields.Many2one('hr.employee', string='Approver', required=True)  # Changed to hr.employee
    sequence = fields.Integer(string='Step', default=10, help='Approval step sequence')
    
    status = fields.Selection([
        ('waiting', 'Waiting'),  # Not their turn yet
        ('pending', 'Pending'),  # Their turn to approve
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='waiting', required=True)
    
    comments = fields.Text(string='Comments', help='Comments added during approval/rejection')
    approval_date = fields.Datetime(string='Approval Date')
    
    # PDF Requirement: Sequential approval - expense moves to next approver only after current one approves
    is_current_approver = fields.Boolean(
        string='Current Approver',
        help='True if this is the current step in sequential approval'
    )
    
    # Role information
    role_name = fields.Char(string='Role', help='e.g., Manager, Finance, Director')

    @api.model
    def create(self, vals):
        """Override create to ensure proper sequence"""
        if not vals.get('sequence'):
            claim_id = vals.get('claim_id')
            if claim_id:
                max_sequence = self.search([('claim_id', '=', claim_id)], order='sequence desc', limit=1)
                vals['sequence'] = (max_sequence.sequence or 0) + 10
        return super().create(vals)


class ExpenseClaim(models.Model):
    """Main expense claim model - Implementing PDF Requirements"""
    _name = 'expense.claim'
    _description = 'Expense Claim'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # PDF Requirement: Expense Submission fields (Amount, Category, Description, Date)
    name = fields.Char(string='Description', required=True, tracking=True)
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self._get_default_employee(),
        tracking=True
    )
    
    # PDF Requirement: Amount can be different from company's currency
    amount_source = fields.Float(
        string='Amount',
        required=True,
        tracking=True,
        help='Amount in the expense currency'
    )
    
    source_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )
    
    # PDF Requirement: Amount visible in company's default currency for managers
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        related='company_id.currency_id',
        store=True
    )
    
    amount_company = fields.Float(
        string='Amount (Company Currency)',
        compute='_compute_amount_company',
        store=True,
        tracking=True,
        help='Amount converted to company currency for manager visibility'
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=date.today,
        tracking=True
    )
    
    category_id = fields.Many2one(
        'expense.category',
        string='Category',
        required=True,
        tracking=True
    )
    
    # PDF Requirement: Enhanced state management for approval workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('waiting_approval', 'Waiting for Approval'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', default='draft', required=True, tracking=True)
    
    # PDF Requirement: Approval workflow fields
    approver_line_ids = fields.One2many(
        'expense.approver.line',
        'claim_id',
        string='Approvers',
        help='Sequential or conditional approvers'
    )
    
    approval_rule_id = fields.Many2one(
        'expense.approval.rule',
        string='Approval Rule',
        help='Rule that defines how this expense should be approved'
    )
    
    # PDF Requirement: OCR for receipts (auto-read)
    receipt_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Receipt',
        help='Upload receipt for OCR processing - auto-generates expense details'
    )
    
    # PDF Requirement: First approved by manager if IS_MANAGER_APPROVER is checked
    manager_approval_required = fields.Boolean(
        string='Manager Approval Required',
        compute='_compute_manager_approval_required',
        store=True,
        help='True if employee\'s manager needs to approve first'
    )
    
    current_approver_id = fields.Many2one(
        'hr.employee',
        string='Current Approver',
        help='Current person who needs to approve this expense'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to false to archive the expense claim'
    )
    
    # Computed fields for approval status
    pending_approvals = fields.Integer(
        string='Pending Approvals',
        compute='_compute_approval_status'
    )
    
    total_approvers = fields.Integer(
        string='Total Approvers',
        compute='_compute_approval_status'
    )

    @api.model
    def _get_default_employee(self):
        """Get current user's employee record"""
        return self.env.user.employee_id
    
    @api.depends('employee_id.expense_manager_id', 'employee_id.expense_manager_id.is_manager_approver')
    def _compute_manager_approval_required(self):
        """PDF Requirement: Check if manager approval is required first"""
        for record in self:
            manager = record.employee_id.expense_manager_id
            record.manager_approval_required = bool(manager and manager.is_manager_approver)

    @api.depends('amount_source', 'source_currency_id', 'company_currency_id')
    def _compute_amount_company(self):
        """Compute amount in company currency using external API"""
        for record in self:
            if not record.amount_source or not record.source_currency_id:
                record.amount_company = 0.0
                continue
                
            # If same currency, no conversion needed
            if record.source_currency_id == record.company_currency_id:
                record.amount_company = record.amount_source
                continue
            
            # Get conversion rate from external API
            try:
                rate = self._get_conversion_rate(
                    record.source_currency_id.name,
                    record.company_currency_id.name
                )
                record.amount_company = record.amount_source * rate
            except Exception as e:
                _logger.error(f"Currency conversion failed: {str(e)}")
                # Fallback to Odoo's built-in currency conversion
                record.amount_company = record.source_currency_id._convert(
                    record.amount_source,
                    record.company_currency_id,
                    record.company_id,
                    record.date or date.today()
                )

    def _get_conversion_rate(self, from_currency, to_currency):
        """Get conversion rate from external API"""
        try:
            # Use the external API for conversion rates
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            if to_currency not in rates:
                raise UserError(f"Conversion rate not found for {to_currency}")
                
            return rates[to_currency]
            
        except requests.RequestException as e:
            _logger.error(f"API request failed: {str(e)}")
            raise UserError(f"Failed to fetch conversion rate: {str(e)}")
        except Exception as e:
            _logger.error(f"Conversion rate calculation failed: {str(e)}")
            raise UserError(f"Currency conversion error: {str(e)}")

    @api.depends('approver_line_ids.status')
    def _compute_approval_status(self):
        """Compute approval status counts"""
        for record in self:
            record.total_approvers = len(record.approver_line_ids)
            record.pending_approvals = len(record.approver_line_ids.filtered(
                lambda x: x.status == 'pending'
            ))

    def action_submit(self):
        """PDF Requirement: Submit expense for approval with proper workflow"""
        if self.state != 'draft':
            raise UserError("Only draft expenses can be submitted.")
        
        # PDF Requirement: Setup approval workflow based on manager and rules
        self._setup_approval_workflow()
        
        if not self.approver_line_ids:
            raise UserError("No approvers configured for this expense. Please check approval rules.")
        
        self.state = 'submitted'
        
        # PDF Requirement: Start approval process with first approver
        self._start_approval_process()
        
        # Process OCR if receipt is attached (PDF Additional feature)
        if self.receipt_attachment_id:
            self._process_receipt_ocr()
        
        # Send notification
        self.message_post(
            body=f"Expense '{self.name}' has been submitted for approval. Current approver: {self.current_approver_id.name if self.current_approver_id else 'Multiple'}",
            subject="Expense Submitted for Approval"
        )

    def _setup_approval_workflow(self):
        """PDF Requirement: Setup approval workflow based on manager and rules"""
        # Clear existing approver lines
        self.approver_line_ids.unlink()
        
        approver_lines = []
        
        # PDF Requirement: First approved by manager if IS_MANAGER_APPROVER is checked
        if self.manager_approval_required:
            manager = self.employee_id.expense_manager_id
            approver_lines.append({
                'approver_id': manager.id,
                'sequence': 10,
                'status': 'pending',  # Manager is first, so pending
                'role_name': 'Manager',
                'is_current_approver': True
            })
        
        # Add rule-based approvers
        if self.approval_rule_id:
            rule_lines = self._get_rule_based_approvers()
            approver_lines.extend(rule_lines)
        
        # Create approver lines
        for line_vals in approver_lines:
            line_vals['claim_id'] = self.id
            self.env['expense.approver.line'].create(line_vals)
    
    def _get_rule_based_approvers(self):
        """Get approvers based on approval rule"""
        rule = self.approval_rule_id
        approver_lines = []
        
        if rule.rule_type == 'sequential':
            # PDF Requirement: Sequential approval (Step 1 → Manager, Step 2 → Finance, Step 3 → Director)
            base_sequence = 20 if self.manager_approval_required else 10
            for rule_line in rule.approver_line_ids:
                status = 'pending' if not self.manager_approval_required and rule_line.sequence == rule.approver_line_ids[0].sequence else 'waiting'
                approver_lines.append({
                    'approver_id': rule_line.approver_id.id,
                    'sequence': base_sequence + rule_line.sequence,
                    'status': status,
                    'role_name': rule_line.role_name,
                    'is_current_approver': status == 'pending'
                })
        
        elif rule.rule_type in ['percentage', 'specific_approver', 'hybrid']:
            # PDF Requirement: Conditional approval (percentage, specific approver, or hybrid)
            base_sequence = 20 if self.manager_approval_required else 10
            
            if rule.rule_type in ['percentage', 'hybrid']:
                # Add all configured approvers for percentage-based approval
                for rule_line in rule.approver_line_ids:
                    status = 'pending' if not self.manager_approval_required else 'waiting'
                    approver_lines.append({
                        'approver_id': rule_line.approver_id.id,
                        'sequence': base_sequence,
                        'status': status,
                        'role_name': rule_line.role_name or 'Approver',
                        'is_current_approver': status == 'pending'
                    })
            
            if rule.rule_type in ['specific_approver', 'hybrid']:
                # Add specific approver (e.g., CFO)
                if rule.specific_approver_id:
                    status = 'pending' if not self.manager_approval_required else 'waiting'
                    approver_lines.append({
                        'approver_id': rule.specific_approver_id.id,
                        'sequence': base_sequence,
                        'status': status,
                        'role_name': 'Special Approver',
                        'is_current_approver': status == 'pending'
                    })
        
        return approver_lines
    
    def _start_approval_process(self):
        """Start the approval process"""
        # Set first approver as current
        first_approver = self.approver_line_ids.filtered('is_current_approver')
        if first_approver:
            self.current_approver_id = first_approver[0].approver_id
            self.state = 'waiting_approval'
    
    def action_approve(self):
        """PDF Requirement: Approve expense with proper workflow"""
        current_employee = self.env.user.employee_id
        if not current_employee:
            raise UserError("Current user is not linked to an employee record.")
        
        # Find current user's approver line
        approver_line = self.approver_line_ids.filtered(
            lambda x: x.approver_id.id == current_employee.id and x.status == 'pending'
        )
        
        if not approver_line:
            raise UserError("You are not authorized to approve this expense or it's not your turn yet.")
        
        # PDF Requirement: Approve with comments
        approver_line.write({
            'status': 'approved',
            'approval_date': fields.Datetime.now(),
            'is_current_approver': False
        })
        
        # PDF Requirement: Move to next approver or complete approval
        self._process_next_approval_step()
        
        self.message_post(
            body=f"Expense '{self.name}' approved by {current_employee.name}.",
            subject="Expense Approved"
        )

    def _process_next_approval_step(self):
        """PDF Requirement: Process next approval step or complete approval"""
        rule = self.approval_rule_id
        
        if not rule or rule.rule_type == 'sequential':
            # Sequential approval - move to next approver
            self._move_to_next_sequential_approver()
        else:
            # Conditional approval - check if conditions are met
            self._check_conditional_approval()
    
    def _move_to_next_sequential_approver(self):
        """PDF Requirement: Move to next approver in sequential approval"""
        # Find next waiting approver
        next_approver = self.approver_line_ids.filtered(
            lambda x: x.status == 'waiting'
        ).sorted('sequence')
        
        if next_approver:
            # Move to next approver
            next_approver[0].write({
                'status': 'pending',
                'is_current_approver': True
            })
            self.current_approver_id = next_approver[0].approver_id
            self.state = 'in_progress'
            
            # Notify next approver
            self.message_post(
                body=f"Expense '{self.name}' is now waiting for approval from {next_approver[0].approver_id.name}.",
                subject="Expense Approval Required"
            )
        else:
            # All approvers have approved
            self.state = 'approved'
            self.current_approver_id = False
            self.message_post(
                body=f"Expense '{self.name}' has been fully approved.",
                subject="Expense Fully Approved"
            )
    
    def _check_conditional_approval(self):
        """PDF Requirement: Check conditional approval rules"""
        rule = self.approval_rule_id
        approved_lines = self.approver_line_ids.filtered(lambda x: x.status == 'approved')
        total_lines = self.approver_line_ids
        
        is_approved = False
        
        if rule.rule_type == 'percentage':
            # PDF: If 60% of approvers approve → Expense approved
            approval_ratio = len(approved_lines) / len(total_lines) * 100
            is_approved = approval_ratio >= rule.approval_percentage
            
        elif rule.rule_type == 'specific_approver':
            # PDF: If CFO approves → Expense auto-approved
            specific_approved = approved_lines.filtered(
                lambda x: x.approver_id.id == rule.specific_approver_id.id
            )
            is_approved = bool(specific_approved)
            
        elif rule.rule_type == 'hybrid':
            # PDF: Combine both (e.g., 60% OR CFO approves)
            approval_ratio = len(approved_lines) / len(total_lines) * 100
            percentage_met = approval_ratio >= rule.approval_percentage
            
            specific_approved = approved_lines.filtered(
                lambda x: x.approver_id.id == rule.specific_approver_id.id
            )
            specific_met = bool(specific_approved)
            
            if rule.hybrid_logic == 'OR':
                is_approved = percentage_met or specific_met
            else:  # AND logic
                is_approved = percentage_met and specific_met
        
        if is_approved:
            self.state = 'approved'
            self.current_approver_id = False
            # Set remaining pending approvers to waiting
            self.approver_line_ids.filtered(lambda x: x.status == 'pending').write({
                'status': 'waiting',
                'is_current_approver': False
            })
            self.message_post(
                body=f"Expense '{self.name}' has been approved based on approval rule conditions.",
                subject="Expense Conditionally Approved"
            )
        else:
            # Continue waiting for more approvals
            self.state = 'in_progress'
    
    def action_reject(self):
        """PDF Requirement: Reject expense with comments"""
        current_employee = self.env.user.employee_id
        if not current_employee:
            raise UserError("Current user is not linked to an employee record.")
        
        approver_line = self.approver_line_ids.filtered(
            lambda x: x.approver_id.id == current_employee.id and x.status == 'pending'
        )
        
        if not approver_line:
            raise UserError("You are not authorized to reject this expense or it's not your turn yet.")
        
        # PDF Requirement: Reject with comments
        approver_line.write({
            'status': 'rejected',
            'approval_date': fields.Datetime.now(),
            'is_current_approver': False
        })
        
        # Any rejection stops the entire approval process
        self.state = 'rejected'
        self.current_approver_id = False
        
        # Set all other pending approvers to waiting
        self.approver_line_ids.filtered(lambda x: x.status == 'pending').write({
            'status': 'waiting',
            'is_current_approver': False
        })
        
        self.message_post(
            body=f"Expense '{self.name}' has been rejected by {current_employee.name}.",
            subject="Expense Rejected"
        )

    def _check_approval_complete(self):
        """Check if approval process is complete based on approval rule"""
        if not self.approval_rule_id:
            # If no rule, require all approvers to approve
            return all(line.status == 'approved' for line in self.approver_line_ids)
        
        rule = self.approval_rule_id
        approved_count = len(self.approver_line_ids.filtered(lambda x: x.status == 'approved'))
        total_count = len(self.approver_line_ids)
        
        if rule.rule_type == 'percentage':
            required_approvals = (rule.approval_percentage / 100) * total_count
            return approved_count >= required_approvals
        
        elif rule.rule_type == 'specific_user':
            specific_approved = self.approver_line_ids.filtered(
                lambda x: x.approver_id.id == rule.specific_approver_id.id and x.status == 'approved'
            )
            return bool(specific_approved)
        
        elif rule.rule_type == 'hybrid':
            percentage_met = approved_count >= ((rule.approval_percentage / 100) * total_count)
            specific_approved = bool(self.approver_line_ids.filtered(
                lambda x: x.approver_id.id == rule.specific_approver_id.id and x.status == 'approved'
            ))
            
            if rule.hybrid_logic == 'OR':
                return percentage_met or specific_approved
            else:  # AND logic
                return percentage_met and specific_approved
        
        return False

    def _process_receipt_ocr(self):
        """Process receipt using OCR functionality"""
        if not self.receipt_attachment_id:
            return
        
        try:
            # Import OCR controller function
            from ..controllers.ocr_controller import process_receipt_ocr
            ocr_data = process_receipt_ocr(self.receipt_attachment_id.id)
            
            # Update expense with OCR data if found
            if ocr_data.get('amount'):
                try:
                    extracted_amount = float(ocr_data['amount'])
                    if not self.amount_source:  # Only update if not already set
                        self.amount_source = extracted_amount
                except ValueError:
                    _logger.warning(f"Could not convert extracted amount '{ocr_data['amount']}' to float")
            
            if ocr_data.get('date') and not self.date:
                try:
                    from datetime import datetime
                    extracted_date = datetime.strptime(ocr_data['date'], '%Y-%m-%d').date()
                    self.date = extracted_date
                except ValueError:
                    _logger.warning(f"Could not parse extracted date '{ocr_data['date']}'")
            
            # Log vendor information
            if ocr_data.get('vendor'):
                self.message_post(
                    body=f"OCR detected vendor: {ocr_data['vendor']}",
                    subject="OCR Processing Complete"
                )
                
        except Exception as e:
            _logger.error(f"OCR processing failed: {str(e)}")
            self.message_post(
                body=f"OCR processing failed: {str(e)}",
                subject="OCR Processing Error"
            )

    @api.constrains('amount_source')
    def _check_amount_positive(self):
        for record in self:
            if record.amount_source <= 0:
                raise ValidationError("Expense amount must be positive.")

    @api.constrains('date')
    def _check_date_not_future(self):
        for record in self:
            if record.date > date.today():
                raise ValidationError("Expense date cannot be in the future.")


class HrEmployeeInherit(models.Model):
    """Extend HR Employee with expense management fields"""
    _inherit = 'hr.employee'

    # Core fields as per PDF requirements
    is_manager_approver = fields.Boolean(
        string='Is Manager Approver',
        help='Check this if the employee can approve expenses as a manager (first approval step)'
    )
    
    # Manager relationship for expense approval hierarchy
    expense_manager_id = fields.Many2one(
        'hr.employee',
        string='Expense Manager',
        help='Manager who approves this employee\'s expenses'
    )
    
    # Role in expense management
    expense_role = fields.Selection([
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Admin')
    ], string='Expense Role', default='employee', required=True)
    
    # User management capabilities
    def create_employee_user(self, name, email, role='employee'):
        """Create user for employee with proper role"""
        user_vals = {
            'name': name,
            'login': email,
            'email': email,
            'groups_id': [(6, 0, self._get_expense_groups(role))]
        }
        user = self.env['res.users'].create(user_vals)
        
        employee_vals = {
            'name': name,
            'work_email': email,
            'user_id': user.id,
            'expense_role': role
        }
        
        if role == 'manager':
            employee_vals['is_manager_approver'] = True
            
        return self.create(employee_vals)
    
    def _get_expense_groups(self, role):
        """Get security groups based on role"""
        group_mapping = {
            'employee': [self.env.ref('hackathon_expense_management.group_expense_employee').id],
            'manager': [self.env.ref('hackathon_expense_management.group_expense_manager').id],
            'admin': [self.env.ref('hackathon_expense_management.group_expense_admin').id]
        }
        return group_mapping.get(role, [])
