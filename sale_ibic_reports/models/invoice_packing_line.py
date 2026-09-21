# -*- coding: utf-8 -*-
from odoo import api, fields, models


class InvoicePackingLine(models.Model):
    _name = 'invoice.packing.line'
    _description = 'Invoice Packing List Line'
    _order = 'sequence, id'

    move_id = fields.Many2one(
        'account.move', string='Invoice',
        required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)

    # Container
    container_no = fields.Char(string='Container No.')

    # Product / Item
    product_id = fields.Many2one('product.product', string='Product')
    item_description = fields.Char(string='Item Description')
    origin_country_id = fields.Many2one('res.country', string='Origin')

    # Quantity: e.g. 2500 cartons × 10 kg each
    qty_cartons = fields.Integer(string='Qty (Cartons)', default=1)
    unit_weight_kg = fields.Float(string='Unit Weight (kg)', default=10.0)

    # Weights (computed)
    total_net_weight = fields.Float(
        string='Total Net Weight (kg)',
        compute='_compute_weights', store=True)
    tare_per_carton = fields.Float(
        string='Tare / Carton (kg)', default=0.525,
        help='Extra weight per carton for gross calculation')
    total_gross_weight = fields.Float(
        string='Total Gross Weight (kg)',
        compute='_compute_weights', store=True)

    @api.depends('qty_cartons', 'unit_weight_kg', 'tare_per_carton')
    def _compute_weights(self):
        for line in self:
            line.total_net_weight = line.qty_cartons * line.unit_weight_kg
            line.total_gross_weight = (
                line.total_net_weight + line.qty_cartons * line.tare_per_carton
            )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.item_description:
            self.item_description = self.product_id.name
