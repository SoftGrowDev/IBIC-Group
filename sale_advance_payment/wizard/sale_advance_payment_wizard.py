from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleAdvancePaymentWizard(models.TransientModel):
    _name = 'sale.advance.payment.wizard'
    _description = 'Sale Order Advance Payment Wizard'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        required=True,
        domain=[('type', 'in', ['bank', 'cash'])],
        default=lambda self: self.env['account.journal'].search(
            [('type', '=', 'cash'), ('company_id', '=', self.env.company.id)], limit=1
        ),
    )
    amount = fields.Monetary(
        string='Advance Amount',
        required=True,
        currency_field='currency_id',
    )
    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.context_today,
    )
    memo = fields.Char(
        string='Memo / Reference',
    )

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            self.memo = self.sale_order_id.name

    def action_make_payment(self):
        """Create and post the advance payment, then link it to the sale order."""
        self.ensure_one()

        if self.amount <= 0:
            raise UserError(_('Advance payment amount must be greater than zero.'))

        order = self.sale_order_id

        # Create account.payment
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.payment_date,
            'memo': self.memo or order.name,
            'company_id': order.company_id.id,
        }

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # Link to sale order via sale.advance.payment line
        self.env['sale.advance.payment'].create({
            'sale_order_id': order.id,
            'payment_id': payment.id,
        })

        # Post a message on the sale order chatter
        order.message_post(
            body=_(
                'Advance payment of <b>%(amount)s %(currency)s</b> registered via %(journal)s on %(date)s.',
                amount=self.amount,
                currency=self.currency_id.name,
                journal=self.journal_id.name,
                date=self.payment_date,
            )
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Advance Payment Registered'),
                'message': _('Payment of %s %s has been posted successfully.') % (
                    self.amount, self.currency_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }
