# -*- coding: utf-8 -*-
from odoo import models, fields


class HelpCenterScreenshot(models.Model):
    _name = 'help.center.screenshot'
    _description = 'Help Center Screenshot'

    name = fields.Char(string='Screenshot Title', required=True)
    app_id = fields.Many2one('help.center.app', string='App', required=True)
    image_url = fields.Char(string='Image URL', required=True)