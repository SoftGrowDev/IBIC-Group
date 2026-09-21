# -*- coding: utf-8 -*-
import math
from odoo import api, fields, models

KG_TO_LB = 2.20462
TON_TO_KG = 1000.0


class StockPackingLine(models.Model):
    _name = 'stock.packing.line'
    _description = 'Stock Picking Packing List Line'
    _order = 'sequence, id'

    picking_id = fields.Many2one(
        'stock.picking', string='Transfer',
        required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)

    # ── Sale order link (via picking → sale) for inverse o2m ────────────
    sale_id = fields.Many2one(
        'sale.order',
        related='picking_id.sale_id',
        string='Sale Order',
        store=True,
        readonly=True,
    )

    # ── Linked move ──────────────────────────────────────────────────────
    move_id = fields.Many2one('stock.move', string='Stock Move')

    # ── Container / Product ──────────────────────────────────────────────
    container_no = fields.Char(string='Container No.')
    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one('uom.uom', string='UOM')

    # ── Quantities ───────────────────────────────────────────────────────
    sale_qty = fields.Float(
        string='Sale Qty',
        related='move_id.sale_line_id.product_uom_qty',
        store=False,
        readonly=True,
        digits=(16, 3),
        help='Quantity from the originating sale order line.',
    )

    qty = fields.Float(
        string='Qty (TON)',
        digits=(16, 3),
        compute='_compute_qty',
        store=False,
        readonly=False,
        help=(
            'If UOM is TON: same as the move quantity.\n'
            'Otherwise: move_qty × uom.relative_factor × product.weight / 1000.\n'
            'Manually editable.'
        ),
    )

    qty_cartons = fields.Integer(
        string='Cartons',
        compute='_compute_qty_cartons',
        store=False, readonly=False,
        help=(
            'If UOM is TON: qty × Cartons per TON from product (ceiling).\n'
            'Otherwise: same as qty.\n'
            'Manually editable.'
        ),
    )

    # ── Pallet ───────────────────────────────────────────────────────────
    pallet_type = fields.Selection(
        [('wood', 'Wood'), ('plastic', 'Plastic')],
        string='Pallet Type', default='wood')

    pallet_weight = fields.Float(
        string='Pallet Weight (KG)',
        compute='_compute_pallet_weight',
        store=False, readonly=False)

    pallet_qty = fields.Integer(
        string='Pallet Qty',
        compute='_compute_pallet_qty',
        store=False, readonly=False,
        help='qty (TON) × Default Pallet Qty / TON from product. Rounded up. Manually editable.',
    )

    # ── Carton weights ───────────────────────────────────────────────────
    carton_nw_kg = fields.Float(
        string='Carton N.W (TON)',
        compute='_compute_carton_nw_kg',
        store=False, readonly=False,
        digits=(16, 3),
        help='Net weight in TON = qty (TON). Manually editable.',
    )

    carton_gw_kg = fields.Float(
        string='Carton G.W (TON)',
        compute='_compute_carton_gw_kg',
        store=False, readonly=False,
        digits=(16, 3),
        help='Gross weight in TON = qty + (pallet_qty × pallet_weight / 1000). Manually editable.',
    )

    # ── Totals KG ────────────────────────────────────────────────────────
    nw_kg = fields.Float(
        string='NW KG',
        compute='_compute_nw_kg',
        store=False, digits=(16, 3),
        help='qty × 1000 (TON → KG conversion).',
    )

    gw_kg = fields.Float(
        string='GW KG',
        compute='_compute_gw_kg',
        store=False, digits=(16, 3),
        help='Carton N.W (KG) + Carton G.W (KG) + NW KG',
    )

    # ─────────────────────────────────────────────────────────────────────
    # COMPUTES
    # ─────────────────────────────────────────────────────────────────────

    def _is_ton_uom(self):
        """True when this line's UOM is a TON (category Weight, name contains 'ton')."""
        uom = self.uom_id
        if not uom:
            return False
        return 'ton' in uom.name.lower()

    @api.depends('move_id', 'move_id.product_qty', 'move_id.product_uom', 'product_id.weight')
    def _compute_qty(self):
        """
        If the move's UOM is TON → qty = move quantity (already in tons).
        Otherwise            → qty = move_qty × uom.relative_factor × product.weight / 1000
                               (converts to tonnes via UOM reference factor and product weight in KG).
        Manually editable after initial computation.
        """
        for line in self:
            if not line.move_id:
                if not line.qty:
                    line.qty = 0.0
                continue
            uom = line.move_id.product_uom
            move_qty = line.move_id.product_qty
            is_ton = bool(
                uom and
                'ton' in uom.name.lower()
            )
            if is_ton:
                line.qty = move_qty
            else:
                weight = line.product_id.weight or 0.0
                factor = uom.relative_factor if uom else 1.0
                line.qty = move_qty * factor * weight / 1000.0


    @api.depends('qty', 'uom_id', 'product_id.product_tmpl_id.pkg_cartons_per_ton')
    def _compute_qty_cartons(self):
        """
        If UOM is TON: qty × Cartons per TON (ceiling).
        Otherwise   : qty (same value, no conversion).
        """
        for line in self:
            cpt = line.product_id.product_tmpl_id.pkg_cartons_per_ton
            if line._is_ton_uom() and cpt:
                line.qty_cartons = math.ceil(line.qty * cpt)
            else:
                line.qty_cartons = int(math.ceil(line.sale_qty)) if line.sale_qty else 0

    @api.depends('qty', 'product_id.product_tmpl_id.pkg_default_pallet_qty_per_ton')
    def _compute_pallet_qty(self):
        """qty (TON) × Default Pallet Qty / TON, ceiling."""
        for line in self:
            dpqt = line.product_id.product_tmpl_id.pkg_default_pallet_qty_per_ton
            if dpqt and line.qty:
                line.pallet_qty = math.ceil(line.qty * dpqt)
            else:
                line.pallet_qty = 0

    @api.depends('pallet_type',
                 'product_id.product_tmpl_id.pkg_wood_pallet_weight',
                 'product_id.product_tmpl_id.pkg_plastic_pallet_weight')
    def _compute_pallet_weight(self):
        for line in self:
            tmpl = line.product_id.product_tmpl_id
            if line.pallet_type == 'wood':
                val = tmpl.pkg_wood_pallet_weight or '20'
            else:
                val = tmpl.pkg_plastic_pallet_weight or '15'
            try:
                line.pallet_weight = float(val)
            except (TypeError, ValueError):
                line.pallet_weight = 0.0

    @api.depends('qty')
    def _compute_carton_nw_kg(self):
        """Carton N.W (TON) = qty (already in TON)."""
        for line in self:
            line.carton_nw_kg = line.qty

    @api.depends('qty', 'pallet_qty', 'pallet_weight',
                 'qty_cartons', 'product_id.product_tmpl_id.pkg_carton_weight_kg_id.value')
    def _compute_carton_gw_kg(self):
        """
        Carton G.W (TON) = qty
                         + (pallet_qty × pallet_weight_kg / 1000)
                         + (qty_cartons × carton_weight_kg / 1000)
        All addends converted to TON (pallet/carton weights come in KG).
        """
        for line in self:
            carton_w = line.product_id.product_tmpl_id.pkg_carton_weight_kg_id.value or 0.0
            line.carton_gw_kg = (
                line.qty
                + (line.pallet_qty * line.pallet_weight / TON_TO_KG)
                + (line.qty_cartons * carton_w / TON_TO_KG)
            )

    @api.depends('carton_nw_kg')
    def _compute_nw_kg(self):
        """NW KG = Carton N.W (TON) × 1000"""
        for line in self:
            line.nw_kg = line.carton_nw_kg * TON_TO_KG

    @api.depends('carton_gw_kg')
    def _compute_gw_kg(self):
        """GW KG = Carton G.W (TON) × 1000"""
        for line in self:
            line.gw_kg = line.carton_gw_kg * TON_TO_KG

    # ── On-change helpers ────────────────────────────────────────────────
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.onchange('move_id')
    def _onchange_move_id(self):
        if self.move_id:
            self.product_id = self.move_id.product_id
            self.uom_id = self.move_id.product_uom
            # qty is now auto-computed via _compute_qty
