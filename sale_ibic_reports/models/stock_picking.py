# -*- coding: utf-8 -*-
from odoo import api, fields, models

KG_TO_LB = 2.20462


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ── Packing Information header ───────────────────────────────────────
    sp_container_type = fields.Selection(
        [('reefer', 'Reefer'), ('non_reefer', 'Non-Reefer')],
        string='Container Type', default='non_reefer')
    sp_print_type = fields.Selection(
        [('kg', 'KG'), ('lb', 'LB')],
        string='Print Type', default='kg')
    sp_bl_number = fields.Char(string='Bill of Lading No.')

    # ── Packing lines (the main O2M) ─────────────────────────────────────
    sp_packing_line_ids = fields.One2many(
        'stock.packing.line', 'picking_id', string='Packing Lines')

    # ── Summary totals (computed) ─────────────────────────────────────────
    sp_total_qty_ton = fields.Float(
        string='Total Qty (TON)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_qty_cartons = fields.Integer(
        string='Total Qty (Cartons)', compute='_compute_sp_summary', store=True)
    sp_total_wood_pallets = fields.Integer(
        string='Total Wood Pallets', compute='_compute_sp_summary', store=True)
    sp_total_plastic_pallets = fields.Integer(
        string='Total Plastic Pallets', compute='_compute_sp_summary', store=True)
    sp_total_pallets = fields.Integer(
        string='Total Pallets', compute='_compute_sp_summary', store=True)
    sp_total_carton_weight_kg = fields.Float(
        string='Total Carton Weight (KG)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_carton_nw_kg = fields.Float(
        string='Total Carton N.W (TON)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_carton_gw_kg = fields.Float(
        string='Total Carton G.W (TON)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_nw_kg = fields.Float(
        string='Total Net Weight KG', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_gw_kg = fields.Float(
        string='Total Gross Weight KG', compute='_compute_sp_summary', store=True, digits=(16, 3))

    # ── LB versions (auto-converted) ─────────────────────────────────────
    sp_total_carton_weight_lb = fields.Float(
        string='Total Carton Weight (LB)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_carton_nw_lb = fields.Float(
        string='Total Carton N.W (LB)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_carton_gw_lb = fields.Float(
        string='Total Carton G.W (LB)', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_nw_lb = fields.Float(
        string='Total Net Weight LB', compute='_compute_sp_summary', store=True, digits=(16, 3))
    sp_total_gw_lb = fields.Float(
        string='Total Gross Weight LB', compute='_compute_sp_summary', store=True, digits=(16, 3))

    @api.depends(
        'sp_packing_line_ids.qty',
        'sp_packing_line_ids.qty_cartons',
        'sp_packing_line_ids.pallet_type',
        'sp_packing_line_ids.pallet_qty',
        'sp_packing_line_ids.carton_nw_kg',
        'sp_packing_line_ids.carton_gw_kg',
        'sp_packing_line_ids.nw_kg',
        'sp_packing_line_ids.gw_kg',
        'sp_packing_line_ids.pallet_weight',
    )
    def _compute_sp_summary(self):
        for pick in self:
            lines = pick.sp_packing_line_ids
            # Qty
            pick.sp_total_qty_ton = sum(l.qty for l in lines)
            pick.sp_total_qty_cartons = sum(l.qty_cartons for l in lines)
            # Pallets
            wood = lines.filtered(lambda l: l.pallet_type == 'wood')
            plastic = lines.filtered(lambda l: l.pallet_type == 'plastic')
            pick.sp_total_wood_pallets = sum(l.pallet_qty for l in wood)
            pick.sp_total_plastic_pallets = sum(l.pallet_qty for l in plastic)
            pick.sp_total_pallets = pick.sp_total_wood_pallets + pick.sp_total_plastic_pallets
            # Carton weights
            pick.sp_total_carton_weight_kg = sum(l.pallet_weight for l in lines)
            pick.sp_total_carton_nw_kg = sum(l.carton_nw_kg for l in lines)
            pick.sp_total_carton_gw_kg = sum(l.carton_gw_kg for l in lines)
            # Net / Gross
            pick.sp_total_nw_kg = sum(l.nw_kg for l in lines)
            pick.sp_total_gw_kg = sum(l.gw_kg for l in lines)
            # LB conversions
            pick.sp_total_carton_weight_lb = pick.sp_total_carton_weight_kg * KG_TO_LB
            pick.sp_total_carton_nw_lb = pick.sp_total_carton_nw_kg * KG_TO_LB
            pick.sp_total_carton_gw_lb = pick.sp_total_carton_gw_kg * KG_TO_LB
            pick.sp_total_nw_lb = pick.sp_total_nw_kg * KG_TO_LB
            pick.sp_total_gw_lb = pick.sp_total_gw_kg * KG_TO_LB

    # ── Helper: auto-populate packing lines from move lines ─────────────
    def action_populate_packing_lines(self):
        """Populate packing lines from stock moves (one line per move)."""
        for pick in self:
            existing_moves = pick.sp_packing_line_ids.mapped('move_id')
            for move in pick.move_ids.filtered(lambda m: m.state != 'cancel'):
                if move not in existing_moves:
                    pick.sp_packing_line_ids.create({
                        'picking_id': pick.id,
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'uom_id': move.product_uom.id,
                        'qty': move.product_qty,
                    })

    # ── Helper used in report ─────────────────────────────────────────────
    def _int_to_words(self, number, suffix=''):
        try:
            from num2words import num2words
            return num2words(int(number), lang='en').title() + (' ' + suffix if suffix else '')
        except Exception:
            return f"{int(number):,}" + (' ' + suffix if suffix else '')
