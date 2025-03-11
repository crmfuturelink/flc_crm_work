# -*- coding: utf-8 -*-
from odoo import models, fields

class HelpCenterFAQ(models.Model):
    _name = 'help.center.faq'
    _description = 'Help Center FAQ'

    question = fields.Char(string='Question', required=True)
    answer = fields.Text(string='Answer', required=True)
    app_id = fields.Many2one('help.center.app', string='App', required=True)