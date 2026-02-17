# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import fields, models, api

class EstatePropertyOffer(models.Model):
	_name = "estate.property.offer"
	_description = "Real Estate Property Offer"

	price = fields.Float()

	status = fields.Selection(
		[
			("accepted", "Accepted"),
			("refused", "Refused"),
		],
		copy=False,
	)

	partner_id = fields.Many2one(
		"res.partner",
		string="Buyer",
	)

	property_id = fields.Many2one(
		"estate.property",
		string="Property",
		required=True,
		ondelete="cascade",
	)
	validity = fields.Integer(default=7)
	date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)

	@api.depends('validity')
	def _compute_date_deadline(self):
		for offer in self:
			offer.date_deadline = fields.Date.add(fields.Date.today(), days=offer.validity or 0)

	def _inverse_date_deadline(self):
		for offer in self:
			if offer.date_deadline:
				offer.validity = (offer.date_deadline - fields.Date.today()).days
			else:
				offer.validity = 0

	def action_accept(self):
		self.ensure_one()

		# Accept this offer
		self.status = "accepted"

		# Refuse all other offers for the same property (optional but usually desired)
		other_offers = self.property_id.offer_ids - self
		other_offers.filtered(lambda o: o.status != "refused").write({"status": "refused"})

		# Update the property so the statebar reflects the change
		self.property_id.write({
			"state": "offer_accepted",
		})
		return True
	
	def action_refuse(self):
		for offer in self:
			offer.status = "refused"
		return True