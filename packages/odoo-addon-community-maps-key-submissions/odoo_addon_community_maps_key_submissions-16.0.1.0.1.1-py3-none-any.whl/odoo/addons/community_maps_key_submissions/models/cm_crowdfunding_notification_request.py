from odoo import fields, models


class CmPlaceCrowdfundingNotificationRequest(models.Model):
    _inherit = "cm.crowdfunding.notification.request"

    notify_key_submissions = fields.Boolean(string="Notify key submissions")
    template_key_submissions = fields.Many2one(
        "mail.template",
        string="Template key submissions",
        domain=[("model", "=", "crm.lead")]
    )

