# -*- coding: utf-8 -*-
from odoo import api, fields, models

# 1 metric ton = 1000 kg × 2.20462 lb/kg
LB_PER_TON = 2204.62


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Container and Origin for packing list
    sol_container_no = fields.Char(string='Container No.')
    sol_origin_country_id = fields.Many2one('res.country', string='Origin Country')
    
    # Unit weight for packing calculations
    sol_unit_weight_kg = fields.Float(string='Unit Weight (kg)', default=10.0)
    sol_tare_per_unit = fields.Float(string='Tare per Unit (kg)', default=0.525)
    
    # Computed weights
    sol_total_net_weight = fields.Float(
        string='Total Net Weight (kg)',
        compute='_compute_weights', store=True)
    sol_total_gross_weight = fields.Float(
        string='Total Gross Weight (kg)',
        compute='_compute_weights', store=True)

    @api.depends('product_uom_qty', 'sol_unit_weight_kg', 'sol_tare_per_unit')
    def _compute_weights(self):
        for line in self:
            if line.display_type:
                line.sol_total_net_weight = 0
                line.sol_total_gross_weight = 0
            else:
                # If unit weight is provided, use it
                if line.sol_unit_weight_kg > 0:
                    line.sol_total_net_weight = line.product_uom_qty * line.sol_unit_weight_kg
                    line.sol_total_gross_weight = line.sol_total_net_weight + (line.product_uom_qty * line.sol_tare_per_unit)
                else:
                    # Fallback to product weight if available
                    line.sol_total_net_weight = line.product_uom_qty * (line.product_id.weight or 10.0)
                    line.sol_total_gross_weight = line.sol_total_net_weight + (line.product_uom_qty * line.sol_tare_per_unit)

    def _prepare_invoice_line(self, **optional_values):
        """Override to copy container and origin to invoice line"""
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'invl_container_no': self.sol_container_no,
            'invl_origin_country_id': self.sol_origin_country_id.id,
            'invl_unit_weight_kg': self.sol_unit_weight_kg,
            'invl_tare_per_unit': self.sol_tare_per_unit,
        })
        return res

    # ── Proforma invoice display cells (driven by UOM kind) ──────────────
    def _ibic_proforma_row(self):
        """
        Return the formatted cell values for one proforma table row,
        switching behaviour on the sale line's UOM kind
        (uom.uom.ibic_uom_kind = carton / ton / lb).

        Empty string means the cell is blank; '---' means not applicable.
        Prices are pre-formatted with a '$' prefix; quantities are plain.
        """
        self.ensure_one()
        kind = self.product_uom_id.ibic_uom_kind or 'other'
        tmpl = self.product_id.product_tmpl_id
        cpt = tmpl.pkg_cartons_per_ton or 0     # Cartons per TON
        pu = self.price_unit or 0.0
        qty = self.product_uom_qty or 0.0
        total = self.price_subtotal or 0.0

        def money(v, d=3):
            return '$ {:,.{}f}'.format(v or 0.0, d)

        def num(v, d=3):
            return '{:,.{}f}'.format(v or 0.0, d)

        def count(v):
            # Carton count: no thousands separator (e.g. 1379, not 1,379)
            return '{:.0f}'.format(v or 0.0)

        row = {
            'kind': kind,
            'ton_price': '',
            'carton_price': '',
            'net_weight_ton': '',
            'total_cartons': '',
            'lb_price': '',
            'lb_qty': '',
            'total': money(total, 2),
        }

        if kind == 'carton':
            # Sold per carton: carton price = unit price, cartons = qty.
            # Ton price / net-weight-per-ton not applicable.
            row['ton_price'] = '---'
            row['net_weight_ton'] = '---'
            row['carton_price'] = money(pu, 3)
            row['total_cartons'] = count(qty)

        elif kind == 'ton':
            # Sold per ton: ton price = unit price, net weight/ton = qty.
            # Cartons + carton price derived via Cartons-per-TON on product.
            row['ton_price'] = money(pu, 3)
            row['net_weight_ton'] = num(qty, 3)
            row['total_cartons'] = count(qty * cpt) if cpt else ''
            row['carton_price'] = money(pu / cpt, 3) if cpt else ''

        elif kind == 'lb':
            # Sold per lb: lb price = unit price, lb qty = qty.
            # Ton price and net weight/ton converted from lb.
            row['lb_price'] = money(pu, 3)
            row['lb_qty'] = num(qty, 3)
            row['ton_price'] = money(pu * LB_PER_TON, 2)
            row['net_weight_ton'] = num(qty / LB_PER_TON, 3)

        else:
            # No kind set → keep the previous default behaviour.
            row['ton_price'] = money(pu, 3)
            row['carton_price'] = money(pu / cpt, 3) if cpt else ''
            row['net_weight_ton'] = num(qty, 3)
            row['total_cartons'] = count(qty * cpt) if cpt else ''

        return row
