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

from odoo import models, fields, api
import requests
from lxml import etree

class BiometricTerminal(models.Model):
    _name = 'biometric.terminal'
    _description = 'Biometric Terminal'

    name = fields.Char("Branch Name", required=True)
    serial_number = fields.Char("Serial Number", required=True)
    branch = fields.Char("Branch Description")
    branch_contact = fields.Char("IT/Branch Manger")
    branch_phone = fields.Char("Branch Phone")
    branch_email = fields.Char("Branch Email")
    username = fields.Char("Username", required=True)
    password = fields.Char("Password", required=True)

    def action_biometric_attendance_wizard(self):
        """Opens the Fetch Biometric Attendance Wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fetch Biometric Attendance Logs',
            'res_model': 'biometric.attendance.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('flc_biometric_integration.view_biometric_attendance_wizard_form').id,
            'target': 'new',
        }

class BiometricAttendanceLog(models.Model):
    _name = 'biometric.attendance.log'
    _description = 'Biometric Attendance Log'
    _rec_name = 'employee_name'
    _order = 'attendance_date desc, employee_id'

    employee_name = fields.Char("Employee Name", compute="_compute_employee_name", store=True)
    attendance_date = fields.Date("Attendance Date", compute="_compute_attendance_date", store=True)
    user_id = fields.Char(string="Employee ID")
    log_time = fields.Datetime("Log Time")
    terminal_id = fields.Many2one('biometric.terminal', "Branch")
    attendance_type = fields.Selection([('in', 'Check-In'), ('out', 'Check-Out')], "Type")
    employee_id = fields.Many2one('hr.employee', string="Employee")

    # Daily summary fields
    first_check_in = fields.Datetime("First Check-In", compute="_compute_attendance_summary", store=True)
    last_check_out = fields.Datetime("Last Check-Out", compute="_compute_attendance_summary", store=True)
    all_logs = fields.Text("Log Details", compute="_compute_attendance_summary")

    # New fields for better reporting
    total_hours = fields.Float("Total Hours", compute="_compute_attendance_summary", store=True)
    is_first_record = fields.Boolean("Is First Record", compute="_compute_attendance_summary", store=True)
    summary_record_id = fields.Many2one('biometric.attendance.log', "Summary Record", compute="_compute_summary_record",
                                        store=True)
    attendance_logs = fields.One2many('biometric.attendance.log.line', 'attendance_log_id', string="Attendance Logs")

    def get_attendance_for_day(self, day):
        """Return attendance status for the given day"""
        log = self.attendance_logs.filtered(lambda l: l.attendance_date.day == day)
        if log:
            return log.status  # 'P' for Present, 'A' for Absent, 'L' for Leave
        return '-'

    def print_attendance_report(self):
        """Generate the PDF report"""
        return self.env.ref('flc_biometric_integration.action_biometric_attendance_report').report_action(self)

    @api.depends('log_time')
    def _compute_attendance_date(self):
        """Compute the date from the log timestamp"""
        for record in self:
            if record.log_time:
                record.attendance_date = record.log_time.date()
            else:
                record.attendance_date = False

    @api.depends('employee_id')
    def _compute_employee_name(self):
        """Store the employee name for better performance in reports"""
        for record in self:
            record.employee_name = record.employee_id.name if record.employee_id else "Unknown"

    @api.depends('employee_id', 'attendance_date')
    def _compute_summary_record(self):
        """Link all records to the first record of the day for this employee"""
        for record in self:
            if not record.employee_id or not record.attendance_date:
                record.summary_record_id = False
                continue

            # Find the first record for this employee-date combination
            first_record = self.env['biometric.attendance.log'].search([
                ('employee_id', '=', record.employee_id.id),
                ('attendance_date', '=', record.attendance_date)
            ], order="log_time asc", limit=1)

            if first_record:
                if record.id == first_record.id:
                    record.summary_record_id = record.id
                else:
                    record.summary_record_id = first_record.id
            else:
                record.summary_record_id = False

    @api.depends('employee_id', 'attendance_date', 'log_time', 'attendance_type')
    def _compute_attendance_summary(self):
        """Compute attendance summary information"""
        # Process records grouped by employee and date for efficiency
        employee_date_groups = {}
        for record in self:
            if not record.employee_id or not record.attendance_date:
                record.first_check_in = False
                record.last_check_out = False
                record.all_logs = ""
                record.total_hours = 0.0
                record.is_first_record = False
                continue

            key = (record.employee_id.id, record.attendance_date)
            if key not in employee_date_groups:
                employee_date_groups[key] = []
            employee_date_groups[key].append(record.id)

        # Process each group
        for (employee_id, date), record_ids in employee_date_groups.items():
            records = self.browse(record_ids)

            # Fetch ALL logs for this employee-date combination
            all_logs = self.env['biometric.attendance.log'].search([
                ('employee_id', '=', employee_id),
                ('attendance_date', '=', date)
            ], order="log_time asc")

            # Get first record (will be used as summary record)
            first_record = all_logs[0] if all_logs else None

            if not first_record:
                continue

            # Filter check-ins and check-outs
            check_ins = all_logs.filtered(lambda r: r.attendance_type == 'in')
            check_outs = all_logs.filtered(lambda r: r.attendance_type == 'out')

            # Get first check-in and last check-out
            first_in = check_ins[0].log_time if check_ins else False
            last_out = check_outs[-1].log_time if check_outs else False

            # Calculate total hours if both check-in and check-out exist
            total_hours = 0.0
            if first_in and last_out:
                time_diff = last_out - first_in
                total_hours = time_diff.total_seconds() / 3600  # Convert to hours

            # Format all logs for display
            log_entries = []
            for log in all_logs:
                log_entries.append(f"{log.log_time.strftime('%H:%M:%S')} - {log.attendance_type.upper()}")
            all_logs_text = "\n".join(log_entries)

            # Update all records in this group
            for record in records:
                # Mark if this is the first record of the day
                record.is_first_record = (record.id == first_record.id)

                # Only store summary data on the first record
                if record.is_first_record:
                    record.first_check_in = first_in
                    record.last_check_out = last_out
                    record.all_logs = all_logs_text
                    record.total_hours = total_hours
                else:
                    record.first_check_in = False
                    record.last_check_out = False
                    record.all_logs = ""
                    record.total_hours = 0.0

    def name_get(self):
        """Custom name display for records"""
        result = []
        for record in self:
            if record.employee_id and record.attendance_date:
                name = f"{record.employee_name} - {record.attendance_date}"
                result.append((record.id, name))
            else:
                result.append((record.id, "New Attendance Log"))
        return result


class BiometricAttendanceLogLine(models.Model):
    _name = 'biometric.attendance.log.line'
    _description = 'Biometric Attendance Log Line'

    attendance_log_id = fields.Many2one('biometric.attendance.log', string="Attendance Log")
    attendance_date = fields.Date(string="Date")
    status = fields.Selection([('P', 'Present'), ('A', 'Absent'), ('L', 'Leave')], default='A')
