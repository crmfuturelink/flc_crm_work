# models/hr_employee_type.py
from odoo import models, fields, api


class HrEmployeeType(models.Model):
    _name = 'hr.employee.type'
    _description = 'Employee Type'

    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')

    # Leave Policy Fields
    paid_leave_eligible = fields.Boolean(string='Eligible for Paid Leave', default=False)
    paid_leave_per_month = fields.Float(string='Paid Leaves Per Month', default=0.0)
    festival_leave_eligible = fields.Boolean(string='Eligible for Festival Leave', default=False)

    # Work Schedule
    default_work_schedule_id = fields.Many2one('hr.work.schedule', string='Default Work Schedule')

    # Probation Settings
    probation_required = fields.Boolean(string='Probation Required', default=True)
    probation_period_months = fields.Integer(string='Probation Period (Months)', default=3)

    active = fields.Boolean(default=True)

    @api.model
    def _get_full_time_mon_sat_type(self):
        return self.env.ref('flc_hr_management.employee_type_full_time_mon_sat')

    @api.model
    def _get_full_time_mon_fri_type(self):
        return self.env.ref('flc_hr_management.employee_type_full_time_mon_fri')

    @api.model
    def _get_part_time_type(self):
        return self.env.ref('flc_hr_management.employee_type_part_time')

    @api.model
    def _get_intern_type(self):
        return self.env.ref('flc_hr_management.employee_type_intern')

    @api.model
    def _get_contract_type(self):
        return self.env.ref('flc_hr_management.employee_type_contract')