from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    wage_without_currency = fields.Float(string="Wage (No Currency)", compute="_get_wage_without_currency")
    wage_in_words = fields.Char(string="Wage in Words", compute="_compute_wage_in_words")
    # employee_category = fields.Selection([
    #     ('consultant', 'Consultant'),
    #     ('education', 'Education-Based')
    # ], string="Employee Category", default='consultant')
    employee_hra = fields.Float(string='HRA', compute='_get_hra')
    employee_da = fields.Float(string='DA', compute='_get_da')
    total_earned_wages = fields.Float(string="Total Earned Wages", compute="_compute_total_earned_wages", store=True)
    total_deductions = fields.Float(string="Total Deductions", compute="_compute_total_deductions", store=True)
    net_payable_wage = fields.Float(string="Net Payable Wage", compute="_compute_net_payable_wage", store=True)

    @api.depends('total_earned_wages', 'total_deductions')
    def _compute_net_payable_wage(self):
        for payslip in self:
            payslip.net_payable_wage = payslip.total_earned_wages - payslip.total_deductions

    @api.depends('employee_id')
    def _compute_total_deductions(self):
        for payslip in self:
            payslip.total_deductions = (
                    float(payslip.employee_id.provident_fund or 0) +
                    float(payslip.employee_id.employee_esic or 0) +
                    float(payslip.employee_id.professional_tax or 0)
            )

    @api.depends('employee_hra', 'employee_da')
    def _compute_total_earned_wages(self):
        for payslip in self:
            payslip.total_earned_wages = payslip.employee_hra + payslip.employee_da

    def _get_hra(self):
        for rec in self:
            rec.employee_hra = rec.employee_id.contract_id.hra

    def _get_da(self):
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