from odoo import models, fields, api
import requests
from lxml import etree
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class BiometricAttendanceWizard(models.TransientModel):
    _name = 'biometric.attendance.wizard'
    _description = 'Fetch Biometric Logs'

    # from_date = fields.Datetime("From Date", required=True)
    # to_date = fields.Datetime("To Date", required=True)
    from_date = fields.Datetime("From Date", default=lambda self: datetime.today().replace(day=1), required=True)
    to_date = fields.Datetime("To Date", default=lambda self: datetime.today(), required=True)
    terminal_id = fields.Many2one('biometric.terminal', "Branch", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=False)

    # def action_download_report(self):
    #     return self.env.ref('flc_biometric_integration.biometric_attendance_report_action').report_action(self)

    # def fetch_attendance_summary(self):
    #     """Fetch summarized biometric logs for the given month"""
    #     domain = [
    #         ('attendance_date', '>=', self.from_date),
    #         ('attendance_date', '<=', self.to_date)
    #     ]
    #     if self.terminal_id:
    #         domain.append(('terminal_id', '=', self.terminal_id.id))
    #     if self.employee_id:
    #         domain.append(('employee_id', '=', self.employee_id.id))
    #
    #     return self.env['biometric.attendance.log'].search(domain, order="attendance_date desc")
    #
    # def action_download_report(self):
    #     """Trigger the PDF report download"""
    #     return self.env.ref('flc_biometric_integration.biometric_attendance_report_action').report_action(self)

    @api.model
    def cron_fetch_attendance_logs(self):
        print("\nCron Job Started::::::::::::::::::: Now Time is: ", fields.Datetime.now())
        terminals = self.env['biometric.terminal'].search([])
        for terminal in terminals:
            wizard = self.create({
                'from_date': fields.Datetime.to_string(fields.Datetime.now() - timedelta(days=1)),
                'to_date': fields.Datetime.to_string(fields.Datetime.now()),
                'terminal_id': terminal.id,
            })
            wizard.fetch_attendance_logs()


    def fetch_attendance_logs(self):
        print("\n self",self, self._context)
        url = "http://116.72.248.17/iclock/webapiservice.asmx"
        headers = {"Content-Type": "text/xml"}
        data = f'''<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <GetTransactionsLog xmlns="http://tempuri.org/">
              <FromDateTime>{self.from_date}</FromDateTime>
              <ToDateTime>{self.to_date}</ToDateTime>
              <SerialNumber>{self.terminal_id.serial_number}</SerialNumber>
              <UserName>{self.terminal_id.username}</UserName>
              <UserPassword>{self.terminal_id.password}</UserPassword>
              <strDataList>string</strDataList>
            </GetTransactionsLog>
          </soap:Body>
        </soap:Envelope>'''

        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200:
            try:
                _logger.info(f"Biometric API Response: {response.text}")  # Log full API response

                root = etree.fromstring(response.content)
                namespace = {'ns': 'http://tempuri.org/'}

                # Extract strDataList
                data_list_elem = root.find(".//ns:strDataList", namespace)

                if data_list_elem is None or not data_list_elem.text or not data_list_elem.text.strip():
                    _logger.warning("No biometric log data found in API response.")
                    return

                # Clean and split log entries
                logs = [line.strip() for line in data_list_elem.text.strip().split("\n") if line.strip()]

                for log in logs:
                    log_parts = log.split("\t")  # Split by tab

                    # Ensure correct format
                    if len(log_parts) < 2:
                        _logger.warning(f"Skipping malformed log entry: {log}")
                        continue  # Skip malformed entries

                    user_id = log_parts[0].strip() if log_parts[0].strip() else None
                    log_time = log_parts[1].strip() if log_parts[1].strip() else None

                    # Debugging: Log extracted values
                    _logger.info(f"Extracted Log: UserID={user_id}, LogTime={log_time}")

                    if not user_id or not log_time:
                        _logger.warning(f"Skipping log entry due to missing data: UserID={user_id}, LogTime={log_time}")
                        continue

                    # Determine event type (Check-In or Check-Out)
                    event_type = 'in' if "07:" in log_time or "08:" in log_time else 'out'

                    # Find employee by biometric_id or identification_id
                    emp_id = self.env['hr.employee'].sudo().search([
                        '|',
                        ('biometric_id', '=', user_id),
                        ('identification_id', '=', user_id)
                    ], limit=1)

                    employee_name = emp_id.name if emp_id else user_id

                    if emp_id:
                        _logger.info(f"Matched Employee: {emp_id.name} (ID: {emp_id.id}) for Biometric ID: {user_id}")
                    else:
                        _logger.warning(f"No matching employee found for Biometric ID: {user_id}")

                    # Create attendance log
                    self.env['biometric.attendance.log'].sudo().create({
                        'employee_id': emp_id.id if emp_id else False,
                        'employee_name': employee_name,
                        'user_id':user_id,
                        'log_time': log_time,
                        'terminal_id': self.terminal_id.id,
                        'attendance_type': event_type
                    })

            except Exception as e:
                _logger.error(f"Error processing biometric logs: {str(e)}")
        else:
            _logger.error(f"Error fetching data from API: {response.status_code}, {response.text}")
            raise ValueError(f"API request failed with status {response.status_code}")

