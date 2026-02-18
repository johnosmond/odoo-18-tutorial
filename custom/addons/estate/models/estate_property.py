# -*- coding: utf-8 -*-
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
	_name = 'estate.property'
	_description = 'Estate Property'

	name = fields.Char(required=True)
	description = fields.Text()
	postcode = fields.Char()
	date_availability = fields.Date(
		copy=False,
		default=lambda self: fields.Date.today() + relativedelta(months=3)
	)
	expected_price = fields.Float(copy=False)
	selling_price = fields.Float(readonly=True)
	bedrooms = fields.Integer(default=2)
	living_area = fields.Integer(string='Living Area (sqm)')
	facades = fields.Integer()
	garage = fields.Boolean()
	garden = fields.Boolean()
	garden_area = fields.Integer(string='Garden Area (sqm)')
	garden_orientation = fields.Selection(
		[
			('north', 'North'),
			('south', 'South'),
			('east', 'East'),
			('west', 'West'),
		]
	)
	active = fields.Boolean(default=True)

	state = fields.Selection(
		[
			('new', 'New Listing'),
			('offer_received', 'Offer Received'),
			('offer_accepted', 'Offer Accepted'),
			('sold', 'Sold'),
			('cancelled', 'Cancelled'),
		],
		string='Status',
		default='new',
		required=True,
		copy=False,
	)

	property_type_id = fields.Many2one(
		"estate.property.type",
		string="Property Type"
	)
	
	tag_ids = fields.Many2many(
		"estate.property.tag",
		string="Tags",
	)
	
	offer_ids = fields.One2many(
		"estate.property.offer",
		"property_id",
		string="Offers",
	)

	def action_set_sold(self):
		for record in self:
			record.state = 'sold'

	def action_set_cancelled(self):
		for record in self:
			record.state = 'cancelled'

	total_area = fields.Float(
		string='Total Area (sqm)',
		compute='_compute_total_area',
		store=True
	)

	@api.depends('living_area', 'garden_area')
	def _compute_total_area(self):
		for record in self:
			record.total_area = (record.living_area or 0) + (record.garden_area or 0)

	@api.onchange("garden")
	def _onchange_garden(self):
		if self.garden:
			self.garden_area = 10
			self.garden_orientation = "north"
		else:
			self.garden_area = 0
			self.garden_orientation = False