from odoo import api, fields, models


class CmPlace(models.Model):
    _inherit = "cm.place"

    key_submissions_target_reached = fields.Boolean(
        string="Key submissions target reached",
        compute="compute_key_submissions_target_reached",
        store=True
    )

    @api.depends("form_submission_ids")
    def compute_key_submissions_target_reached(self):
        for record in self:
            if record.map_id.key_submissions_target > 0:
                record.key_submissions_target_reached = (
                    len(record.form_submission_ids.filtered(lambda submission: submission.is_key_submission == True))
                    >= record.map_id.key_submissions_target
                )
            else:
                record.key_submissions_target_reached = False


    def crowdfunding_notifications(self, request, submission_id=False, submissions_notified=False):
        if request.notify_key_submissions:
            for submission in self.form_submission_ids:
                # This conditional avoids sending crowdfunding notification to a newly created submission.
                # They'll receive the general autoresponder
                submissions_notified = []
                if submission.id != submission_id or not submission_id:
                    if submission.is_key_submission:
                        submissions_notified.append(submission.id)
                        template = request.template_key_submissions
                        template.send_mail(
                            res_id=submission.id,
                            force_send=True,
                            email_layout_xmlid="mail.mail_notification_layout",
                        )
        super().crowdfunding_notifications(request, submission_id, submissions_notified)
