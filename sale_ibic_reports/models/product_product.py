# -*- coding: utf-8 -*-
from odoo import fields, models

WOOD_PALLET_WEIGHTS = [('20', '20 KG'), ('22', '22 KG'), ('24', '24 KG')]
PLASTIC_PALLET_WEIGHTS = [('15', '15 KG'), ('17', '17 KG'), ('20', '20 KG')]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ── Packaging Information tab on product template / variant ──────────
    pkg_cartons_per_ton = fields.Float(
        string='Cartons per TON')
    pkg_carton_weight_kg_id = fields.Many2one(
        'kg.weight', string='Carton Weight KG',
        help='Select the carton weight from the KG weight reference table')
    pkg_units_per_carton = fields.Integer(
        string='Units per Carton')
    pkg_wood_pallet_weight = fields.Selection(
        WOOD_PALLET_WEIGHTS, string='Wood Pallet Weight KG', default='20')
    pkg_plastic_pallet_weight = fields.Selection(
        PLASTIC_PALLET_WEIGHTS, string='Plastic Pallet Weight KG', default='15')
    pkg_default_pallet_qty_per_ton = fields.Integer(
        string='Default Pallet Qty / TON', default=1)
