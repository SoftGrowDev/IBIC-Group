# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_distribution = fields.Json(
        string='Analytic Distribution',
        copy=False,
        help='Analytic distribution for this stock move. Auto-filled from PO/SO line if linked.',
    )

    is_analytic_readonly = fields.Boolean(
        string='Analytic Readonly',
        compute='_compute_analytic_readonly',
        help='True if analytic is auto-synced from PO/SO'
    )

    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )
    @api.depends('purchase_line_id', 'sale_line_id')
    def _compute_analytic_readonly(self):
        """Make analytic readonly if linked to PO/SO"""
        for move in self:
            # Check if move is linked to purchase or sale order line
            has_po_line = bool(move.purchase_line_id)
            has_so_line = hasattr(move, 'sale_line_id') and bool(move.sale_line_id)
            move.is_analytic_readonly = has_po_line or has_so_line

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-sync analytic from PO/SO line on creation"""
        moves = super().create(vals_list)

        for move in moves:
            # Auto-sync from purchase order line
            if move.purchase_line_id and move.purchase_line_id.analytic_distribution:
                move.analytic_distribution = move.purchase_line_id.analytic_distribution

            # Auto-sync from sale order line (if sale_stock is installed)
            elif hasattr(move, 'sale_line_id') and move.sale_line_id and move.sale_line_id.analytic_distribution:
                move.analytic_distribution = move.sale_line_id.analytic_distribution

            # If no source and picking has default analytic, use it
            elif not move.analytic_distribution and move.picking_id.analytic_distribution:
                move.analytic_distribution = move.picking_id.analytic_distribution

        return moves

    def write(self, vals):
        """Update analytic from PO/SO line if those fields change"""
        res = super().write(vals)

        if 'purchase_line_id' in vals or 'sale_line_id' in vals:
            for move in self:
                # Auto-sync from purchase order line
                if move.purchase_line_id and move.purchase_line_id.analytic_distribution:
                    move.analytic_distribution = move.purchase_line_id.analytic_distribution

                # Auto-sync from sale order line
                elif hasattr(move, 'sale_line_id') and move.sale_line_id and move.sale_line_id.analytic_distribution:
                    move.analytic_distribution = move.sale_line_id.analytic_distribution

        return res

    def _create_analytic_lines_from_move(self):
        """Create analytic lines based on move's analytic distribution"""
        self.ensure_one()

        if not self.analytic_distribution:
            return

        # Get move cost (valuation)
        try:
            move_cost = self._get_move_cost()
        except Exception as e:
            # Log the error but don't block the transfer validation
            _logger.warning(
                "Could not calculate cost for stock move %s (product: %s). "
                "Analytic lines will not be created. Error: %s",
                self.id, self.product_id.name, str(e)
            )
            return

        # Skip if cost is zero or negative
        if not move_cost or move_cost <= 0:
            return

        # Create analytic lines for each distribution
        AnalyticLine = self.env['account.analytic.line']

        for analytic_account_id, percentage in self.analytic_distribution.items():
            if not percentage:
                continue

            # Calculate cost for this analytic account
            cost_amount = move_cost * (percentage / 100.0)

            # Skip if amount is zero
            if not cost_amount:
                continue

            try:
                # Prepare analytic line values
                vals = {
                    'name': _('[Stock] %s - %s') % (self.picking_id.name or '', self.product_id.display_name),
                    'account_id': int(analytic_account_id),
                    'amount': -abs(cost_amount),  # Negative for cost
                    'unit_amount': self.product_uom_qty,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_uom.id,
                    'company_id': self.company_id.id,
                    'category': 'other',
                    'stock_move_id': self.id,
                    'stock_picking_id': self.picking_id.id,
                }

                # Create the analytic line
                AnalyticLine.create(vals)
            except Exception as e:
                # Log the error but continue with other analytic accounts
                _logger.warning(
                    "Failed to create analytic line for move %s, account %s. Error: %s",
                    self.id, analytic_account_id, str(e)
                )

    def _get_move_cost(self):
        """Calculate the cost of this move from stock valuation layers"""
        self.ensure_one()

        # Try to get from stock valuation layers if available
        if hasattr(self, 'stock_valuation_layer_ids') and self.stock_valuation_layer_ids:
            return sum(self.stock_valuation_layer_ids.mapped('value'))

        # Alternative: Try to get from account moves if automated inventory valuation
        if hasattr(self, 'account_move_ids') and self.account_move_ids:
            # Get the sum of debit/credit from stock valuation account
            stock_valuation_account = self.product_id.categ_id.property_stock_valuation_account_id
            if stock_valuation_account:
                for account_move in self.account_move_ids:
                    for line in account_move.line_ids:
                        if line.account_id == stock_valuation_account:
                            # Return absolute value of the amount
                            return abs(line.debit - line.credit)

        # Fallback: Calculate from product cost and quantity
        # Use standard_price or weighted average cost
        unit_cost = self.product_id.standard_price

        # If product uses FIFO/AVCO costing, try to get the actual cost
        if self.product_id.cost_method in ('fifo', 'average'):
            # Try to get from quants
            if hasattr(self, 'quant_ids') and self.quant_ids:
                quant_cost = sum(q.cost * q.quantity for q in self.quant_ids if q.quantity > 0)
                quant_qty = sum(q.quantity for q in self.quant_ids if q.quantity > 0)
                if quant_qty > 0:
                    unit_cost = quant_cost / quant_qty

        return unit_cost * self.product_uom_qty