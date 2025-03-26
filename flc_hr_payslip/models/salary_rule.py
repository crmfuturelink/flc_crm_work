from odoo import models, fields, api
from datetime import date

class SalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    attendance_based = fields.Boolean(
        string="Attendance Based",
        default=False,
        help="If checked, this rule will be calculated based on attendance"
    )

    def _compute_rule(self, localdict):
        """Override to apply attendance factor to attendance-based rules"""
        self.ensure_one()

        if self.attendance_based and 'contract' in localdict:
            employee = localdict.get('employee')
            payslip = localdict.get('payslip')

            if employee and employee.attendance_based_pay and payslip:
                attendance_factor = 0
                if payslip.total_working_days > 0:
                    attendance_factor = payslip.days_worked / payslip.total_working_days

                # Calculate amount with attendance factor
                amount = super(SalaryRule, self)._compute_rule(localdict)
                return amount * attendance_factor

        return super(SalaryRule, self)._compute_rule(localdict)