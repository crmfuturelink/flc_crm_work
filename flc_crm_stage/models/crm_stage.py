from odoo import models, fields, api

class CRMStage(models.Model):
    _inherit = "crm.stage"

    allowed_groups = fields.Many2many(
        'res.groups', string="Allowed Groups",
        help="Only users in these groups can see this stage"
    )

    @api.model
    def get_user_allowed_stages(self):
        """Return stages based on user group access."""
        user = self.env.user
        return self.search([
            '|', ('allowed_groups', 'in', user.groups_id.ids), ('allowed_groups', '=', False)
        ])
