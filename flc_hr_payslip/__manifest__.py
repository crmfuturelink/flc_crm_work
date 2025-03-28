{
    'name': 'FLC HR Payslip',
    'category': 'Generic Modules/Human Resources',
    'version': '17.0.1.0.4',
    'sequence': 1,
    'author': 'Developer FLC',
    'summary': 'Payroll For Odoo 17 Community Edition',
    'description': "FLC Pay Slip PDF",
    'website': '',
    'license': 'LGPL-3',
    'depends': ['om_hr_payroll', 'hr', 'hr_holidays', 'flc_biometric_integration'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_leave_security.xml',
        'data/ir_cron.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_leave_view.xml',
        'views/hr_payslip_view.xml',
        'wizard/hr_probation_wizard_views.xml',
        'reports/flc_payslip_report.xml',
        'reports/flc_payslip_report_template.xml',
        # 'reports/future_link_payslip_template.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'flc_hr_paysli/static/src/scss/font-family.scss',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': True
}
