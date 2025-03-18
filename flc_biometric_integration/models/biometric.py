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
from datetime import date, timedelta
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

    # employee_name = fields.Char("Employee Name", compute="_compute_employee_name", store=True)
    employee_name = fields.Char("Employee Name", related="employee_id.name", store=True)
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

    def get_date_range(self):
        """Return a list of dates for the report period"""
        # Static date range: January 25 to February 26 of the current year
        current_year = fields.Date.today().year
        date_from = date(current_year, 1, 25)
        date_to = date(current_year, 2, 26)

        dates = []
        current_date = date_from
        while current_date <= date_to:
            dates.append(current_date)
            current_date += timedelta(days=1)

        return dates


    def _find_summary_record(self, employee_id, date):
        """Find the summary record for the employee on the given date"""
        # Convert date string to date object if needed
        if isinstance(date, str):
            date = fields.Date.from_string(date)

        # Find the record that has the attendance summary
        summary_record = self.env['biometric.attendance.log'].search([
            ('employee_id', '=', employee_id),
            ('attendance_date', '=', date),
            ('is_first_record', '=', True)
        ], limit=1)

        return summary_record

    def get_employee_attendance(self, employee_id, attendance_date):
        """Fetch attendance data for a specific employee and date."""
        logs = self.search([
            ('employee_id', '=', employee_id),
            ('attendance_date', '=', attendance_date)
        ], order="log_time asc")

        first_check_in = logs.filtered(lambda l: l.attendance_type == 'in')[:1].log_time
        last_check_out = logs.filtered(lambda l: l.attendance_type == 'out')[-1:].log_time

        total_hours = 0.0
        if first_check_in and last_check_out:
            total_hours = (last_check_out - first_check_in).total_seconds() / 3600.0  # Convert to hours

        return {
            'first_check_in': first_check_in.strftime('%H:%M:%S') if first_check_in else '--:--',
            'last_check_out': last_check_out.strftime('%H:%M:%S') if last_check_out else '--:--',
            'total_hours': total_hours,
            'status': 'present' if first_check_in and last_check_out else 'absent'
        }

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
    #####----------------------- Register Formate Document-------------------------#####
    # def get_status(self, employee_id, date):
    #     # Logic to determine attendance status (P, A, WO, etc.)
    #     attendance = self.env['hr.attendance'].search([
    #         ('employee_id', '=', employee_id),
    #         ('check_in', '>=', date + ' 00:00:00'),
    #         ('check_in', '<=', date + ' 23:59:59')
    #     ], limit=1)
    #
    #     if attendance:
    #         return 'P'  # Present
    #     else:
    #         # Check for leaves, weekly offs, etc.
    #         return 'A'  # Absent

    # def get_in_time1(self, employee_id, date):
    #     # Get first check-in time
    #     attendance = self.env['hr.attendance'].search([
    #         ('employee_id', '=', employee_id),
    #         ('check_in', '>=', date + ' 00:00:00'),
    #         ('check_in', '<=', date + ' 23:59:59')
    #     ], order='check_in asc', limit=1)
    #
    #     if attendance:
    #         return fields.Datetime.from_string(attendance.check_in).strftime('%H:%M')
    #     return ''

    # def get_out_time1(self, employee_id, date):
    #     # Get first check-out time
    #     attendance = self.env['hr.attendance'].search([
    #         ('employee_id', '=', employee_id),
    #         ('check_in', '>=', date + ' 00:00:00'),
    #         ('check_in', '<=', date + ' 23:59:59')
    #     ], order='check_in asc', limit=1)
    #
    #     if attendance and attendance.check_out:
    #         return fields.Datetime.from_string(attendance.check_out).strftime('%H:%M')
    #     return ''
    #
    # def get_in_time2(self, employee_id, date):
    #     # Get second check-in time (if applicable)
    #     attendances = self.env['hr.attendance'].search([
    #         ('employee_id', '=', employee_id),
    #         ('check_in', '>=', date + ' 00:00:00'),
    #         ('check_in', '<=', date + ' 23:59:59')
    #     ], order='check_in asc')
    #
    #     if len(attendances) > 1:
    #         return fields.Datetime.from_string(attendances[1].check_in).strftime('%H:%M')
    #     return ''
    #
    # def get_out_time2(self, employee_id, date):
    #     # Get second check-out time (if applicable)
    #     attendances = self.env['hr.attendance'].search([
    #         ('employee_id', '=', employee_id),
    #         ('check_in', '>=', date + ' 00:00:00'),
    #         ('check_in', '<=', date + ' 23:59:59')
    #     ], order='check_in asc')
    #
    #     if len(attendances) > 1 and attendances[1].check_out:
    #         return fields.Datetime.from_string(attendances[1].check_out).strftime('%H:%M')
    #     return ''

class ReportBiometricAttendance(models.AbstractModel):
    _name = 'report.flc_biometric_integration.attendance_register1'
    _description = 'Biometric Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['biometric.attendance.log'].browse(docids)

        # Fetch all employees with biometric attendance data for the report
        employees = self.env['hr.employee'].search([])

        # Collect attendance data per employee
        attendance_data = {}
        attendance_date = fields.Date.context_today(self)
        for emp in employees:
            attendance_data[emp.id] = self.env['biometric.attendance.log'].get_employee_attendance(emp.id, attendance_date)

        return {
            'doc_ids': docids,
            'doc_model': 'biometric.attendance.log',
            'docs': docs,
            'employees': employees,
            'attendance_data': attendance_data,
            'attendance_date': attendance_date
        }


class BiometricAttendanceLogLine(models.Model):
    _name = 'biometric.attendance.log.line'
    _description = 'Biometric Attendance Log Line'

    attendance_log_id = fields.Many2one('biometric.attendance.log', string="Attendance Log")
    attendance_date = fields.Date(string="Date")
    status = fields.Selection([('P', 'Present'), ('A', 'Absent'), ('L', 'Leave')], default='A')
