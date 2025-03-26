from odoo import models, fields, api
from datetime import date, timedelta

from odoo.odoo.tools.populate import compute


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_category = fields.Selection([('consultant', 'Consultant'), ('education', 'Education-Based')
                                          ], string="Employee Category", default='consultant')
    provident_fund = fields.Float(string='Provident Fund')
    employee_esic = fields.Float(string='ESIC')
    professional_tax = fields.Float(string='Professional Tax ')
    employee_doj = fields.Char(string='Date of Joining')
    aadhar_no = fields.Char(string='Aadhar No')
    pf_no = fields.Char(string='PF No')
    uan_no = fields.Char(string='UAN No')
    eisc_no = fields.Char(string='EISC No')
    branch_id = fields.Many2one('res.branch', string="Branch")
    has_weekend_off = fields.Boolean(string="Has Saturday-Sunday Off")
    last_leave_allocation = fields.Date(string="Last Paid Monthly Allocation Date", default=False)
    annual_leave_balance = fields.Float(string="Monthly Paid Leave Balance", default=0.0)
    used_annual_leaves_this_month = fields.Integer(string="Used Monthly Leaves This Month", default=0)
    weekly_off_type = fields.Selection([('sunday', 'Sunday Off'), ('saturday_sunday', 'Saturday & Sunday Off')],
                                       string="Weekly Off Type", default='sunday')
    employee_team = fields.Selection([('india', 'India Team'), ('canada', 'Canada Team')],
                                     string="Employee Team", required=True, default='india')
    daily_reporting_timing = fields.Selection([('10_7', '10:00 AM - 7:00 PM'), ('9_6', '9:00 AM - 6:00 PM'),
                                               ('9_30_6_30', '9:30 AM - 6:30 PM')], string="Daily Reporting Time",
                                              default='10_7')
    break_timing = fields.Selection([('1_1_45', '1:00 PM - 1:45 PM'), ('1_45_2_30', '1:45 PM - 2:30 PM'),
                                     ('1_2_30', '1:00 PM - 2:30 PM'), ], string="Break Timing", default='1_2_30')
    attendance_based_pay = fields.Boolean(string="Attendance Based Pay", default=False,
                                          help="If checked, salary will be calculated based on biometric attendance")
    bio_attendance_ids = fields.One2many('biometric.attendance.log', 'employee_id', compute='_compute_attendance',
                                         store=True, readonly=False)
    is_bio_metric_synced = fields.Boolean(string="Biometric Synced Count", default=False,
                                          help="Biometric device user ID")

    break_time = fields.Float("Total Break Time (Minutes)", compute="_compute_attendance", store=True)
    access_time = fields.Float("Total Worked Hours", compute="_compute_attendance", store=True)

    probation_end_date = fields.Date(string="Probation End Date", compute="_compute_probation_end_date", store=True)
    probation_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('extended', 'Extended')
    ], string="Probation Status", default='pending', tracking=True)
    extended_probation_date = fields.Date(string="Extended Probation Date")

    @api.depends('create_date')
    def _compute_probation_end_date(self):
        for rec in self:
            if rec.create_date:
                rec.probation_end_date = rec.create_date.date() + timedelta(days=90)

    def action_complete_probation(self):
        """Mark probation as completed"""
        for rec in self:
            rec.probation_status = 'completed'

    def action_extend_probation(self, new_date):
        """Extend probation with a new date"""
        for rec in self:
            rec.probation_status = 'extended'
            rec.extended_probation_date = new_date

    def check_probation_completion(self):
        """Cron job to check probation completion"""
        today = date.today()
        employees = self.search([('probation_end_date', '=', today), ('probation_status', '=', 'pending')])

        for emp in employees:
            if emp.parent_id:  # Reporting manager exists
                template = self.env.ref('your_module.email_template_probation_notification')
                template.send_mail(emp.id, force_send=True)

    @api.depends('biometric_id')
    def _compute_attendance(self):
        for employee in self:
            if not employee.is_bio_metric_synced or not employee.biometric_id:
                employee.bio_attendance_ids = []
                continue

            # Fetch biometric logs for the employee
            logs = self.env['biometric.attendance.log'].search(
                [('user_id', '=', employee.biometric_id)],
                order='attendance_date asc'
            )

            attendance_data = []
            total_break_time = 0.0  # Total break time in minutes
            total_access_time = 0.0  # Total worked hours

            previous_log = None

            for log in logs:
                break_time = 0.0  # Reset per log entry

                if previous_log:
                    break_start = previous_log.last_check_out
                    break_end = log.first_check_in

                    if break_start and break_end:
                        break_duration = (break_end - break_start).total_seconds() / 60  # Convert to minutes
                        if 30 <= break_duration <= 90:  # Consider breaks only in valid range
                            break_time = break_duration  # Assign per log
                            total_break_time += break_duration  # Accumulate total break time

                # Append attendance record with break_time and access_time
                attendance_data.append((0, 0, {
                    'employee_id': employee.id,
                    'attendance_date': log.attendance_date,
                    'first_check_in': log.first_check_in,
                    'last_check_out': log.last_check_out,
                    'total_hours': log.total_hours,
                    'break_time': break_time,  # Pass break time per log
                    'access_time': log.total_hours,  # Pass total hours per log
                }))

                total_access_time += log.total_hours
                previous_log = log  # Update previous log for next iteration

            # Assign computed values to employee records
            employee.bio_attendance_ids = [(5, 0, 0)] + attendance_data  # Clear & update records
            employee.break_time = total_break_time  # Store total break time
            employee.access_time = total_access_time  # Store total worked hours

    #
    # ###Working Code  for Normal
    # @api.depends('biometric_id')
    # def _compute_attendance(self):
    #     print("\n_compute_attendance::::::::::::::::::", self, self._context)
    #
    #     for employee in self:
    #         print("\nemployee::::::::::::::::::", employee, employee._context)
    #
    #         if not employee.is_bio_metric_synced:
    #             employee.bio_attendance_ids = []  # ✅ Assign directly
    #             continue
    #
    #         if not employee.biometric_id:  # ✅ Corrected condition
    #             continue  # Skip if biometric_id is missing
    #
    #         # Fetch only biometric logs, ignore hr.attendance
    #         logs = self.env['biometric.attendance.log'].search(
    #             [('user_id', '=', employee.biometric_id)],
    #             order='attendance_date asc'
    #         )
    #         print("\nlogs::::::::::::::::::", logs)
    #
    #         attendance_data = [(0, 0, {
    #             'employee_id': employee.id,
    #             'attendance_date': log.attendance_date,
    #             'first_check_in': log.first_check_in,
    #             'last_check_out': log.last_check_out,
    #             'total_hours': log.total_hours,
    #         }) for log in logs]
    #         print("\nattendance_data::::::::::::::::::", attendance_data)
    #
    #         # ✅ Correct assignment
    #         employee.bio_attendance_ids = [(5, 0, 0)] + attendance_data  # Clear & update records


    ##hr.contract.type###
    """
     ######We have four types of employees with different leave policies:
    -------------------------------------------------------------------------
    A . Full-Time(Mon-Sat) - Employees- Monday to Saturday
       * Get 1.5 paid leaves per month after completing 3 months of probation.
       
    B. Full-Time(Mon-Fri)
       * Employees with Saturday and Sunday off do not receive 1.5 paid leaves.
       
    C. Part-Time Employees
       * Do not receive paid leave or festival leave.
       
    d. Interns
      * Do not receive paid leave.
      
    e . Contract Basis Employees
     * Do not receive 1.5 paid leaves
     * Paid based on work hours (pro-rata basis).
    ----------------------------------------------
    """
    employee_type_id = fields.Many2one('hr.contract.type', string="Work Type", help="Employee Contract Type")
    employee_type = fields.Selection([
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('intern', 'Intern'),
        ('contract', 'Contract Basis'),
    ], string="Employee Type", required=True)
    """
    FLC CRM - Employee Stages Module

    - Adds Employee Stages in Odoo HR.
    - Displays employee stages as a status bar.
    - Allows stage transitions directly from the employee form.
    """
    stage = fields.Selection([
        ('new', 'New / Joined'),
        ('training', 'Training'),
        ('probation', 'Probation'),
        ('employment', 'Employment'),
        ('pip', 'PIP'),
        ('notice_period', 'Notice Period'),
        ('relieved', 'Relieved'),
        ('rejoined', 'Rejoined'),
    ], string="Employee Stage", default="new", tracking=True)

    @api.model
    def check_probation_status(self):
        """ Cron job to check probation completion and notify managers """
        today = date.today()
        print("today :::::", today)
        employees = self.search([
            ('stage', '=', 'probation'),
            ('joining_date', '<=', today)])
        print("employee :::::", employees)
        for emp in employees:
            emp._notify_managers_about_probation()

    def _notify_managers_about_probation(self):
        """Notify the reporting manager when an employee completes 3 months probation."""
        # three_months_ago = date.today() - timedelta(days=90)
        # employees = self.search([('joining_date', '=', three_months_ago)])
        #
        # for emp in employees:
        if self.parent_id:  # Reporting Manager exists
            message = f"Employee {self.name} joining date{self.joining_date}  has completed their 3-month probation period ."
            print("message :::::", message)
            self.parent_id.message_post(body=message, subtype_xmlid="mail.mt_comment", partner_ids=[self.parent_id.id])

    @api.model
    def reset_monthly_leave_limit(self):
        """ Reset annual leave usage counter and set annual_leave_balance to 0 at the start of each month """
        employees = self.search([])
        employees.write({
            'used_annual_leaves_this_month': 0,  # Reset used monthly leaves
            'annual_leave_balance': 0  # Reset annual leave balance
        })

    def allocate_monthly_leaves(self):
        """ Automatically allocate 1.5 leave every month for full-time employees """
        print("allocate_monthly_leaves::::::::::::::::::", self, self._context)
        today = date.today()

        # Retrieve all full-time employees who have no weekend off
        employees = self.env['hr.employee'].search([
            ('employee_type', '=', 'full_time'),
            ('stage', '=', 'employment'),
            ('has_weekend_off', '=', False)  # Only Mon-Sat employees eligible
        ])
        for emp in employees:
            # Skip if leave has already been allocated this month
            if emp.last_leave_allocation and emp.last_leave_allocation.month == today.month:
                continue  # Already allocated this month

            # Find the leave type 'Full Day Leave'
            leave_type = self.env['hr.leave.type'].search([('name', '=', 'Full Day Leave')], limit=1)

            if not leave_type:
                raise ValueError("Leave Type 'Full Day Leave' is missing. Please configure it in Odoo.")
            # Auto-allocate leave without approval
            self.env['hr.leave.allocation'].create({
                'name': f'Monthly Paid Leave for {emp.name}',
                'holiday_status_id': leave_type.id,
                'employee_id': emp.id,
                'number_of_days': 1.5,
                'state': 'confirm',  # Automatically approved
            })

            # Update the last leave allocation date
            emp.write({'last_leave_allocation': today, 'annual_leave_balance':1.5})
            # Notify Employee
            emp.message_post(
                body=f"You have been granted 1.5 days of leave for {today.strftime('%B')}.",
                subtype_xmlid="mail.mt_comment"
            )

            # Notify Manager
            if emp.parent_id:
                emp.parent_id.message_post(
                    body=f"{emp.name} has received 1.5 days of leave for {today.strftime('%B')}.",
                    subtype_xmlid="mail.mt_comment"
                )

        return True

