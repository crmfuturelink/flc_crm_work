# models/hr_probation.py
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class HrProbation(models.Model):
    _name = 'hr.probation'
    _description = 'Employee Probation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date'

    name = fields.Char(string='Reference', readonly=True, copy=False, default='New')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one(related='employee_id.department_id', store=True)
    job_id = fields.Many2one(related='employee_id.job_id', store=True)

    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)

    state = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('to_review', 'To Review'),
        ('extended', 'Extended'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ], string='Status', default='ongoing', tracking=True)

    original_end_date = fields.Date(string='Original End Date', readonly=True)
    extension_date = fields.Date(string='Extension Date')
    extension_reason = fields.Text(string='Extension Reason')

    review_date = fields.Date(string='Review Date')
    reviewed_by_id = fields.Many2one('res.users', string='Reviewed By')
    review_notes = fields.Text(string='Review Notes')

    days_left = fields.Integer(string='Days Left', compute='_compute_days_left', store=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.probation') or 'New'
        if vals.get('end_date') and not vals.get('original_end_date'):
            vals['original_end_date'] = vals['end_date']
        return super(HrProbation, self).create(vals)

    @api.depends('end_date')
    def _compute_days_left(self):
        today = fields.Date.today()
        for probation in self:
            if probation.end_date:
                delta = (probation.end_date - today).days
                probation.days_left = delta if delta > 0 else 0
            else:
                probation.days_left = 0

    @api.model
    def _cron_check_probation_ending_soon(self):
        """Scheduled action to check probations ending in 7 days"""
        today = fields.Date.today()
        one_week_later = today + timedelta(days=7)

        probations = self.search([
            ('state', '=', 'ongoing'),
            ('end_date', '<=', one_week_later),
            ('end_date', '>=', today),
        ])

        for probation in probations:
            # Only update to 'to_review' if not already there
            if probation.state == 'ongoing':
                probation.write({'state': 'to_review'})

            # Create notification for manager
            manager = probation.employee_id.parent_id.user_id
            if manager:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'note': f"Probation period for {probation.employee_id.name} is ending on {probation.end_date}. Please review.",
                    'user_id': manager.id,
                    'res_id': probation.id,
                    'res_model_id': self.env['ir.model']._get('hr.probation').id,
                    'summary': 'Probation Review Required',
                    'date_deadline': probation.end_date,
                })

    def action_complete_probation(self):
        self.ensure_one()
        self.write({
            'state': 'completed',
            'review_date': fields.Date.today(),
            'reviewed_by_id': self.env.user.id,
        })
        # Trigger leave allocation for eligible employees
        if self.employee_id.employee_type_id.paid_leave_eligible:
            self._create_paid_leave_allocation()

        return True

    def action_extend_probation(self):
        self.ensure_one()
        return {
            'name': 'Extend Probation',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.probation.extend.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_probation_id': self.id}
        }

    def _create_paid_leave_allocation(self):
        """Create leave allocation for employee after probation completion"""
        allocation = self.env['hr.leave.allocation'].create({
            'name': f"Automatic Allocation for {self.employee_id.name}",
            'holiday_status_id': self.env.ref('flc_hr_management.holiday_status_paid_leave').id,
            'employee_id': self.employee_id.id,
            'number_of_days': self.employee_id.employee_type_id.paid_leave_per_month,
            'allocation_type': 'regular',
            'state': 'validate',
        })
        return allocation


class HrProbationExtendWizard(models.TransientModel):
    _name = 'hr.probation.extend.wizard'
    _description = 'Probation Extension Wizard'

    probation_id = fields.Many2one('hr.probation', string='Probation', required=True)
    extension_date = fields.Date(string='New End Date', required=True)
    extension_reason = fields.Text(string='Reason for Extension', required=True)

    @api.onchange('probation_id')
    def _onchange_probation_id(self):
        if self.probation_id:
            self.extension_date = self.probation_id.end_date + relativedelta(months=1)

    def action_extend(self):
        self.ensure_one()
        self.probation_id.write({
            'end_date': self.extension_date,
            'extension_date': self.extension_date,
            'extension_reason': self.extension_reason,
            'state': 'extended',
            'review_date': fields.Date.today(),
            'reviewed_by_id': self.env.user.id,
        })
        return {'type': 'ir.actions.act_window_close'}