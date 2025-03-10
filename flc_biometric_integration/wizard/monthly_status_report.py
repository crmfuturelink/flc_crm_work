from odoo import models, fields, api

class MonthlyStatusReportWizard(models.TransientModel):
    _name = 'monthly.status.report.wizard'
    _description = 'Monthly Status Report Wizard'

    department_id = fields.Many2one('hr.department', string="Department")
    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    report_data = fields.Date(string="Report Date")

    # def action_view_report(self):
    #     """This method will return an action to show the report in a popup view."""
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Monthly Status Report',
    #         'res_model': 'monthly.status.report.wizard',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('flc_biometric_integration.view_report_popup_form').id,
    #         'target': 'new',  # Open as a popup
    #         'context': self._context,
    #     }
    def action_view_report(self):
        """Method to generate and download the Biometric Attendance PDF report."""
        return self.env.ref('flc_biometric_integration.action_biometric_attendance_report').report_action(self)

    # def action_view_report(self):

        # """Method to open the report popup with selected date range."""
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Monthly Status Report',
        #     'res_model': 'monthly.status.report.wizard',
        #     'view_mode': 'form',
        #     'view_id': self.env.ref('flc_biometric_integration.view_report_popup_form').id,
        #     'target': 'new',
        #     'context': {
        #         'default_start_date': self.from_date,
        #         'default_end_date': self.to_date,
        #     },
        # }

