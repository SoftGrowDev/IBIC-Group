from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    product_categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        related='product_id.categ_id',
        store=True,
        readonly=True,
    )

    usd_rate = fields.Float(
        string='USD Rate',
        compute='_compute_usd_fields',
        store=True,
        digits=(16, 6),
    )

    usd_amount = fields.Monetary(
        string='USD Amount',
        compute='_compute_usd_fields',
        store=True,
        currency_field='usd_currency_id',
    )

    usd_currency_id = fields.Many2one(
        'res.currency',
        string='USD Currency',
        compute='_compute_usd_currency',
    )

    @api.depends('date')
    def _compute_usd_currency(self):
        usd = self.env.ref('base.USD', raise_if_not_found=False)

        for rec in self:
            rec.usd_currency_id = usd.id if usd else False

    @api.depends('amount', 'date', 'company_id')
    def _compute_usd_fields(self):
        usd = self.env.ref('base.USD', raise_if_not_found=False)

        for rec in self:
            rec.usd_rate = 0.0
            rec.usd_amount = 0.0

            if not usd or not rec.company_id:
                continue

            company_currency = rec.company_id.currency_id
            line_date = rec.date or fields.Date.today()

            rate = usd._get_conversion_rate(
                usd,
                company_currency,
                rec.company_id,
                line_date
            )

            rec.usd_rate = rate

            if rate:
                rec.usd_amount = rec.amount / rate
