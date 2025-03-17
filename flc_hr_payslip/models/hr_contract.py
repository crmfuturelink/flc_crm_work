from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Wages Earned Fields
    wage_basic_da = fields.Float(string="Basic + DA")
    wage_hra = fields.Float(string="House Rent Allowance")
    wage_conveyance = fields.Float(string="Conveyance Allowance")
    wage_washing = fields.Float(string="Washing Allowance")
    wage_bonus = fields.Float(string="Advance Bonus @8.33%")
    wage_other_allowance = fields.Float(string="Other Allowance")
    wage_ph = fields.Float(string="P H Wages")
    wage_advance_bonus = fields.Float(string="Advance Bonus")
    wage_leave_payment = fields.Float(string="Leave Payment")
    wage_par_incentive = fields.Float(string="Par. Incentive")
    wage_food = fields.Float(string="Food Allowance")

    # Deductions Fields
    deduction_pf = fields.Float(string="Provident Fund (12%)")
    deduction_esic = fields.Float(string="ESIC @0.75%")
    deduction_prof_tax = fields.Float(string="Professional Tax")
    deduction_glwf = fields.Float(string="G L W F")
    deduction_advance = fields.Float(string="Advance")
    deduction_canteen = fields.Float(string="Canteen")
    deduction_transport = fields.Float(string="Transport")
    deduction_other_loan = fields.Float(string="Other / Loan")
    deduction_fine = fields.Float(string="Fine")
    deduction_loss_damage = fields.Float(string="Loss or Damages")
