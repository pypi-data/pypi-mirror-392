from odoo import api, fields, models


class CmMap(models.Model):
    _inherit = "cm.map"

    key_submissions_metadata_key = fields.Char(string="Metadata key to identify key submissions")
    key_submissions_metadata_values = fields.Char(string="Metadata values to identify key submissions")
    key_submissions_target = fields.Integer(string="Target number of key submissions")

    @api.constrains('key_submissions_metadata_key','key_submissions_metadata_values')
    def propagate_submissions_is_key_submission(self):
        submissions = self.env['crm.lead'].search([('submission_type','in',["place_submission","place_proposal_submission"])])
        for submission in submissions:
            submission.compute_is_key_submission()
        for place in submissions.mapped("place_id"):
            place.compute_key_submissions_target_reached()

    @api.constrains("key_submissions_target")
    def propagate_key_submissions_target_reached(self):
        places = self.env['cm.place'].search([])
        for place in places:
            place.compute_key_submissions_target_reached()


