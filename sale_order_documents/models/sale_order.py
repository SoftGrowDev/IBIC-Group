from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    document_ids = fields.One2many(
        'sale.order.document',
        'sale_order_id',
        string='Documents'
    )

    def _create_invoices(self, grouped=False, final=False, date=None):

        invoices = super()._create_invoices(
            grouped=grouped,
            final=final,
            date=date,
        )
        for order in self:
            related_invoices = invoices.filtered(
                lambda inv: order.name in (inv.invoice_origin or '')
            )

            for invoice in related_invoices:

                for doc in order.document_ids:

                    self.env['sale.order.document'].create({
                        'name': doc.name,
                        'attachment_id': doc.attachment_id,
                        'sale_order_id': order.id,
                        'invoice_id': invoice.id,
                    })

        return invoices