# -*- coding: utf-8 -*-
{
	'name': 'Estate',
	'version': '1.0',
	'summary': 'Estate management',
	'depends': ['base'],
	'data': [
		'security/estate_security.xml',
		'security/ir.model.access.csv',
		'views/estate_menus.xml',
		'views/estate_property_views.xml',
		'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
		'views/estate_offer_warning_wizard_views.xml',
		'views/estate_offer_list.xml',
	],
	'installable': True,
	'application': True,
}
