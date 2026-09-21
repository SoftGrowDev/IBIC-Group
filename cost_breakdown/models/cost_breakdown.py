from odoo import api, fields, models


def _get_rate_to_egp(currency, company, date=None):
    """
    Return the exchange rate: 1 unit of `currency` = X EGP.
    Uses Odoo's built-in _convert: converts 1.0 of `currency` → EGP.
    Falls back to 1.0 if EGP not found or same currency.
    """
    egp = currency.env.ref('base.EGP', raise_if_not_found=False)
    if not egp or not currency or currency == egp:
        return 1.0
    try:
        from datetime import date as date_cls
        rate_date = date or date_cls.today()
        # Convert 1 unit of currency → EGP
        result = currency._convert(1.0, egp, company, rate_date)
        return result if result else 1.0
    except Exception:
        return 1.0


def _get_expense_account(product):
    """
    Return the accounting expense account for a product, resolving the
    product's own expense account first, then falling back to its category.
    Returns an empty account.account recordset when none is configured.
    """
    empty = product.env['account.account']
    if not product:
        return empty
    try:
        account = product.property_account_expense_id
        if not account:
            account = product.categ_id.property_account_expense_categ_id
        return account or empty
    except Exception:
        return empty


class CostBreakdown(models.Model):
    _name = 'cost.breakdown'
    _description = 'Estimated Cost Breakdown'
    _order = 'id desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    customer_id = fields.Many2one(
        related='sale_order_id.partner_id',
        string='Customer',
        store=True,
    )
    product_id = fields.Many2one(
        related='sale_order_line_id.product_id',
        string='Product',
        store=True,
    )
    qty = fields.Float(
        related='sale_order_line_id.product_uom_qty',
        string='Qty',
        store=True,
    )
    uom_id = fields.Many2one(
        related='sale_order_line_id.product_uom_id',
        string='UOM',
        store=True,
    )

    # ── Sale Price (per unit, in SO currency = USD) ───────────────────────
    sale_price = fields.Float(
        related='sale_order_line_id.price_unit',
        string='Sale Price (per unit)',
        store=True,
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        string='Currency',
        store=True,
    )
    company_id = fields.Many2one(
        related='sale_order_id.company_id',
        store=True,
    )

    # ── FX rate: SO currency → EGP  (auto-filled, manually overridable) ──
    sale_fx_rate = fields.Float(
        string='Sale FX Rate (→ EGP)',
        default=1.0,
        digits=(16, 4),
        help='Rate to convert the Sale Order currency into EGP. '
             'Auto-filled from Odoo currency rates when the Sale Order is set.',
        tracking=True,
    )

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed')],
        default='draft',
        tracking=True,
    )
    line_ids = fields.One2many(
        'cost.breakdown.line',
        'breakdown_id',
        string='Components',
    )

    # ── Totals (computed) ─────────────────────────────────────────────────
    total_cost_usd = fields.Float(
        string='Total Cost (USD)',
        compute='_compute_totals',
        store=True,
        digits='Product Price',
    )
    total_cost_egp = fields.Float(
        string='Total Cost (EGP)',
        compute='_compute_totals',
        store=True,
        digits='Product Price',
    )
    sale_price_usd = fields.Float(
        string='Sale Price (USD)',
        compute='_compute_totals',
        store=True,
        digits='Product Price',
        help='sale_price per unit × qty',
    )
    sale_price_egp = fields.Float(
        string='Sale Price (EGP)',
        compute='_compute_totals',
        store=True,
        digits='Product Price',
        help='Sale Price (USD) × Sale FX Rate',
    )
    margin_usd = fields.Float(
        string='Margin (USD)',
        compute='_compute_totals',
        store=True,
        digits='Product Price',
    )
    margin_egp = fields.Float(
        string='Margin (EGP)',
        compute='_compute_totals',
        store=True,
        digits='Product Price',
    )
    margin_percent_usd = fields.Float(
        string='Margin % (USD)',
        compute='_compute_totals',
        store=True,
    )
    margin_percent_egp = fields.Float(
        string='Margin % (EGP)',
        compute='_compute_totals',
        store=True,
    )

    # Legacy aliases
    total_cost     = fields.Float(compute='_compute_totals', store=True,
                                  string='Total Cost (EGP) [legacy]')
    margin         = fields.Float(compute='_compute_totals', store=True,
                                  string='Margin (EGP) [legacy]')
    margin_percent = fields.Float(compute='_compute_totals', store=True,
                                  string='Margin % [legacy]')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('cost.breakdown') or 'New'
                )
        return super().create(vals_list)

    # ── Auto-fill sale_fx_rate when sale_order_id or currency changes ─────
    @api.onchange('sale_order_id', 'currency_id')
    @api.constrains('sale_order_id', 'currency_id')
    def _onchange_sale_order_fill_fx(self):
        for rec in self:
            if rec.currency_id and rec.company_id:
                rec.sale_fx_rate = _get_rate_to_egp(
                    rec.currency_id, rec.company_id)

    @api.depends(
        'line_ids.total_usd',
        'line_ids.total_egp',
        'sale_price', 'qty', 'sale_fx_rate',
    )
    def _compute_totals(self):
        for rec in self:
            fx = rec.sale_fx_rate or 1.0

            # Cost — each line already carries correct USD & EGP totals
            cost_usd = sum(rec.line_ids.mapped('total_usd'))
            cost_egp = sum(rec.line_ids.mapped('total_egp'))
            rec.total_cost_usd = cost_usd
            rec.total_cost_egp = cost_egp
            rec.total_cost     = cost_egp

            # Revenue
            rev_usd = rec.sale_price * rec.qty
            rev_egp = rev_usd * fx
            rec.sale_price_usd = rev_usd
            rec.sale_price_egp = rev_egp

            # Margin — same currency vs same currency, never mixed
            m_usd = rev_usd - cost_usd
            m_egp = rev_egp - cost_egp
            rec.margin_usd = m_usd
            rec.margin_egp = m_egp
            rec.margin     = m_egp

            rec.margin_percent_usd = (m_usd / rev_usd) if rev_usd else 0.0
            rec.margin_percent_egp = (m_egp / rev_egp) if rev_egp else 0.0
            rec.margin_percent     = rec.margin_percent_egp

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.depends('name', 'product_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.name} – {rec.product_id.display_name or ''}"
            )


