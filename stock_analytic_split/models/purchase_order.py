# -*- coding: utf-8 -*-

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    # In Odoo 19, analytic_distribution should already be on purchase.order.line
    # This file is here to ensure compatibility and add any additional methods if needed
    
    # The analytic_distribution field is automatically inherited from account.analytic.mixin
    # which is already in the _inherit chain for purchase.order.line in standard Odoo
