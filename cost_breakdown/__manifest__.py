{
    'name': 'Estimated Cost Breakdown',
    'version': '19.0.1.3.0',
    'category': 'Sales/Sales',
    'summary': 'Estimated Cost Breakdown per Sale Order Line with BOM integration',
    'description': """
        - Adds an Estimated Cost Breakdown model linked to Sale Order lines
        - Button on Sale Order to auto-generate estimated cost breakdowns per line
        - Uses BOM components when available; BOM qty scaled by SO qty
        - Sale Price in USD and EGP with configurable FX rate
        - Margin and Margin % shown in both USD and EGP
        - Smart button always opens as list view
        - Product Nature field on product template; auto-filled on breakdown lines
    """,
    'author': 'eTRIPLE SOFT',
    'depends': ['sale_management', 'mrp', 'stock', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/product_type_views.xml',
        'views/product_template_views.xml',
        'views/cost_breakdown_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