class EmployeeAttendance(models.Model):
    _name = 'employee.attendance'
    _description = 'Employee Attendance'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    date = fields.Datetime(string="Work Date")
    work_date = fields.Datetime(string="Work Date")
    total_hours = fields.Float(string="Total Hours")
    check_in = fields.Datetime(string="Check In")
    first_check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")
    last_check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string="Worked Hours")
    # bio_metric_id = fields.Many2one('biometric.attendance.log',string="Biometric ID")
    attendance_date = fields.Date(string="Attendance Date")

    #i wnat to get all bimetric log Employee ID both smae whic match biometic in hr  meplaoye  eid and   then all attnde log and biometri c show here
    # def get_biometric_attendance(self):
    #     print("get_biometric_attendance::::::::::::::::::", self, self._context)
    #     # Fetch all biometric logs for this employee
    #         hr employee_id =biometric_id
    #     attendance_records = self.env['biometric.attendance.log'].search([user_id = employee_id])with the same employee_id

    # def get_biometric_attendance(self):
    #     print("get_biometric_attendance::::::::::::::::::", self, self._context)
    #     for record in self:
    #         # Fetch all biometric logs for this employee
    #         attendance_records = self.env['biometric.attendance.log'].search([
    #             ('employee_id', '=', record.employee_id.id)
    #         ])
    #         for attendance in attendance_records:
    #             print(f"Biometric Log: {attendance}")


