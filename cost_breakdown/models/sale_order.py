from odoo import api, fields, models
from odoo.exceptions import UserError

from .cost_breakdown import _get_expense_account


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cost_breakdown_count = fields.Integer(
        string='Estimated Cost Breakdowns',
        compute='_compute_cost_breakdown_count',
    )

    @api.depends('order_line')
    def _compute_cost_breakdown_count(self):
        for order in self:
            order.cost_breakdown_count = self.env['cost.breakdown'].search_count(
                [('sale_order_id', '=', order.id)]
            )

    def action_view_cost_breakdowns(self):
        """Smart button – always opens as list view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Estimated Cost Breakdown – {self.name}',
            'res_model': 'cost.breakdown',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }

    def action_create_cost_breakdown(self):
        """
        Create one Estimated Cost Breakdown per sale order line.
        BOM qty is scaled by the SO line qty.
        Skips lines that already have a breakdown.
        """
        self.ensure_one()
        if not self.order_line:
            raise UserError("There are no order lines to generate cost breakdowns for.")

        CostBreakdown = self.env['cost.breakdown']
        created = self.env['cost.breakdown']

        for line in self.order_line:
            if not line.product_id:
                continue
            if CostBreakdown.search([('sale_order_line_id', '=', line.id)], limit=1):
                continue

            breakdown_lines = self._get_breakdown_lines(line)
            breakdown = CostBreakdown.create({
                'sale_order_id': self.id,
                'sale_order_line_id': line.id,
                'line_ids': [(0, 0, v) for v in breakdown_lines],
            })
            created |= breakdown

        if not created:
            raise UserError(
                "Estimated Cost Breakdowns already exist for all order lines.\n"
                "Open the existing records to update them."
            )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Estimated Cost Breakdowns',
            'res_model': 'cost.breakdown',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_bom(self, product):
        return self.env['mrp.bom'].search([
            '|',
            ('product_id', '=', product.id),
            '&',
            ('product_id', '=', False),
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('type', '=', 'normal'),
            '|',
            ('company_id', '=', self.company_id.id),
            ('company_id', '=', False),
        ], limit=1)

    def _get_breakdown_lines(self, sol):
        """
        Return list of cost.breakdown.line vals.
        When a BOM exists:
          - bom_qty  = BOM line qty  (qty per finished unit in BOM)
          - qty      = bom_qty × SO line qty  (total needed for this order)
          - unit_cost is per 1 component unit (not scaled)
        Falls back to the product itself when no BOM.
        """
        lines = []
        so_qty = sol.product_uom_qty or 1.0
        bom = self._find_bom(sol.product_id)

        if bom:
            # BOM may have its own qty (bom.product_qty) — scale proportionally
            bom_base_qty = bom.product_qty or 1.0
            for bom_line in bom.bom_line_ids:
                component = bom_line.product_id
                # qty per finished unit (normalised to BOM base qty = 1)
                bom_qty_per_unit = bom_line.product_qty / bom_base_qty
                total_qty = bom_qty_per_unit * so_qty
                lines.append(self._build_line_vals(
                    product=component,
                    uom_id=bom_line.product_uom_id.id,
                    bom_qty=bom_qty_per_unit,
                    qty=total_qty,
                ))
        else:
            lines.append(self._build_line_vals(
                product=sol.product_id,
                uom_id=sol.product_id.uom_id.id,
                bom_qty=1.0,
                qty=so_qty,
            ))

        return lines

    def _build_line_vals(self, product, uom_id, bom_qty, qty):
        supplier = product.seller_ids[:1]
        type_id = (
            product.product_tmpl_id.product_type_id.id
            if product.product_tmpl_id.product_type_id else False
        )

        # unit_cost is always per 1 unit of the component
        unit_cost = product.standard_price
        source = 'manual'
        vendor_id = False
        currency_id = False

        if supplier:
            vendor_id = supplier.partner_id.id
            source = 'vendor_pricelist'
            currency_id = supplier.currency_id.id if supplier.currency_id else False
            unit_cost = supplier.price or product.standard_price

        return {
            'product_id': product.id,
            'uom_id': uom_id,
            'account_id': _get_expense_account(product).id or False,
            'bom_qty': bom_qty,
            'qty': qty,
            'unit_cost': unit_cost,
            'source': source,
            'type_id': type_id,
            'vendor_id': vendor_id,
            'currency_id': currency_id or self.env.ref(
                'base.USD', raise_if_not_found=False
            ).id,
        }
