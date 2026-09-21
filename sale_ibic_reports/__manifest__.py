# -*- coding: utf-8 -*-
{
    'name': 'IBIC Sale Reports – Proforma Invoice, Packing List & Stock Picking',
    'version': '19.0.2.14.0',
    'summary': (
        'Proforma Invoice and Packing List reports from Sale Orders (IBIC format). '
        'Extended with Product Packaging Info, KG Weight reference, '
        'and Stock Picking Packing List with pallet management.'
    ),
    'author': 'Custom',
    'category': 'Sales',
    'depends': ['sale_management', 'account', 'stock', 'uom', 'tk_freight'],
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'data/kg_weight_data.xml',
        'report/stock_picking_report_actions.xml',
        'views/res_company_views.xml',
        'views/uom_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/invoice_views.xml',
        'views/stock_picking_views.xml',
        'report/report_actions.xml',
        'report/proforma_invoice_template.xml',
        'report/packing_list_template.xml',
        'report/invoice_report_actions.xml',
        'report/invoice_proforma_template.xml',
        'report/invoice_packing_list_template.xml',
        'report/stock_picking_packing_list_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
