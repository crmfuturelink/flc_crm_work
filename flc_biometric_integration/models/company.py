# -*- coding: utf-8 -*-
###############################################################################
#
#    Future Link Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Future Link Pvt. Ltd. (<https://futurelinkconsultants.com>)
#    Author: Ranjan  (crmdeveloper@futurelinkconsultants.com)
#
#
###############################################################################
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    work_start_time = fields.Char(string="Work Start Time", default="09:00", help="Format: HH:MM")
    work_end_time = fields.Char(string="Work End Time", default="18:00", help="Format: HH:MM")
    late_tolerance_mins = fields.Integer(string="Late Tolerance (mins)", default=15)
    early_departure_tolerance_mins = fields.Integer(string="Early Departure Tolerance (mins)", default=15)
    minimum_full_day_hours = fields.Float(string="Minimum Hours for Full Day", default=7.5)

    # Add related fields to sync with res.company
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    def set_values(self):
        """Save values to res.company when settings are changed."""
        super().set_values()
        self.env.company.write({
            'work_start_time': self.work_start_time,
            'work_end_time': self.work_end_time,
            'late_tolerance_mins': self.late_tolerance_mins,
            'early_departure_tolerance_mins': self.early_departure_tolerance_mins,
            'minimum_full_day_hours': self.minimum_full_day_hours,
        })

    @staticmethod
    def get_values(self):
        """Retrieve values from res.company when loading settings."""
        res = super(ResConfigSettings, ResConfigSettings).get_values()
        company = self.env.company
        res.update({
            'work_start_time': company.work_start_time,
            'work_end_time': company.work_end_time,
            'late_tolerance_mins': company.late_tolerance_mins,
            'early_departure_tolerance_mins': company.early_departure_tolerance_mins,
            'minimum_full_day_hours': company.minimum_full_day_hours,
        })
        return res
