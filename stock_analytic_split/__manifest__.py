# -*- coding: utf-8 -*-
{
    'name': 'Stock Analytic Distribution',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Split stock costs across multiple analytic accounts with auto-sync from PO/SO',
    'description': """
Stock Analytic Distribution
============================

Bring the power of analytic accounting directly to your stock transfers.
Split costs across multiple analytic accounts — the same way you do on invoices.
Now with **auto-sync from Purchase Orders and Sales Orders** — analytic is pulled automatically from the source document.

Key Features
------------
* 🎯 Analytic Widget on Move Lines - The native analytic_distribution widget appears on every product line
* 🔄 Auto-Sync from PO / SO Lines - Each stock move inherits the analytic from the matching PO or SO line automatically
* ✏️ Manual Entry for Standalone Transfers - Internal transfers remain fully editable
* ✅ Auto Analytic Lines on Validate - When you validate a transfer, analytic lines are automatically created
* 🔗 Full Stock Traceability - Analytic lines are linked back to stock.move and stock.picking
* 🌍 Arabic Translation + Multi-Plan - Supports multiple analytic plans and percentage splits simultaneously

How It Works
------------
1. Set Analytic on PO/SO Line
2. Confirm the Order - Odoo creates the linked receipt or delivery automatically
3. Analytic Auto-Applied - Open the receipt/delivery and find the analytic already filled from the source document
4. Validate - Click Validate. Analytic lines are created automatically per distribution
5. Standalone Transfers - For transfers without PO/SO, set the analytic manually on the header or per line

Technical Notes
---------------
* Auto-sync uses stock.move.purchase_line_id and stock.move.sale_line_id to match move → order line
* Works safely with or without sale_stock module installed
* Header analytic stored as JSON in stock.picking.analytic_distribution
* Per-line analytic uses stock.move.analytic_distribution
* Cost source uses stock_valuation_layer_ids.value; falls back to standard_price × qty
    """,
    'author': 'Haytham Afify',
    'website': 'https://github.com/haythamafify',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'stock_account',
        'analytic',
        'purchase_stock',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/stock_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
