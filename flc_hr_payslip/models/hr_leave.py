from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError

class HRLeave(models.Model):
    _inherit = "hr.leave"

    approval_status = fields.Selection([
        ('approved_paid', 'Approved Paid Leave'),
        ('approved_unpaid', 'Approved Unpaid Leave'),
        ('unapproved', 'Unapproved Leave'),
        ('approved_half_day', 'Approved Half Day Leave'),
        ('unapproved_half_day', 'Unapproved Half Day Leave')
    ], string="Approval Status", default='unapproved')

    # @api.constrains('number_of_days', 'holiday_status_id', 'employee_id')
    # def check_leave_balance(self):
    #     """ Restrict annual leave usage to 1 per month """
    #     for leave in self:
    #         emp = leave.employee_id
    #
    #         if leave.holiday_status_id.name == "Annual Leave":
    #             if emp.used_annual_leaves_this_month >= 1:
    #                 raise ValidationError(f"{emp.name} has already used 1 annual leave this month.")
    #
    #         if leave.number_of_days not in [0.5, 1.0, 1.5]:
    #             raise ValidationError("Only 0.5, 1.0, or 1.5 days can be applied at a time.")

    # @api.constrains('date_from', 'date_to', 'number_of_days')
    # def _check_leave_submission_timing(self):
    #     """Enforce advance leave request policy based on leave duration"""
    #     for leave in self:
    #         today = date.today()
    #         days_in_advance = (leave.date_from.date() - today).days
    #
    #         if leave.number_of_days <= 3:
    #             if days_in_advance < 7:
    #                 raise ValidationError(
    #                     "Leave requests for 1 to 3 days must be submitted at least 1 week in advance.")
    #
    #         elif leave.number_of_days >= 4:
    #             if days_in_advance < 30:
    #                 raise ValidationError(
    #                     "Leave requests for 4 or more days must be submitted at least 1 month in advance.")

    def action_approve(self):
        """ Override approval process to track annual leave usage """
        res = super(HRLeave, self).action_approve()

        for leave in self:
            emp = leave.employee_id

            # If it's an annual leave, update monthly usage tracker
            if leave.holiday_status_id.name == "Annual Leave":
                emp.used_annual_leaves_this_month += 1

        return res
