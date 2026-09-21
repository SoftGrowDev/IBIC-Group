{
    'name': 'Analytic USD Report',
    'version': '19.0.1.0.0',
    'summary': 'USD analytic line enhancement with PDF and XLSX reports',
    'category': 'Accounting',
    'author': 'OpenAI',
    'depends': [
        'analytic',
        'account',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_line_views.xml',
        'wizard/analytic_line_report_wizard_views.xml',
        'report/analytic_line_report.xml',
        'report/analytic_line_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
