from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_full_feature_user = fields.Boolean(
        compute='_compute_is_full_feature_user',
        string='Is Full Feature User',
    )

    def _compute_is_full_feature_user(self):
        has_group = self.env.user.has_group(
            'sale_full_feature_group.group_sale_full_feature'
        )
        for order in self:
            order.is_full_feature_user = has_group
