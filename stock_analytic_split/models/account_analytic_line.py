# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        ondelete='set null',
        help='Link to stock move that generated this analytic line',
        index=True,
    )
    
    stock_picking_id = fields.Many2one(
        'stock.picking',
        string='Stock Picking',
        ondelete='set null',
        help='Link to stock picking that generated this analytic line',
        index=True,
    )
