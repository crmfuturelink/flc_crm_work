from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    biometric_id = fields.Char("Biometric ID", help="Biometric device user ID")
