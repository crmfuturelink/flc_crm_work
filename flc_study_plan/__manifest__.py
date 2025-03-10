{
    'name': 'FLC Study Plan',
    'category': 'Generic Modules/Human Resources',
    'version': '17.0.1.0.4',
    'sequence': 1,
    'author': 'Developer FLC',
    'summary': ' FLC ',
    'description': "FLC Pay Slip PDF",
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/flc_student_view.xml'
    ],

    'installable': True,
    'application': True,
    'auto_install': True
}
