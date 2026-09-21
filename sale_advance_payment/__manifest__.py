{
    'name': 'Sale Order Advance Payment',
    'version': '19.0.1.8',
    'category': 'Sales',
    'summary': 'Create and manage advance down payments directly from Sale Orders',
    'description': """
        Allows users to register advance/down payments directly from the Sale Order.
        Features:
        - Advance Payment button on confirmed Sale Orders
        - Wizard to select journal and amount
        - Payment Advance tab listing all advance payments
        - Advance payments appear as outstanding credits when invoicing
        - Easy reconciliation with generated invoices
    """,
    'author': 'Technonet',
    'depends': ['sale_management', 'account', 'stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_advance_payment_wizard_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
