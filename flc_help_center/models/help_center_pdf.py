from odoo import models, fields

class HelpCenterPDF(models.Model):
    _name = 'help.center.pdf'
    _description = 'Help Center PDF Viewer'

    name = fields.Char("Document Name", required=True)
    pdf_binary = fields.Binary("PDF File", required=True)
    pdf_filename = fields.Char("Filename")
