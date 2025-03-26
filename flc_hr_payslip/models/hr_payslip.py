from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from calendar import monthrange
from odoo.odoo.tools.populate import compute


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    wage_without_currency = fields.Float(string="Wage (No Currency)", compute="_get_wage_without_currency")
    wage_in_words = fields.Char(string="Wage in Words", compute="_compute_wage_in_words")
    # Wages Earned
    employee_hra = fields.Float(string='HRA', compute='_get_hra')
    employee_da = fields.Float(string='DA', compute='_get_da')
    conveyance_allowance = fields.Float(string='Conveyance Allowance', compute='_get_conveyance_allowance')
    washing_allowance = fields.Float(string='Washing Allowance', compute='_get_washing_allowance')
    advance_bonus = fields.Float(string='Advance Bonus @8.33%', compute='_get_advance_bonus')
    other_allowance = fields.Float(string='Other Allowance', compute='_get_other_allowance')
    ph_wages = fields.Float(string='P H Wages', compute='_get_ph_wages')
    wage_advance_bonus = fields.Float(string="Advance Bonus", compute='_get_wage_advance_bonus')
    leave_payment = fields.Float(string='Leave Payment', compute='_get_leave_payment')
    partial_incentive = fields.Float(string='Partial Incentive', compute='_get_partial_incentive')
    food_allowance = fields.Float(string='Food Allowance', compute="_get_food_allowance")
    # Deductions
    provident_fund = fields.Float(string='Provident Fund (12%)')
    esic = fields.Float(string='ESIC (0.75%)')
    professional_tax = fields.Float(string='Professional Tax')
    glwf = fields.Float(string='G L W F')
    advance = fields.Float(string='Advance')
    canteen = fields.Float(string='Canteen Deduction')
    transport = fields.Float(string='Transport Deduction')
    other_loan = fields.Float(string='Other / Loan Deduction')
    fine = fields.Float(string='Fine')
    loss_or_damages = fields.Float(string='Loss or Damages')

    total_earned_wages = fields.Float(string="Total Earned Wages", compute="_compute_total_earned_wages", store=True)
    total_deductions = fields.Float(string="Total Deductions", compute="_compute_total_deductions", store=True)
    net_payable_wage = fields.Float(string="Net Payable Wage", compute="_compute_net_payable_wage", store=True)
    # Payable Days
    present_days = fields.Float(string='Present Days', default='25')
    ph_days = fields.Float(string='Public Holiday Days', compute='_compute_attendance_days')
    pl_days = fields.Float(string='Paid Leave Days', compute='_compute_attendance_days')
    overtime_hours = fields.Float(string='Overtime Hours', compute='_compute_attendance_days')
    weekly_off_days = fields.Float(string='Weekly Off Days', compute='_compute_attendance_days')
    total_payable_days = fields.Float(string='Total Payable Days', default='25')


    # def _compute_payable_days(self):
    #     for payslip in self:
    #         total_days = payslip.date_to.day - payslip.date_from.day + 1
    #         leave_days = self.env['hr.leave'].search_count([
    #             ('employee_id', '=', payslip.employee_id.id),
    #             ('state', '=', 'validate'),
    #             ('date_from', '>=', payslip.date_from),
    #             ('date_to', '<=', payslip.date_to)
    #         ])
    #         late_deductions = self.env['hr.attendance'].search_count([
    #             ('employee_id', '=', payslip.employee_id.id),
    #             ('is_late', '=', True),
    #             ('check_in', '>=', payslip.date_from),
    #             ('check_out', '<=', payslip.date_to)
    #         ])
    #         payslip.payable_days = total_days - leave_days - (late_deductions * 0.5)  # Half-day deduction per late

    def compute_salary(self):
        for payslip in self:
            daily_salary = payslip.contract_id.wage / 30  # Assuming 30-day month
            total_salary = daily_salary * payslip.payable_days

            payslip.write({'amount': total_salary})


    @api.model
    def get_current_datetime(self):
        """It  Will print Current Date and Time with Timezone On PDF footer"""
        # Get current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Convert to desired timezone
        local_tz = pytz.timezone(self.env.user.tz or 'UTC')
        local_now = utc_now.astimezone(local_tz)

        # Get timezone abbreviation
        tz_abbr = local_now.strftime('%Z')

        # Format date and time with timezone abbreviation
        return local_now.strftime('%B %d, %Y %I:%M:%S %p') + ' ' + tz_abbr

    @api.depends()
    def _compute_attendance_days(self):
        return True

    # @api.depends('present_days', 'ph_days', 'pl_days', 'weekly_off_days', 'overtime_hours')
    # def _compute_total_payable_days(self):
    #     for payslip in self:
    #         payslip.total_payable_days = (
    #                 payslip.present_days + payslip.ph_days + payslip.pl_days + payslip.weekly_off_days + (
    #                     payslip.overtime_hours / 8)
    #         )
    @api.depends('present_days', 'ph_days', 'pl_days', 'weekly_off_days', 'overtime_hours')
    def _compute_total_payable_days(self):
        for payslip in self:
            payslip.total_payable_days = (
                    payslip.present_days + payslip.ph_days + payslip.pl_days + payslip.weekly_off_days + (
                        payslip.overtime_hours / 8))

    @api.depends('line_ids', 'line_ids.total')
    def _compute_amount_in_words(self):
        for payslip in self:
            net_salary = 0.0
            for line in payslip.line_ids:
                if line.code == 'NET':
                    net_salary = line.total
                    break

            payslip.amount_in_words = payslip.currency_id.amount_to_text(net_salary)

    # @api.depends('total_earned_wages', 'total_deductions')
    # def _compute_net_payable_wage(self):
    #     for payslip in self:
    #         payslip.net_payable_wage = payslip.total_earned_wages - payslip.total_deductions
    @api.depends('total_earned_wages', 'total_deductions')
    def _compute_net_payable_wage(self):
        for payslip in self:
            payslip.net_payable_wage = payslip.total_earned_wages - payslip.total_deductions

    # @api.depends('employee_id')
    # def _compute_total_deductions(self):
    #     for payslip in self:
    #         payslip.total_deductions = (
    #                 float(payslip.employee_id.provident_fund or 0) +
    #                 float(payslip.employee_id.employee_esic or 0) +
    #                 float(payslip.employee_id.professional_tax or 0)
    #         )

    @api.depends('provident_fund', 'esic', 'professional_tax', 'glwf', 'advance', 'canteen', 'transport', 'other_loan',
                 'fine', 'loss_or_damages')
    def _compute_total_deductions(self):
        for payslip in self:
            payslip.total_deductions = (
                    payslip.provident_fund + payslip.esic + payslip.professional_tax +
                    payslip.glwf + payslip.advance + payslip.canteen + payslip.transport +
                    payslip.other_loan + payslip.fine + payslip.loss_or_damages
            )

    # @api.depends('employee_hra', 'employee_da')
    # def _compute_total_earned_wages(self):
    #     for payslip in self:
    #         payslip.total_earned_wages = payslip.employee_hra + payslip.employee_da
    @api.depends('employee_hra', 'employee_da', 'conveyance_allowance', 'washing_allowance', 'advance_bonus',
                 'other_allowance', 'ph_wages', 'leave_payment', 'partial_incentive', 'food_allowance')
    def _compute_total_earned_wages(self):
        for payslip in self:
            payslip.total_earned_wages = (
                    payslip.employee_hra + payslip.employee_da + payslip.conveyance_allowance +
                    payslip.washing_allowance + payslip.advance_bonus + payslip.other_allowance +
                    payslip.ph_wages + payslip.leave_payment + payslip.partial_incentive + payslip.food_allowance
            )
    def _get_food_allowance(self):
        """This Method is Used For Food Allowance in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.food_allowance = rec.employee_id.contract_id.wage_food

    def _get_partial_incentive(self):
        """This Method is Used For Partial Incentive in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.partial_incentive = rec.employee_id.contract_id.wage_par_incentive

    def _get_leave_payment(self):
        """This Method is Used For Leave Payment in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.leave_payment = rec.employee_id.contract_id.wage_leave_payment

    def _get_wage_advance_bonus(self):
        """This Method is Used For Advance Bonus in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.wage_advance_bonus = rec.employee_id.contract_id.wage_advance_bonus

    def _get_ph_wages(self):
        """This Method is Used For PH Wages in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.ph_wages = rec.employee_id.contract_id.wage_ph

    def _get_other_allowance(self):
        """This Method is Used For Other Allowance in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.other_allowance = rec.employee_id.contract_id.wage_other_allowance

    def _get_advance_bonus(self):
        """Advance Bonus @8.33%"""
        for rec in self:
            rec.advance_bonus = rec.employee_id.contract_id.wage_bonus

    def _get_washing_allowance(self):
        """This Method is Used For Washing Allowance in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.washing_allowance = rec.employee_id.contract_id.wage_washing if rec.employee_id.contract_id else 0

    def _get_conveyance_allowance(self):
        """This method is Used For Conveyance Allowance in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.conveyance_allowance = rec.employee_id.contract_id.wage_conveyance

    def _get_hra(self):
        """This Method is Used For HRA in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.employee_hra = rec.employee_id.contract_id.wage_hra

    def _get_da(self):
        """This Method is Used For DA in Pay Slip and Data getting Form Hr contract"""
        for rec in self:
            rec.employee_da = rec.employee_id.contract_id.da

    def _get_wage_without_currency(self):
        for rec in self:
            rec.wage_without_currency = rec.employee_id.contract_id.wage

    @api.depends('net_payable_wage')
    def _compute_wage_in_words(self):
        for rec in self:
            if rec.net_payable_wage:
                amount_in_words = rec.number_to_words(rec.net_payable_wage)
                currency_name = rec.company_id.currency_id.name or "Rupees"
                rec.wage_in_words = f"{amount_in_words} {currency_name} Only"
            else:
                rec.wage_in_words = " "

    def number_to_words(self, num):
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen',
                 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

        def _convert_below_thousand(n):
            if n < 10:
                return ones[n]
            elif n < 20:
                return teens[n - 10]
            elif n < 100:
                return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
            else:
                return ones[n // 100] + ' Hundred' + (
                    '' if n % 100 == 0 else ' and ' + _convert_below_thousand(n % 100))

        if num == 0:
            return 'Zero'

        # Split amount into rupees and paise
        rupees = int(num)
        paise = int(round((num - rupees) * 100))

        # Convert rupees to words
        result = ''
        if rupees >= 10000000:  # Crore
            result += _convert_below_thousand(rupees // 10000000) + ' Crore '
            rupees %= 10000000

        if rupees >= 100000:  # Lakh
            result += _convert_below_thousand(rupees // 100000) + ' Lakh '
            rupees %= 100000

        if rupees >= 1000:  # Thousand
            result += _convert_below_thousand(rupees // 1000) + ' Thousand '
            rupees %= 1000

        if rupees > 0:
            result += _convert_below_thousand(rupees)

        # Add paise if applicable
        if paise > 0:
            result += ' and ' + _convert_below_thousand(paise) + ' Paise'

        return result.strip()
