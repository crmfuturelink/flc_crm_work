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

from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    biometric_id = fields.Char("Biometric ID", help="Biometric device user ID")
