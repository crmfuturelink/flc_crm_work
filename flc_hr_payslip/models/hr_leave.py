from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError

class HRLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains('number_of_days', 'holiday_status_id', 'employee_id')
    def check_leave_balance(self):
        """ Restrict annual leave usage to 1 per month """
        for leave in self:
            emp = leave.employee_id

            if leave.holiday_status_id.name == "Annual Leave":
                if emp.used_annual_leaves_this_month >= 1:
                    raise ValidationError(f"{emp.name} has already used 1 annual leave this month.")

            if leave.number_of_days not in [0.5, 1.0, 1.5]:
                raise ValidationError("Only 0.5, 1.0, or 1.5 days can be applied at a time.")

    def action_approve(self):
        """ Override approval process to track annual leave usage """
        res = super(HRLeave, self).action_approve()

        for leave in self:
            emp = leave.employee_id

            # If it's an annual leave, update monthly usage tracker
            if leave.holiday_status_id.name == "Annual Leave":
                emp.used_annual_leaves_this_month += 1

        return res
