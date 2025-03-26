# __manifest__.py
{
    'name': 'FLC HR Management',
    'version': '1.0',
    'summary': 'Custom HR Management for FLC',
    'description': """
        Custom HR Management module for FLC with advanced leave and attendance tracking.
        - Custom employee types
        - Flexible work schedules
        - Probation management
        - Advanced leave policies
        - Biometric attendance integration
    """,
    'category': 'Human Resources',
    'author': 'FLC',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/hr_employee_type_data.xml',
        # 'data/hr_work_schedule_data.xml',
        # 'views/hr_employee_type_views.xml',
        # 'views/hr_work_schedule_views.xml',
        # 'views/hr_probation_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': True,
}