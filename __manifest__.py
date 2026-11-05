# -*- coding: utf-8 -*-
{
    'name': "Consultation",

    'summary': "Manage patients, doctors, departments, and medical appointments",

    'description': """
Long description of module's purpose
    """,

    'author': "Thaw Zin Htet",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Healthcare',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

