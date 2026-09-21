{
    'name': 'Sale Full Feature Group',
    'version': '19.0.1.2.0',
    'category': 'Sales',
    'summary': 'Controls visibility of Sale Order buttons, smart buttons and tabs based on user group',
    'description': """
See Full Features – Sales group
================================
WITH the group:
  - All header buttons visible
  - All smart buttons visible
  - All notebook pages visible

WITHOUT the group:
  Before sale (draft / sent / to_approve):
    Pages  : Order Lines · Shipping Info · Other Info
    Buttons: Confirm · Create Estimated Cost Breakdown · Send · Preview

  On sale / done:
    Pages  : Order Lines · Shipping Info · Other Info
    Buttons: Send · Preview

  Smart buttons : always hidden
  Advance Payment button : always hidden
    """,
    'author': 'Custom',
    'depends': [
        'sale_management',
        'cost_breakdown',
        'sale_ibic_reports',
        'sale_advance_payment',
        'sale_order_documents',
        'sale_project_auto',
        'sales_order_double_approval',
    ],
    'data': [
        'security/security.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
