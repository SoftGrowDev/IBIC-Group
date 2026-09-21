# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Container and Origin for packing list
    invl_container_no = fields.Char(string='Container No.')
    invl_origin_country_id = fields.Many2one('res.country', string='Origin Country')
    
    # Unit weight for packing calculations
    invl_unit_weight_kg = fields.Float(string='Unit Weight (kg)', default=10.0)
    invl_tare_per_unit = fields.Float(string='Tare per Unit (kg)', default=0.525)
    
    # Computed weights
    invl_total_net_weight = fields.Float(
        string='Total Net Weight (kg)',
        compute='_compute_weights', store=True)
    invl_total_gross_weight = fields.Float(
        string='Total Gross Weight (kg)',
        compute='_compute_weights', store=True)

    @api.depends('quantity', 'invl_unit_weight_kg', 'invl_tare_per_unit')
    def _compute_weights(self):
        for line in self:
            if line.display_type:
                line.invl_total_net_weight = 0
                line.invl_total_gross_weight = 0
            else:
                # If unit weight is provided, use it
                if line.invl_unit_weight_kg > 0:
                    line.invl_total_net_weight = line.quantity * line.invl_unit_weight_kg
                    line.invl_total_gross_weight = line.invl_total_net_weight + (line.quantity * line.invl_tare_per_unit)
                else:
                    # Fallback to product weight if available
                    line.invl_total_net_weight = line.quantity * (line.product_id.weight or 10.0)
                    line.invl_total_gross_weight = line.invl_total_net_weight + (line.quantity * line.invl_tare_per_unit)
