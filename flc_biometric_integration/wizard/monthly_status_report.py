from odoo import models, fields, api
from datetime import timedelta, date
import logging
import sys

_logger = logging.getLogger(__name__)

class MonthlyStatusReportWizard(models.TransientModel):
    _name = 'monthly.status.report.wizard'
    _description = 'Monthly Status Report Wizard'

    department_id = fields.Many2one('hr.department', string="Department")
    from_date = fields.Date(string="From Date", required=True, default=lambda self: date.today().replace(day=1))
    to_date = fields.Date(string="To Date", required=True, default=lambda self: date.today().replace(day=1) + timedelta(days=30) - timedelta(days=1))
    employee_id = fields.Many2one('hr.employee', string="Employee")

    # def action_view_report(self):
    #     domain = []
    #     if self.department_id:
    #         domain.append(('department_id', '=', self.department_id.id))
    #     if self.employee_id:
    #         domain.append(('id', '=', self.employee_id.id))
    #
    #     employees = self.env['hr.employee'].search(domain)
    #     print("Employees:", employees)
    #     print("Employees Name:", employees.name)
    #     report_details = []
    #
    #     for employee in employees:
    #         # ✅ Fetch full attendance log records
    #         attendance_logs = self.env['biometric.attendance.log'].search([
    #             ('employee_id', '=', employee.id),
    #             ('attendance_date', '>=', self.from_date),
    #             ('attendance_date', '<=', self.to_date)
    #         ], order='attendance_date')
    #         print("attendance_logs:", attendance_logs)
    #
    #         # ✅ Make sure 'attendance_logs' contains recordsets, NOT just IDs
    #         print(f"Employee: {employee.name}, Attendance Logs: {attendance_logs}")  # Debugging
    #
    #         report_details.append({
    #             'employee_name': employee.name,
    #             'employee_id': employee.identification_id or '',
    #             'total_work_duration': sum(log.total_hours for log in attendance_logs),
    #             'present_days': len(set(log.attendance_date for log in attendance_logs)),
    #             'absent_days': (self.to_date - self.from_date).days + 1 - len(
    #                 set(log.attendance_date for log in attendance_logs)),
    #             'attendance_logs': attendance_logs,  # ✅ Ensure full records are passed
    #             'total_days': (self.to_date - self.from_date).days + 1,
    #             'department_name': employee.department_id.name if employee.department_id else ''
    #         })
    #
    #     return self.env.ref('flc_biometric_integration.action_report_flc_biometric_attendance_register_wiz').report_action(self, report_details=report_details)
    #     #     {
    #     #     'type': 'ir.actions.report',
    #     #     'report_name': 'flc_biometric_integration.report_attendance_register_flc_wiz',
    #     #     'data': {'report_details': report_details},
    #     #     # ✅ Make sure report_details is a list of dicts with full records
    #     # }

    def get_date_range(self):
        date_from = self.from_date
        date_to = self.to_date

        dates = []
        current_date = date_from
        while current_date <= date_to:
            dates.append(current_date)
            current_date += timedelta(days=1)

        _logger.info(f"Generated Date Range: {dates}")  # Debugging Line
        return dates
    def action_view_report(self):
        domain = []
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        if self.employee_id:
            domain.append(('id', '=', self.employee_id.id))

        employees = self.env['hr.employee'].search(domain)
        print("Employees:", employees)

        report_details = []
        print("From Date:", self.from_date)
        print("To Date:", self.to_date)
        print("Department:", self.department_id.name if self.department_id else '')
        for employee in employees:
            attendance_logs = self.env['biometric.attendance.log'].search([
                ('employee_id', '=', employee.id),('is_first_record', '=', True),
                ('attendance_date', '>=', self.from_date),
                ('attendance_date', '<=', self.to_date)
            ], order='attendance_date')
            print("Attendance Logs:", attendance_logs)
            for log in attendance_logs:
                print(" employee Attendance Log:", log)
                print("Attendance Date:", log.attendance_date)
                print("First Check In:", log.first_check_in)
                print("Last Check Out:", log.last_check_out)
                print("Total Hours:", log.total_hours)
            # get attndel logs  id lien liek chekin chekout first_check_in , last_check_out
            # attendance_logs.first_check_in = [log.first_check_in for log in attendance_logs]

            present_days = len(set(log.attendance_date for log in attendance_logs))
            total_work_duration = sum(log.total_hours for log in attendance_logs)
            total_days = (self.to_date - self.from_date).days + 1
            absent_days = total_days - present_days

            report_details.append({
                'employee_name': employee.name,
                'employee_id': employee.identification_id or '',
                'total_work_duration': total_work_duration,
                'present_days': present_days,
                'absent_days': absent_days,
                # 'attendance_logs': attendance_logs,
                'total_days': total_days,
                'department_name': employee.department_id.name if employee.department_id else '',
                'attendance_logs': [
                    {
                        'log_id': log.id,
                        'attendance_date': log.attendance_date,
                        'first_check_in': log.first_check_in or 'N/A',
                        'last_check_out': log.last_check_out or 'N/A',
                        'total_hours': log.total_hours or 'N/A'
                    }
                    for log in attendance_logs
                ]
            })
        print("Report Details:", report_details)

        data = {
            'date_from': self.from_date,
            'date_to': self.to_date,
            'report_details': report_details,
            'department_name': self.department_id.name if self.department_id else '',
            'employee_name': self.employee_id.name if self.employee_id else '',
            'attendance_logs': attendance_logs,
            'get_date_range': self.get_date_range()
        }
        print("Data:", data)
        # lllllllllllllllllllllllllll
        return self.env.ref('flc_biometric_integration.action_report_flc_biometric_attendance_register_wiz').report_action(self, data=data)
