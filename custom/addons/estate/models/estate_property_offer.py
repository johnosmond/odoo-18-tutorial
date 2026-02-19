# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
	_name = "estate.property.offer"
	_description = "Real Estate Property Offer"

	price = fields.Float()

	_sql_constraints = [
		("check_price_positive", "CHECK(price > 0)", "Offer price must be strictly positive."),
	]

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

	active = fields.Boolean(default=True)
	
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

		# Prevent accepting if another offer is already accepted
		accepted_offer = self.property_id.offer_ids.filtered(
			lambda o: o.status == "accepted" and o != self
		)
		if accepted_offer:
			raise UserError("An offer has already been accepted for this property.")

		# build soft warnings (do not block)
		warnings = []

		expected = getattr(self.property_id, "expected_price", None)
		if expected and self.price < expected:
			warnings.append(_("The offer price is below the expected price (%s).") % expected)

		# best offer excluding the current one; ignore refused offers
		other_offers = self.property_id.offer_ids.filtered(
			lambda o: o.id != self.id and o.status != "refused"
		)
		best = max(other_offers.mapped("price"), default=0)
		if best and self.price < best:
			warnings.append(_("The offer price is below the best offer (%s).") % best)

		# If warnings exist, open wizard unless explicitly bypassed
		if warnings and not self.env.context.get("bypass_low_offer_warning"):
			wizard = self.env["estate.offer.warning.wizard"].create({
				"offer_id": self.id,
				"message": "\n".join(warnings),
			})
			return {
				"type": "ir.actions.act_window",
				"name": _("Low Offer Warning"),
				"res_model": "estate.offer.warning.wizard",
				"view_mode": "form",
				"res_id": wizard.id,
				"target": "new",
			}

		# Accept this offer
		self.status = "accepted"

		# Refuse all other offers for the same property (optional but usually desired)
		other_offers = self.property_id.offer_ids - self
		other_offers.filtered(lambda o: o.status != "refused").write({"status": "refused"})

		# Update the property so the statebar reflects the change
		self.property_id.write({"state": "offer_accepted"})
		
		return {"type": "ir.actions.client", "tag": "reload"}
	
	def action_refuse(self):
		for offer in self:
			offer.status = "refused"
		return {"type": "ir.actions.client", "tag": "reload"}
	
	# validity and deadline computation
	validity = fields.Integer(
		string="Validity (days)",
		default=7,
	)

	date_deadline = fields.Date(
		string="Deadline",
		compute="_compute_date_deadline",
		inverse="_inverse_date_deadline",
		store=True,
	)

	@api.depends("create_date", "validity")
	def _compute_date_deadline(self):
		for record in self:
			# create_date is empty until the record is saved the first time
			base_date = (record.create_date.date() if record.create_date else fields.Date.context_today(record))
			record.date_deadline = base_date + timedelta(days=record.validity or 0)

	def _inverse_date_deadline(self):
		for record in self:
			if not record.date_deadline:
				record.validity = 0
				continue
			base_date = (record.create_date.date() if record.create_date else fields.Date.context_today(record))
			record.validity = (record.date_deadline - base_date).days
