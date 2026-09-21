from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_payment_ids = fields.One2many(
        'sale.advance.payment',
        'sale_order_id',
        string='Advance Payments',
    )

    advance_payment_count = fields.Integer(
        string='Advance Payments Count',
        compute='_compute_advance_payment_count',
    )

    advance_payment_total = fields.Monetary(
        string='Total Advance Paid',
        compute='_compute_advance_payment_total',
        currency_field='currency_id',
    )

    @api.depends('advance_payment_ids.payment_id.state')
    def _compute_advance_payment_count(self):
        for order in self:
            order.advance_payment_count = len(order.advance_payment_ids)

    @api.depends('advance_payment_ids.amount', 'advance_payment_ids.payment_id.state')
    def _compute_advance_payment_total(self):
        for order in self:
            order.advance_payment_total = sum(
                p.amount for p in order.advance_payment_ids
                if p.payment_id.state == 'posted'
            )

    def action_register_advance_payment(self):
        """Open the advance payment wizard."""
        self.ensure_one()
        return {
            'name': _('Register Advance Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.advance.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_currency_id': self.currency_id.id,
                'default_amount': self.amount_total,
            },
        }

    def action_view_advance_payments(self):
        """Open advance payments list."""
        self.ensure_one()
        payment_ids = self.advance_payment_ids.mapped('payment_id').ids
        return {
            'name': _('Advance Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', payment_ids)],
            'target': 'current',
        }


class SaleAdvancePayment(models.Model):
    _name = 'sale.advance.payment'
    _description = 'Sale Order Advance Payment'
    _order = 'payment_date desc'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
    )
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='sale_order_id.partner_id',
        string='Customer',
        store=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        related='payment_id.journal_id',
        string='Journal',
        store=True,
    )
    amount = fields.Monetary(
        related='payment_id.amount',
        string='Amount',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='payment_id.currency_id',
        string='Currency',
        store=True,
    )
    payment_date = fields.Date(
        related='payment_id.date',
        string='Payment Date',
        store=True,
    )
    state = fields.Selection(
        related='payment_id.state',
        string='Status',
        store=True,
    )
    payment_reference = fields.Char(
        related='payment_id.payment_reference',
        string='Reference',
        store=True,
    )
    memo = fields.Char(
        related='payment_id.memo',
        string='Memo',
        store=True,
    )
