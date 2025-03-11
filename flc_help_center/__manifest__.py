# __manifest__.py

{
    'name': 'Help',
    'version': '17.0',
    'category': 'Tools',
    'summary': 'Manage screenshots, videos, and FAQs.',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/help_center_data.xml',
        'views/help_center_views.xml',
        'wizard/help_center_pdf_wizard.xml',
        'views/menu_views.xml'
    ],
    'installable': True,
    'application': True,
}
