from odoo import models, fields


class SaleDocumentName(models.Model):
    """
        Initialize Sale Document Name:
         -
    """
    _name = 'sale.document.name'
    _description = 'Sale Document Name'

    name = fields.Char(
        required=True,
        translate=True,
    )


class SaleOrderDocument(models.Model):
    _name = 'sale.order.document'
    _description = 'Sale Order Document'
    _rec_name = 'name_id'

    name = fields.Char(required=True)

    attachment_id = fields.Binary(
        string='Attachment',
        required=True,
    )
    name_id = fields.Many2one(
        'sale.document.name'
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        ondelete='cascade',
    )

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        ondelete='cascade',
    )
