from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import AccessError


class HrProbationWizard(models.TransientModel):
    _name = 'hr.probation.wizard'
    _description = 'Employee Probation Approval'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True)
    probation_status = fields.Selection([('pending', 'Pending'), ('completed', 'Completed'), ('extended', 'Extended')
                                         ], string="Probation Status", default='pending', tracking=True)
    extended_probation_date = fields.Date(string="Extended Probation Date", tracking=True)
    extend_option = fields.Selection(
        [('1w', 'Extend by 1 Week'), ('1m', 'Extend by 1 Month'), ('3m', 'Extend by 3 Months')
         ], string="Extension Period", tracking=True)

    def confirm_action(self):
        """Confirm probation completion"""
        if self.employee_id.parent_id.user_id != self.env.user:
            raise AccessError("Only the employee's reporting manager can approve or extend probation.")

        if self.probation_status == 'completed':
            self.employee_id.write({
                'probation_status': 'completed',
                'confirmation_date': fields.Date.today()
            })

        return {'type': 'ir.actions.act_window_close'}

    def extended_date(self):
        """Extend probation based on selected option"""
        if self.employee_id.parent_id.user_id != self.env.user:
            raise AccessError("Only the employee's reporting manager can extend probation.")

        extension_days = {'1w': 7, '1m': 30, '3m': 90}.get(self.extend_option, 0)

        new_date = self.employee_id.probation_end_date + timedelta(days=extension_days)

        self.employee_id.with_context(force_update=True).write({
            'probation_status': 'extended',
            'extend_option': self.extend_option,
            'extended_probation_date': new_date
        })
        return {'type': 'ir.actions.act_window_close'}
