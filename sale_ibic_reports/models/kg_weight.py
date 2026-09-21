# -*- coding: utf-8 -*-
from odoo import fields, models


class KgWeight(models.Model):
    """Reference table for carton weight values (KG)."""
    _name = 'kg.weight'
    _description = 'Carton Weight KG Reference'
    _order = 'value'

    name = fields.Char(string='Name', required=True)
    value = fields.Float(string='Weight (KG)', required=True)
    active = fields.Boolean(default=True)

    def name_get(self):
        return [(rec.id, f"{rec.value} KG") for rec in self]
