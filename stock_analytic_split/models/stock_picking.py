# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    analytic_distribution = fields.Json(
        string='Analytic Distribution',
        help='Default analytic distribution for all moves in this picking',
        copy=False,
    )

    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    @api.onchange('analytic_distribution')
    def _onchange_analytic_distribution(self):
        """Propagate header analytic to all move lines"""
        if self.analytic_distribution:
            for move in self.move_ids:
                # Only update if move doesn't have PO/SO line (not auto-synced)
                if not move.purchase_line_id and not self._has_sale_line(move):
                    move.analytic_distribution = self.analytic_distribution

    def _has_sale_line(self, move):
        """Check if sale_stock module is installed and move has sale_line_id"""
        return hasattr(move, 'sale_line_id') and move.sale_line_id

    def button_validate(self):
        """Override to create analytic lines on validation"""
        res = super().button_validate()
        
        # Create analytic lines for validated moves
        for picking in self:
            picking._create_analytic_lines()
        
        return res

    def _create_analytic_lines(self):
        """Create analytic lines for all done moves with analytic distribution"""
        self.ensure_one()
        
        for move in self.move_ids.filtered(lambda m: m.state == 'done' and m.analytic_distribution):
            move._create_analytic_lines_from_move()
