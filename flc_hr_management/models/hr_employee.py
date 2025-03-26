# models/hr_employee.py
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Employee Type Fields
    employee_type = fields.Selection([('full_time', 'Full-Time'),
                                      ('part_time', 'Part-Time'),
                                      ('intern', 'Intern'),
                                      ('contract', 'Contract-Based')
                                      ], string="Employee Type", required=False)
    #
    # employee_type_id = fields.Many2one('hr.employee.type', string='Employee Type', tracking=True)
    # work_schedule_id = fields.Many2one('hr.work.schedule', string='Work Schedule', tracking=True)
    #
    # # Probation Fields
    # probation_id = fields.Many2one('hr.probation', string='Current Probation', compute='_compute_probation')
    # probation_state = fields.Selection(related='probation_id.state', string='Probation Status')
    # probation_end_date = fields.Date(related='probation_id.end_date', string='Probation End Date')
    # probation_days_left = fields.Integer(related='probation_id.days_left', string='Probation Days Left')
    # is_probation_completed = fields.Boolean(string='Probation Completed', compute='_compute_is_probation_completed',
    #                                         store=True)
    #
    # # Attendance and Leave Tracking Fields
    # current_month_late_count = fields.Integer(string='Late Arrivals This Month', compute='_compute_attendance_stats')
    # current_month_excess_breaks = fields.Integer(string='Excess Breaks This Month', compute='_compute_attendance_stats')
    #
    # # Fields for leave policy
    # paid_leave_eligible = fields.Boolean(related='employee_type_id.paid_leave_eligible',
    #                                      string='Eligible for Paid Leave')
    # paid_leave_balance = fields.Float(string='Paid Leave Balance', compute='_compute_leave_balances')
    # unpaid_leave_balance = fields.Float(string='Unpaid Leave Balance', compute='_compute_leave_balances')
    #
    # # Reporting Time
    # reporting_time = fields.Float(string='Reporting Time', default=10.0)  # Default 10:00 AM
    # end_time = fields.Float(string='End Time', default=19.0)  # Default 7:00 PM
    #
    # @api.depends('employee_type_id')
    # def _compute_is_probation_completed(self):
    #     for employee in self:
    #         if employee.probation_state in ['completed', False]:
    #             employee.is_probation_completed = True
    #         else:
    #             employee.is_probation_completed = False
    #
    # @api.model
    # def create(self, vals):
    #     employee = super(HrEmployee, self).create(vals)
    #
    #     # Set default work schedule based on employee type
    #     if employee.employee_type_id and employee.employee_type_id.default_work_schedule_id and not employee.work_schedule_id:
    #         employee.work_schedule_id = employee.employee_type_id.default_work_schedule_id.id
    #
    #     # Create probation record if required
    #     if employee.employee_type_id and employee.employee_type_id.probation_required:
    #         probation_months = employee.employee_type_id.probation_period_months
    #         start_date = fields.Date.today()
    #         end_date = start_date + relativedelta(months=probation_months)
    #
    #         self.env['hr.probation'].create({
    #             'employee_id': employee.id,
    #             'start_date': start_date,
    #             'end_date': end_date,
    #             'state': 'ongoing',
    #         })
    #
    #     return employee
    #
    # @api.onchange('employee_type_id')
    # def _onchange_employee_type_id(self):
    #     if self.employee_type_id and self.employee_type_id.default_work_schedule_id:
    #         self.work_schedule_id = self.employee_type_id.default_work_schedule_id
    #         self.reporting_time = self.work_schedule_id.start_time
    #         self.end_time = self.work_schedule_id.end_time
    #
    # def _compute_probation(self):
    #     for employee in self:
    #         probation = self.env['hr.probation'].search([
    #             ('employee_id', '=', employee.id),
    #             ('state', 'in', ['ongoing', 'to_review', 'extended'])
    #         ], limit=1)
    #         employee.probation_id = probation.id if probation else False
    #
    # def _compute_attendance_stats(self):
    #     today = fields.Date.today()
    #     first_day = today.replace(day=1)
    #
    #     for employee in self:
    #         # Count late arrivals this month
    #         late_attendances = self.env['hr.attendance'].search_count([
    #             ('employee_id', '=', employee.id),
    #             ('check_in', '>=', first_day),
    #             ('check_in', '<=', today),
    #             ('is_late', '=', True)
    #         ])
    #
    #         # Consider the 3 free late arrivals policy
    #         employee.current_month_late_count = max(0, late_attendances - 3)
    #
    #         # Count excess breaks
    #         excess_breaks = self.env['hr.lunch.break'].search_count([
    #             ('employee_id', '=', employee.id),
    #             ('date', '>=', first_day),
    #             ('date', '<=', today),
    #             ('is_excess', '=', True)
    #         ])
    #         employee.current_month_excess_breaks = excess_breaks
    #
    # def _compute_leave_balances(self):
    #     today = fields.Date.today()
    #
    #     for employee in self:
    #         # Compute paid leave balance
    #         paid_leave_type = self.env.ref('flc_hr_management.holiday_status_paid_leave', False)
    #         if paid_leave_type and employee.is_probation_completed and employee.paid_leave_eligible:
    #             leaves = self.env['hr.leave.allocation'].search([
    #                 ('employee_id', '=', employee.id),
    #                 ('holiday_status_id', '=', paid_leave_type.id),
    #                 ('state', '=', 'validate'),
    #             ])
    #             allocated = sum(leaves.mapped('number_of_days'))
    #
    #             used_leaves = self.env['hr.leave'].search([
    #                 ('employee_id', '=', employee.id),
    #                 ('holiday_status_id', '=', paid_leave_type.id),
    #                 ('state', '=', 'validate'),
    #             ])
    #             used = sum(used_leaves.mapped('number_of_days'))
    #
    #             employee.paid_leave_balance = allocated - used
    #         else:
    #             employee.paid_leave_balance = 0.0
    #
    #         # For simplicity, setting unpaid leave balance to 0
    #         # In reality, this would depend on specific business logic
    #         employee.unpaid_leave_balance = 0.0