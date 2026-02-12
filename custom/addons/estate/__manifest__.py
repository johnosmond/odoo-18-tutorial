# -*- coding: utf-8 -*-
{
    'name': 'Estate',
    'version': '1.0',
    'summary': 'Estate management',
    'depends': ['base'],
    'data': [
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
    ],
    'installable': True,
    'application': True,
}