class CostBreakdownLine(models.Model):
    _name = 'cost.breakdown.line'
    _description = 'Estimated Cost Breakdown Line'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    breakdown_id = fields.Many2one(
        'cost.breakdown',
        string='Estimated Cost Breakdown',
        required=True,
        ondelete='cascade',
    )

    type_id = fields.Many2one('product.type', string='Product Nature')

    product_id = fields.Many2one(
        'product.product',
        string='Component',
        required=True,
    )
    uom_id = fields.Many2one('uom.uom', string='UOM')
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        help='Accounting account for this component. '
             'Auto-filled from the product/category expense account; editable.',
    )

    bom_qty = fields.Float(
        string='BOM Qty (per unit)',
        digits=(16, 4),
        help='Quantity from BOM per one finished product unit.',
    )
    qty = fields.Float(
        string='Total Qty',
        digits=(16, 4),
        help='bom_qty × SO qty. Editable.',
    )

    # ── Currency & FX ─────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('base.USD', raise_if_not_found=False),
    )
    fx_rate = fields.Float(
        string='FX Rate (→ EGP)',
        default=1.0,
        digits=(16, 4),
        help='Auto-filled from Odoo currency rates (this currency → EGP). '
             'Editable for manual override.',
    )

    unit_cost = fields.Float(
        string='Unit Cost',
        digits='Product Price',
        help='Cost per 1 unit of this component, in the line currency.',
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True,
        digits='Product Price',
        help='qty × unit_cost in line currency.',
    )
    total_usd = fields.Float(
        string='Total (USD)',
        compute='_compute_total',
        store=True,
        digits='Product Price',
    )
    total_egp = fields.Float(
        string='Total (EGP)',
        compute='_compute_total',
        store=True,
        digits='Product Price',
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain=[('supplier_rank', '>', 0)],
    )
    source = fields.Selection(
        [('vendor_pricelist', 'Vendor Pricelist'), ('manual', 'Manual')],
        string='Source',
        default='manual',
    )
    note = fields.Char(string='Note')

    @api.depends('qty', 'unit_cost', 'fx_rate', 'currency_id')
    def _compute_total(self):
        usd_ref = self.env.ref('base.USD', raise_if_not_found=False)
        egp_ref = self.env.ref('base.EGP', raise_if_not_found=False)

        for line in self:
            fx = line.fx_rate or 1.0
            raw = line.qty * line.unit_cost
            line.total = raw
            cur = line.currency_id

            if cur and usd_ref and cur == usd_ref:
                # USD line → EGP = raw × fx_rate,  USD = raw
                line.total_egp = raw * fx
                line.total_usd = raw
            elif cur and egp_ref and cur == egp_ref:
                # EGP line → EGP = raw,  USD = raw ÷ fx_rate
                line.total_egp = raw
                line.total_usd = (raw / fx) if fx else 0.0
            else:
                # Other currency: fx_rate means "1 of this → EGP"
                line.total_egp = raw * fx
                # USD = EGP ÷ rate-of-USD-to-EGP; we don't have that here
                # so we use the same fx as approximation
                line.total_usd = (line.total_egp / fx) if fx else 0.0

    # ── Auto-fill fx_rate from Odoo currency rates ────────────────────────
    @api.onchange('currency_id')
    @api.constrains('currency_id')
    def _onchange_currency_id_fill_fx(self):
        for line in self:
            if line.currency_id and line.breakdown_id.company_id:
                line.fx_rate = _get_rate_to_egp(
                    line.currency_id, line.breakdown_id.company_id)
            elif line.currency_id:
                # fallback: use env.company
                line.fx_rate = _get_rate_to_egp(
                    line.currency_id, line.env.company)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        product = self.product_id
        tmpl = product.product_tmpl_id
        self.uom_id = product.uom_id
        self.type_id = tmpl.product_type_id or False
        self.account_id = _get_expense_account(product)
        # Default: product cost
        self.unit_cost = product.standard_price
        self.source = 'manual'
        # Try to find best supplier from supplier info
        supplier_info = product.seller_ids[:1]  # first supplier line
        if supplier_info:
            self.vendor_id = supplier_info.partner_id
            self.source = 'vendor_pricelist'
            if supplier_info.currency_id:
                self.currency_id = supplier_info.currency_id
                self.fx_rate = _get_rate_to_egp(
                    supplier_info.currency_id,
                    self.breakdown_id.company_id or self.env.company,
                )
            self.unit_cost = supplier_info.price or product.standard_price

    def _get_supplier_info(self, product, vendor):
        """
        Return the best matching product.supplierinfo record for the given
        product + vendor combination.
        Matches on partner, then picks the line with the lowest min_qty
        that still applies (standard Odoo vendor pricelist logic).
        Falls back to the first line for that vendor regardless of min_qty.
        """
        if not product or not vendor:
            return self.env['product.supplierinfo']
        domain = [
            ('partner_id', '=', vendor.id),
            '|',
            ('product_id', '=', product.id),
            '&',
            ('product_id', '=', False),
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
        ]
        return self.env['product.supplierinfo'].search(
            domain, order='min_qty asc', limit=1
        )

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        """When vendor changes, update unit_cost and currency from supplier info."""
        for line in self:
            if not line.vendor_id or not line.product_id:
                continue
            supplier = line._get_supplier_info(line.product_id, line.vendor_id)
            if supplier:
                line.source = 'vendor_pricelist'
                line.unit_cost = supplier.price or line.product_id.standard_price
                if supplier.currency_id:
                    line.currency_id = supplier.currency_id
                    line.fx_rate = _get_rate_to_egp(
                        supplier.currency_id,
                        line.breakdown_id.company_id or line.env.company,
                    )
            else:
                # vendor exists but no pricelist line → fall back to product cost
                line.source = 'manual'
                line.unit_cost = line.product_id.standard_price
