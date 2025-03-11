# -*- coding: utf-8 -*-

from odoo import models, fields


class HelpCenterVideo(models.Model):
    _name = 'help.center.video'
    _description = 'Help Center Video'

    name = fields.Char(string='Video Title', required=True)
    app_id = fields.Many2one('help.center.app', string='App', required=True)
    video_url = fields.Char(string='Video URL', required=True)
