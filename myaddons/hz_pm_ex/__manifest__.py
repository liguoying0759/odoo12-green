# -*- coding: utf-8 -*-
{
    'name': "HZ_PM项目管理",
    'category' : 'Projects',

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        HZ_PM项目管理
    """,

    'author': "lgy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'hr_timesheet', 'project_forecast'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_task.xml',
        'views/project_project.xml',
        # 'views/mail_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}