from odoo import models, fields, api

class HelpCenterApp(models.Model):
    _name = "help.center.app"
    _description = "Help Center Items"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    type = fields.Selection([
        ('screenshot', 'Screenshot'),
        ('video', 'Video'),
        ('faq', 'FAQ')
    ], string="Type", required=True)
    is_screenshoot = fields.Boolean(string="Is Screenshot")
    is_video = fields.Boolean(string="Is video")
    is_faq = fields.Boolean(string="Is FAQ")
    sequence = fields.Integer(string="Sequence", default=10)
    image = fields.Binary(string="Image")  # If storing images for screenshots
    video_url = fields.Char(string="Video URL")  # If video type
    answer = fields.Html(string="FAQ Answer")  # If FAQ type
    document = fields.Binary(string="Upload PDF")
    document_filename = fields.Char(string="Filename")

    # video_url = fields.Char(string="Video URL")  # For external links
    video_attachment = fields.Binary(string="Upload Video")  # For uploaded videos
    video_attachment_filename = fields.Char(string="Video Filename")  # To store file name

    # def open_time_off(self):
    #     print("This is a test")
    #
    #     return True

    # def open_time_off(self):
    #     pdf_url = "/web/content?model=help.center.app&id=%s&field=document&filename_field=name&download=true" % self.id
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': pdf_url,
    #         'target': 'new',
    #     }

    def open_time_off(self):
        """Open the PDF in a popup wizard"""
        return {
            'name': 'PDF Preview',
            'type': 'ir.actions.act_window',
            'res_model': 'help.center.pdf.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pdf_binary': self.document,
                'default_pdf_filename': self.document_filename,
            }
        }

    def open_employee(self):
        print("This is a test")

        return True

    def open_attendance(self):
        print("This is a test")

        return True


class HelpCenterPDFWizard(models.TransientModel):
    _name = 'help.center.pdf.wizard'
    _description = 'PDF Preview Wizard'

    pdf_binary = fields.Binary(string="PDF File", readonly=True)
    pdf_filename = fields.Char(string="Filename", readonly=True)