from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_type_id = fields.Many2one(
        'product.type',
        string='Product Nature',
        help='Cost breakdown nature used when this product appears as a component.',
    )
