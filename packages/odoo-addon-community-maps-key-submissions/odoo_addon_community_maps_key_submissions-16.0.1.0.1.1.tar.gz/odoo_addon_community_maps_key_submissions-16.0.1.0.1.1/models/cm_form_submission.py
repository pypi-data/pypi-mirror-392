from odoo import api, fields, models


class CmFormSubmission(models.Model):
    _inherit = "crm.lead"

    is_key_submission = fields.Boolean(string="Key submission", compute="compute_is_key_submission",store="True")
    key_submissions_target_reached = fields.Boolean(related="place_id.key_submissions_target_reached")

    @api.depends("form_submission_metadata_ids")
    def compute_is_key_submission(self):
        for record in self:
            filtered_metadata_ids = record.form_submission_metadata_ids.filtered(
                lambda meta: (
                    meta.key == record.place_id.map_id.key_submissions_metadata_key and
                    meta.value in record.place_id.map_id.key_submissions_metadata_values.split(',')
                )
            )
            record.is_key_submission = bool(filtered_metadata_ids)

