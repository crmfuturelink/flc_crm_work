from odoo import models, fields, api
from datetime import date, datetime, timedelta
from calendar import monthrange


class BiometricPayslipCalculation(models.Model):
    _inherit = 'hr.payslip'

    total_working_days = fields.Integer(string="Total Working Days", compute="_compute_payable_days")
    # attendance_logs::::::::: biometric.attendance.log(28716, 28714, 28713, 28715, 28710, 28712, 28711, 28709, 28708,
    #                                                   28707, 28705, 28706, 28704, 28703, 28702, 28701, 28699, 28700,
    #                                                   28698, 28697)
    days_worked = fields.Integer(string="Days Worked")
    payable_days = fields.Float(string="Payable Days")
    biometric_attendance_ids = fields.One2many('biometric.attendance.log', 'employee_id', string="Biometric Attendance")
    total_hours_worked = fields.Float(string="Total Hours Worked")
    #######################For Payslip Calculation#########################
    ## Wages Earned ##
    basic_da = fields.Float(string="Basic + DA", compute='_get_basic_da')
    def _get_basic_da(self):
        for rec in self:
            rec.basic_da = self.total_working_days * rec.contract_id.da
    # basic_da =  *  employee_hra = fields.Float(string='HRA', compute='_get_hra')
    hra = fields.Float(string="House Rent Allowance (HRA)")
    conveyance_allowance = fields.Float(string="Conveyance Allowance")
    washing_allowance = fields.Float(string="Washing Allowance")
    advance_bonus_833 = fields.Float(string="Advance Bonus @8.33%")
    other_allowance = fields.Float(string="Other Allowance")
    ph_wages = fields.Float(string="P H Wages")
    advance_bonus = fields.Float(string="Advance Bonus")
    leave_payment = fields.Float(string="Leave Payment")
    partial_incentive = fields.Float(string="Partial Incentive")
    food_allowance = fields.Float(string="Food Allowance")

    ## Deductions ##
    provident_fund = fields.Float(string="Provident Fund (12%)")
    e_s_i_c = fields.Float(string="ESIC @0.75%")
    professional_tax = fields.Float(string="Professional Tax")
    g_l_w_f = fields.Float(string="G L W F")
    advance = fields.Float(string="Advance Deduction")
    canteen = fields.Float(string="Canteen Charges")
    transport = fields.Float(string="Transport Charges")
    loan_deduction = fields.Float(string="Other / Loan Deduction")
    fine = fields.Float(string="Fine Deduction")
    loss_damages = fields.Float(string="Loss or Damages Deduction")

    ## Total Earnings & Deductions ##
    total_earnings = fields.Float(string="Gross Earned Wages", )
    total_deductions = fields.Float(string="Total Deductions")
    net_salary = fields.Float(string="NET PAYABLE")

    ###########Biometric Attendance Calculation For Payslip ################
    month_days = fields.Integer(string="Month Days", compute="_compute_payable_days")
    total_paid_days = fields.Float(string="Total Paid Days")
    weekly_off = fields.Integer(string="Weekly-Off")
    days_off = fields.Integer(string="Days-Off")
    paid_holidays = fields.Integer(string="Paid Holidays")
    unpaid_holidays = fields.Integer(string="Unpaid Holidays")
    working_days = fields.Integer(string="Working Days")
    max_payable_days = fields.Integer(string="Max Payable Days")
    lwp = fields.Integer(string="LWP (Leave Without Pay)")
    net_paid_days = fields.Float(string="Net Paid Days")
    present_days = fields.Integer(string="Present Days")
    paid_leaves = fields.Integer(string="Paid Leaves",)
    worked_days = fields.Integer(string="Worked Days",)
    payable_day = fields.Float(string="Payable Days")

    # payable_days = fields.Float(string="Payable Days", compute="_compute_payable_days")

    # def compute_sheet(self):
    #     """ Compute payroll based on biometric attendance data. """
    #     res = super(BiometricPayslipCalculation, self).compute_sheet()
    #     print("\nres:::::", res)
    #     # self._compute_payable_days()
    #     # llllllllllllllllllllllllll
    #     return res

    def _compute_payable_days(self):
        for payslip in self:
            total_days = (payslip.date_to - payslip.date_from).days + 1
            print("\nTotal Days:::::::::", total_days)
            payslip.month_days = total_days

            employee = payslip.employee_id
            print("\nemployee:::::::::", employee)

            # Fetch biometric attendance logs for the payslip period
            attendance_logs = self.env['biometric.attendance.log'].search([
                ('employee_id', '=', employee.id),
                ('attendance_date', '>=', payslip.date_from),
                ('attendance_date', '<=', payslip.date_to),
            ])
            print("\nAttendance Logs:::::::::", attendance_logs)

            # Fetch approved leave records in the same period
            approved_leaves = self.env['hr.leave'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'validate'),
                ('date_from', '>=', payslip.date_from),
                ('date_to', '<=', payslip.date_to),
            ])
            print("\nApproved Leaves:::::::::", approved_leaves)

            # Initialize counters
            paid_leaves = len(approved_leaves)
            present_days = 0
            lwp = 0  # Leave Without Pay

            required_hours = 8  # Standard full working hours

            # Dictionary to store total worked hours per day
            daily_hours = {}

            for log in attendance_logs:
                day_date = log.attendance_date

                if day_date not in daily_hours:
                    daily_hours[day_date] = 0

                daily_hours[day_date] += log.total_hours or 0  # Summing total hours per day

            # Compute payable days
            for day_date, worked_hours in daily_hours.items():
                if worked_hours >= required_hours:
                    present_days += 1  # Full-day payable
                elif worked_hours >= 4:
                    present_days += 0.5  # Half-day payable
                else:
                    lwp += 1  # No pay

            # Assign computed values
            payslip.total_working_days = len(daily_hours.keys())  # Unique working days based on logs
            payslip.present_days = present_days
            payslip.paid_leaves = paid_leaves
            payslip.lwp = lwp
            payslip.payable_day = present_days + paid_leaves  # ✅ Correct assignment

            print(f"\nComputed Payslip for {employee.name}:")
            print(f"Total Working Days: {payslip.total_working_days}")
            print(f"Present Days: {present_days}, Paid Leaves: {paid_leaves}, LWP: {lwp}")

    def generate_payslips(self):
        """Cron job to generate payslips for all employees"""
        print("Generating Payslips ::::::::::::::::::::")

        # today = date.today()
        # employees = self.env['hr.employee'].search([])
        #
        # for emp in employees:
        #     print(f"Processing Payslip for Employee: {emp.name}")
        #
        #     # Fetch biometric attendance logs for this employee
        #     attendance_records = self.env['biometric.attendance.log'].search([
        #         ('employee_id', '=', emp.id),
        #         ('attendance_date', '>=', today.replace(day=1)),  # Start of current month
        #         ('attendance_date', '<=', today)  # Today's date
        #     ])
        #
        #     worked_days = len(attendance_records)
        #     total_hours = sum(record.total_hours for record in attendance_records)
        #
        #     payslip_vals = {
        #         'employee_id': emp.id,
        #         'date_from': today.replace(day=1),
        #         'date_to': today,
        #         'total_working_days': (today - today.replace(day=1)).days + 1,
        #         'days_worked': worked_days,
        #         'payable_days': worked_days,
        #         'total_hours_worked': total_hours
        #     }
        #
        #     payslip = self.env['hr.payslip'].create(payslip_vals)
        #     print(f"Payslip Created for {emp.name}: {payslip.id}")
        #     lllllllllllllllllllllllllllllllllllllllllll

        return True

