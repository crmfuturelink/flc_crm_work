from odoo import models, fields

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
    employee_type_id = fields.Many2one('hr.contract.type', string="Employee Type", help="Employee Contract Type")
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

