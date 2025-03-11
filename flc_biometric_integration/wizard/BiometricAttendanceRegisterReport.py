import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import pytz
from zoneinfo import ZoneInfo


class BiometricAttendanceRegisterReport(models.AbstractModel):
    _name = 'report.flc_biometric_integration.attendance_register'
    _description = 'Biometric Attendance Register Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Get report parameters from data or use defaults
        if data and data.get('form'):
            attendance_date = fields.Date.from_string(data['form']['attendance_date'])
            branch_id = data['form'].get('branch_id', False)
            department_id = data['form'].get('department_id', False)
        else:
            attendance_date = fields.Date.today()
            branch_id = False
            department_id = False

        # Get employees based on filters
        domain = []
        if branch_id:
            domain.append(('branch_id', '=', branch_id))
        if department_id:
            domain.append(('department_id', '=', department_id))

        employees = self.env['hr.employee'].search(domain)

        # Store attendance summary for statistics
        self.attendance_summary = {
            'present': 0,
            'absent': 0,
            'late': 0,
            'early_departure': 0,
            'half_day': 0,
            'leave': 0
        }

        # Get branch name if filter is applied
        branch_name = False
        if branch_id:
            branch = self.env['biometric.terminal'].browse(branch_id)
            branch_name = branch.name

        # Get department name if filter is applied
        department_name = False
        if department_id:
            department = self.env['hr.department'].browse(department_id)
            department_name = department.name

        return {
            'doc_ids': docids,
            'doc_model': 'biometric.attendance.log',
            'attendance_date': attendance_date,
            'branch': branch_name,
            'department': department_name,
            'employees': employees,
            'get_employee_attendance': self._get_employee_attendance,
            'get_attendance_count': self._get_attendance_count,
            'datetime': datetime,
        }

    def _get_attendance_count(self, status_type):
        """Return the count of attendance with the specified status"""
        return self.attendance_summary.get(status_type, 0)

    def _get_employee_attendance(self, employee_id, attendance_date):
        """Get detailed attendance for an employee on a specific date"""
        # Initialize result
        result = {
            'status': 'absent',
            'morning_status': 'absent',
            'evening_status': 'absent',
            'total_hours': 0.0,
            'first_check_in': False,
            'last_check_out': False
        }

        # Define standard times (configurable in the future)
        try:
            # Try to use Indian timezone
            tz = ZoneInfo('Asia/Kolkata')
        except:
            try:
                # Fallback to pytz if ZoneInfo fails
                tz = pytz.timezone('Asia/Kolkata')
            except:
                # Last resort - use UTC
                tz = datetime.timezone.utc

        # Company configuration (could be moved to system parameters)
        company = self.env.company
        work_start_time = company.work_start_time or '09:00'
        work_end_time = company.work_end_time or '18:00'
        late_tolerance_mins = company.late_tolerance_mins or 15
        early_departure_tolerance_mins = company.early_departure_tolerance_mins or 15

        # Parse work times
        work_start_hours, work_start_mins = map(int, work_start_time.split(':'))
        work_end_hours, work_end_mins = map(int, work_end_time.split(':'))

        # Create datetime objects for standard times
        date_str = attendance_date.strftime('%Y-%m-%d')
        standard_start = datetime.datetime.strptime(f"{date_str} {work_start_time}:00", "%Y-%m-%d %H:%M:%S")
        standard_end = datetime.datetime.strptime(f"{date_str} {work_end_time}:00", "%Y-%m-%d %H:%M:%S")

        # Add tolerance
        late_threshold = standard_start + datetime.timedelta(minutes=late_tolerance_mins)
        early_departure_threshold = standard_end - datetime.timedelta(minutes=early_departure_tolerance_mins)

        # Search attendance logs for the employee on this date
        logs = self.env['biometric.attendance.log'].search([
            ('employee_id', '=', employee_id),
            ('attendance_date', '=', attendance_date)
        ], order="log_time asc")

        if logs:
            # Check for leaves first
            leave = self.env['hr.leave'].search([
                ('employee_id', '=', employee_id),
                ('date_from', '<=', datetime.datetime.combine(attendance_date, datetime.time.max)),
                ('date_to', '>=', datetime.datetime.combine(attendance_date, datetime.time.min)),
                ('state', '=', 'validate')
            ], limit=1)

            if leave:
                result['status'] = 'leave'
                self.attendance_summary['leave'] += 1
                return result

            # Get check-ins and check-outs
            check_ins = logs.filtered(lambda r: r.attendance_type == 'in')
            check_outs = logs.filtered(lambda r: r.attendance_type == 'out')

            if check_ins:
                result['first_check_in'] = check_ins[0].log_time

                # Determine morning status
                if result['first_check_in'] <= standard_start:
                    result['morning_status'] = 'early'
                elif result['first_check_in'] <= late_threshold:
                    result['morning_status'] = 'on_time'
                else:
                    result['morning_status'] = 'late'
                    self.attendance_summary['late'] += 1

            if check_outs:
                result['last_check_out'] = check_outs[-1].log_time

                # Determine evening status
                if result['last_check_out'] < early_departure_threshold:
                    result['evening_status'] = 'early'
                    self.attendance_summary['early_departure'] += 1
                elif result['last_check_out'] >= standard_end:
                    result['evening_status'] = 'late'
                else:
                    result['evening_status'] = 'on_time'

            # Calculate total hours
            if result['first_check_in'] and result['last_check_out']:
                time_diff = result['last_check_out'] - result['first_check_in']
                result['total_hours'] = time_diff.total_seconds() / 3600  # Convert to hours

                # Determine overall status
                if (result['morning_status'] == 'late' and result['evening_status'] == 'early') or \
                        result['total_hours'] < (company.minimum_full_day_hours or 6.0):
                    result['status'] = 'half_day'
                    self.attendance_summary['half_day'] += 1
                else:
                    result['status'] = 'present'
                    self.attendance_summary['present'] += 1
        else:
            # No logs found - absent
            self.attendance_summary['absent'] += 1

        return result


class BiometricAttendanceRegisterWizard(models.TransientModel):
    _name = 'biometric.attendance.register.wizard'
    _description = 'Attendance Register Report Wizard'

    attendance_date = fields.Date(string='Date', required=True, default=fields.Date.today)
    branch_id = fields.Many2one('biometric.terminal', string='Branch')
    department_id = fields.Many2one('hr.department', string='Department')

    def print_report(self):
        """Generate the register report"""
        data = {
            'form': {
                'attendance_date': self.attendance_date,
                'branch_id': self.branch_id.id if self.branch_id else False,
                'department_id': self.department_id.id if self.department_id else False,
            }
        }

        return self.env.ref('flc_biometric_integration.action_biometric_attendance_register_report_v1').report_action(
            [], data=data
        )