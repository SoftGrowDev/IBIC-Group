from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    document_ids = fields.One2many(
        'sale.order.document',
        'invoice_id',
        string='Documents',
    )
