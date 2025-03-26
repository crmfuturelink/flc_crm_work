# models/hr_work_schedule.py
from odoo import models, fields, api


class HrWorkSchedule(models.Model):
    _name = 'hr.work.schedule'
    _description = 'Work Schedule'

    name = fields.Char(string='Schedule Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')

    # Working Days
    monday = fields.Boolean(string='Monday', default=True)
    tuesday = fields.Boolean(string='Tuesday', default=True)
    wednesday = fields.Boolean(string='Wednesday', default=True)
    thursday = fields.Boolean(string='Thursday', default=True)
    friday = fields.Boolean(string='Friday', default=True)
    saturday = fields.Boolean(string='Saturday', default=False)
    sunday = fields.Boolean(string='Sunday', default=False)

    # Working Hours
    work_hours_per_day = fields.Float(string='Work Hours Per Day', default=8.0)
    start_time = fields.Float(string='Start Time', default=10.0)  # 10:00 AM
    end_time = fields.Float(string='End Time', default=19.0)  # 7:00 PM

    # Lunch Breaks
    lunch_break_1_start = fields.Float(string='Lunch Break 1 Start', default=13.0)  # 1:00 PM
    lunch_break_1_end = fields.Float(string='Lunch Break 1 End', default=13.75)  # 1:45 PM
    lunch_break_2_start = fields.Float(string='Lunch Break 2 Start', default=13.75)  # 1:45 PM
    lunch_break_2_end = fields.Float(string='Lunch Break 2 End', default=14.5)  # 2:30 PM

    # Grace Period (in minutes)
    grace_period = fields.Integer(string='Grace Period (minutes)', default=15)

    # Calculated Fields
    hours_per_week = fields.Float(string='Hours Per Week', compute='_compute_hours_per_week', store=True)

    active = fields.Boolean(default=True)

    @api.depends('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'work_hours_per_day')
    def _compute_hours_per_week(self):
        for schedule in self:
            working_days = sum([
                schedule.monday, schedule.tuesday, schedule.wednesday,
                schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday
            ])
            schedule.hours_per_week = working_days * schedule.work_hours_per_day

    def _float_time_to_str(self, float_time):
        """Convert float time (e.g., 13.5 for 1:30 PM) to string format (13:30)"""
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def get_work_days_list(self):
        """Return a list of working days as integers (0 = Monday, 6 = Sunday)"""
        self.ensure_one()
        work_days = []
        if self.monday:
            work_days.append(0)
        if self.tuesday:
            work_days.append(1)
        if self.wednesday:
            work_days.append(2)
        if self.thursday:
            work_days.append(3)
        if self.friday:
            work_days.append(4)
        if self.saturday:
            work_days.append(5)
        if self.sunday:
            work_days.append(6)
        return work_days