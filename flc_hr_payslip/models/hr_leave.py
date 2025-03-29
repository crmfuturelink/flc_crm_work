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
    emergency_reason = fields.Text(string="Reason for Emergency", help="Required if applying without advance notice.")
    leave_type = fields.Selection([('full_day', 'Full Day Leave'), ('half_day', 'Half Day Leave'),
                                   ('sick', 'Sick Leave'), ('comp_off', 'Compensatory Off')], string="Leave Type",
                                  required=True, default="full_day")
    leave_status = fields.Selection([
        ('draft', 'To Submit'),
        ('submitted', 'Submitted'),
        ('approved_paid', 'Approved Paid Leave'),
        ('approved_unpaid', 'Approved Unpaid Leave'),
        ('unapproved', 'Unapproved Leave'),
        ('approved_half_day', 'Approved Half Day Leave'),
        ('unapproved_half_day', 'Unapproved Half Day Leave'),
        ('approved_comp_off', 'Approved Comp Off'),
        ('unapproved_comp_off', 'Unapproved Comp Off')
    ], string="Leave Status", default='draft')

    is_comp_off = fields.Boolean(string="Is Compensatory Off?", compute="_compute_is_comp_off")

    @api.depends('leave_type')
    def _compute_is_comp_off(self):
        for record in self:
            record.is_comp_off = True if record.leave_type == 'comp_off' else False

    def action_submit(self):
        """Submit the leave request"""
        print("\n action_submit::::::::::::::::;:::::")
        self.write({'leave_status': 'submitted'})

    def action_approve_paid(self):
        """Approve as Paid Leave"""
        self.write({'leave_status': 'approved_paid'})

    def action_approve_unpaid(self):
        """Approve as Unpaid Leave"""
        self.write({'leave_status': 'approved_unpaid'})

    def action_approve_half_day(self):
        """Approve as Half Day Leave"""
        self.write({'leave_status': 'approved_half_day'})

    def action_unapprove_half_day(self):
        """Unapprove Half Day Leave"""
        self.write({'leave_status': 'unapproved_half_day'})

    def action_unapprove(self):
        """Unapprove Leave"""
        self.write({'leave_status': 'unapproved'})

    def action_approve_comp_off(self):
        """Approve Compensatory Off Leave"""
        self.write({'leave_status': 'approved_comp_off'})

    def action_unapprove_comp_off(self):
        """Unapprove Compensatory Off Leave"""
        self.write({'leave_status': 'unapproved_comp_off'})


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

    @api.constrains('date_from', 'date_to', 'number_of_days', 'emergency_reason')
    def _check_leave_submission_timing(self):
        """Enforce advance leave request policy unless an emergency reason is provided."""
        for leave in self:
            today = date.today()
            days_in_advance = (leave.date_from.date() - today).days

            if not leave.emergency_reason:  # Skip validation if a reason is provided
                if 1 <= leave.number_of_days <= 3 and days_in_advance < 7:
                    raise ValidationError(
                        "Leave requests for 1 to 3 days must be submitted at least 1 week in advance, unless it's an emergency.")

                elif leave.number_of_days >= 4 and days_in_advance < 30:
                    raise ValidationError(
                        "Leave requests for 4 or more days must be submitted at least 1 month in advance, unless it's an emergency.")

    def action_approve(self):
        """ Override approval process to track annual leave usage """
        res = super(HRLeave, self).action_approve()

        for leave in self:
            emp = leave.employee_id

            # If it's an annual leave, update monthly usage tracker
            if leave.holiday_status_id.name == "Annual Leave":
                emp.used_annual_leaves_this_month += 1

        return res
