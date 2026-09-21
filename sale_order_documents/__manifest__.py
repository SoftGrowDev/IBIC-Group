{
    'name': 'Sale Order Documents',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Documents on Sale Order transferred to Invoice',
    'depends': [
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        # 'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
