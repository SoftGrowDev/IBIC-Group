# -*- coding: utf-8 -*-
{
    "name": "Invoice PO Reference",
    "summary": "Adds a mandatory PO Reference field visible only on customer invoices",
    "description": """
Invoice PO Reference
=====================
Adds a "PO Reference" field on the invoice (account.move) that:

* Is only shown on customer invoices and credit notes (not on vendor bills
  or miscellaneous journal entries).
* Is mandatory before the invoice can be confirmed/posted.
""",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "BBR Networks",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
