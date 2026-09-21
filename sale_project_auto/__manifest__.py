{
    'name': 'Sale Order Auto Project & Analytic',
    'version': '19.0.1.0.0',
    'summary': 'Auto-create Project and Analytic Account on Sale Order Confirmation',
    'description': """
        When a Sale Order is confirmed:
        - Automatically creates a Project named after the Sale Order
        - Creates an Analytic Account with the same name
        - Links the Analytic Account to the Project
        - Assigns the Analytic Account to all Sale Order lines
    """,
    'author': 'Custom',
    'category': 'Sales/Sales',
    'depends': [
        'sale_management',
        'project',
        'analytic',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
