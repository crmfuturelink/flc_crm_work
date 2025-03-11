# -*- coding: utf-8 -*-
###############################################################################
#
#    Future Link Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Future Link Pvt. Ltd. (<https://futurelinkconsultants.com>)
#    Author: Ranjan  (crmdeveloper@futurelinkconsultants.com)
#
#
###############################################################################

{
    'name': 'FLC Biometric Integration',
    'version': '17.0',
    'summary': 'Integrate Identix Model K90-Pro & eTimeTrackLite with Odoo for attendance tracking.',
    'description': """
        This module integrates the Identix Model K90-Pro biometric device with Odoo.
        It fetches attendance logs from the eTimeTrackLite Web API and synchronizes them with Odoo's HR module.
    """,
    'author': 'Ranjan / FLC',
    'category': 'Human Resources',
    'depends': ['base','hr'],

    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'views/biometric_views.xml',
        'views/hr_employee_view.xml',
        # 'views/company_view.xml',
        'wizard/biometric_attendance_wizard.xml',
        'wizard/monthly_status_report_view.xml',
        'wizard/BiometricAttendanceRegisterReport_view.xml',
        'reports/flc_attendance_report.xml',
        'reports/flc_attendance_report_template.xml',
        'reports/biometric_attendance_register_template_v1.xml',
        'views/menu_item.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
