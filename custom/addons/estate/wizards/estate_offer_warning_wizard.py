# -*- coding: utf-8 -*-
from odoo import fields, models

class EstateOfferWarningWizard(models.TransientModel):
    _name = "estate.offer.warning.wizard"
    _description = "Offer Acceptance Warning"

    offer_id = fields.Many2one("estate.property.offer", required=True)
    message = fields.Text(readonly=True, required=True)

    def action_accept_anyway(self):
        self.ensure_one()
        # bypass warning wizard loop and accept
        self.offer_id.with_context(bypass_low_offer_warning=True).action_accept()
        # close wizard + refresh UI
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_discard(self):
        # close wizard, do nothing
        return {"type": "ir.actions.act_window_close"}
