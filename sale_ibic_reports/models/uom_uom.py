# -*- coding: utf-8 -*-
from odoo import fields, models


class UomUom(models.Model):
    _inherit = 'uom.uom'

    ibic_uom_kind = fields.Selection(
        [
            ('carton', 'Carton'),
            ('ton', 'Ton'),
            ('lb', 'LB'),
        ],
        string='Unit Kind',
        help='IBIC classification of this unit of measure. Used by the '
             'packing-list weight logic to identify TON / Carton / LB units '
             'instead of matching on the unit name.',
    )
