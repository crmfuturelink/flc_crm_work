{
    'name': 'CRM Stage Restriction',
    'version': '17.0',
    'category': 'Sales/CRM',
    'summary': 'Restrict CRM Stages based on user roles',
    'author': 'Your Name',
    'depends': ['crm', 'mail'],
    'data': [
        'security/crm_security.xml',
        # 'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'views/crm_stage_views.xml',
    ],
    'installable': True,
    'application': False,
}
