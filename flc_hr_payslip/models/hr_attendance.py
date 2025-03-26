from odoo import models, fields


class HRAttendance(models.Model):
    _inherit = "hr.attendance"

    is_late = fields.Boolean(string="Late Arrival")
    is_break_exceeded = fields.Boolean(string="Overstayed Break")

    check_in = fields.Datetime(string="Check In")  # Ensure correct type
    attendance_date = fields.Date(string="Attendance Date")  # Renamed field
    total_hours = fields.Float(string="Total Hours")
    work_date = fields.Datetime(string="Work Date")

