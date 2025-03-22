from odoo import models, fields,api
from datetime import date, timedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_category = fields.Selection([
        ('consultant', 'Consultant'),
        ('education', 'Education-Based')
    ], string="Employee Category", default='consultant')
    provident_fund = fields.Float(string='Provident Fund')
    employee_esic = fields.Float(string='ESIC')
    professional_tax  = fields.Float(string='Professional Tax ')
    employee_doj  = fields.Char(string='Date of Joining')
    aadhar_no  = fields.Char(string='Aadhar No')
    pf_no  = fields.Char(string='PF No')
    uan_no  = fields.Char(string='UAN No')
    eisc_no  = fields.Char(string='EISC No')
    branch_id = fields.Many2one('res.branch', string="Branch")
    has_weekend_off = fields.Boolean(string="Has Saturday-Sunday Off")
    last_leave_allocation = fields.Date(string="Last Leave Allocation Date", default=False)
    annual_leave_balance = fields.Float(string="Annual Leave Balance", default=0.0)
    used_annual_leaves_this_month = fields.Integer(string="Used Monthly Leaves This Month", default=0)

    ##hr.contract.type###
    """
     ######We have four types of employees with different leave policies:
    -------------------------------------------------------------------------
    A . Full-Time(Mon-Sat) - Employees- Monday to Saturday
       * Get 1.5 paid leaves per month after completing 3 months of probation.
       
    B. Full-Time(Mon-Fri)
       * Employees with Saturday and Sunday off do not receive 1.5 paid leaves.
       
    C. Part-Time Employees
       * Do not receive paid leave or festival leave.
       
    d. Interns
      * Do not receive paid leave.
      
    e . Contract Basis Employees
     * Do not receive 1.5 paid leaves
     * Paid based on work hours (pro-rata basis).
    ----------------------------------------------
    """
    employee_type_id = fields.Many2one('hr.contract.type', string="Work Type", help="Employee Contract Type")
    employee_type = fields.Selection([
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('intern', 'Intern'),
        ('contract', 'Contract Basis'),
    ], string="Employee Type", required=True)
    """
    FLC CRM - Employee Stages Module

    - Adds Employee Stages in Odoo HR.
    - Displays employee stages as a status bar.
    - Allows stage transitions directly from the employee form.
    """
    stage = fields.Selection([
        ('new', 'New / Joined'),
        ('training', 'Training'),
        ('probation', 'Probation'),
        ('employment', 'Employment'),
        ('pip', 'PIP'),
        ('notice_period', 'Notice Period'),
        ('relieved', 'Relieved'),
        ('rejoined', 'Rejoined'),
    ], string="Employee Stage", default="new", tracking=True)

    @api.model
    def check_probation_status(self):
        """ Cron job to check probation completion and notify managers """
        today = date.today()
        print("today :::::", today)
        employees = self.search([
            ('stage', '=', 'probation'),
            ('joining_date', '<=', today)])
        print("employee :::::", employees)
        for emp in employees:
            emp._notify_managers_about_probation()

    def _notify_managers_about_probation(self):
        """Notify the reporting manager when an employee completes 3 months probation."""
        # three_months_ago = date.today() - timedelta(days=90)
        # employees = self.search([('joining_date', '=', three_months_ago)])
        #
        # for emp in employees:
        if self.parent_id:  # Reporting Manager exists
            message = f"Employee {self.name} joining date{self.joining_date}  has completed their 3-month probation period ."
            print("message :::::", message)
            self.parent_id.message_post(body=message, subtype_xmlid="mail.mt_comment", partner_ids=[self.parent_id.id])

    @api.model
    def reset_monthly_leave_limit(self):
        """ Reset annual leave usage counter and set annual_leave_balance to 0 at the start of each month """
        employees = self.search([])
        employees.write({
            'used_annual_leaves_this_month': 0,  # Reset used monthly leaves
            'annual_leave_balance': 0  # Reset annual leave balance
        })

    def allocate_monthly_leaves(self):
        """ Automatically allocate 1.5 leave every month for full-time employees """
        print("allocate_monthly_leaves::::::::::::::::::", self, self._context)
        today = date.today()

        # Retrieve all full-time employees who have no weekend off
        employees = self.env['hr.employee'].search([
            ('employee_type', '=', 'full_time'),
            ('stage', '=', 'employment'),
            ('has_weekend_off', '=', False)  # Only Mon-Sat employees eligible
        ])
        for emp in employees:
            # Skip if leave has already been allocated this month
            if emp.last_leave_allocation and emp.last_leave_allocation.month == today.month:
                continue  # Already allocated this month

            # Find the leave type 'Full Day Leave'
            leave_type = self.env['hr.leave.type'].search([('name', '=', 'Full Day Leave')], limit=1)

            if not leave_type:
                raise ValueError("Leave Type 'Full Day Leave' is missing. Please configure it in Odoo.")
            # Auto-allocate leave without approval
            self.env['hr.leave.allocation'].create({
                'name': f'Monthly Paid Leave for {emp.name}',
                'holiday_status_id': leave_type.id,
                'employee_id': emp.id,
                'number_of_days': 1.5,
                'state': 'confirm',  # Automatically approved
            })

            # Update the last leave allocation date
            emp.write({'last_leave_allocation': today, 'annual_leave_balance':1.5})
            # Notify Employee
            emp.message_post(
                body=f"You have been granted 1.5 days of leave for {today.strftime('%B')}.",
                subtype_xmlid="mail.mt_comment"
            )

            # Notify Manager
            if emp.parent_id:
                emp.parent_id.message_post(
                    body=f"{emp.name} has received 1.5 days of leave for {today.strftime('%B')}.",
                    subtype_xmlid="mail.mt_comment"
                )

        return True
