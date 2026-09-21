from odoo import fields, models


class ProductType(models.Model):
    _name = 'product.type'
    _description = 'Product Nature'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)
    note = fields.Text(string='Notes')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Product Nature name must be unique.'),
    ]
