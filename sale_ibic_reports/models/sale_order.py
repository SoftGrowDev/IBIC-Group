# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ── Shipping / Transport ─────────────────────────────────────────────
    so_country_of_origin_id = fields.Many2one(
        'res.country', string='Country of Origin')
    so_board_date    = fields.Date(string='Boarding Date')
    so_carriage_by   = fields.Many2one(
        'res.partner',
        string='Carriage By')
    so_port_of_loading   = fields.Many2one(
        'freight.port',
        string='Port of Loading')
    so_port_of_discharge = fields.Many2one(
        'freight.port',
        string='Port of Discharge')
    so_waybill_no        = fields.Char(string='Waybill No.')
    so_container_lta     = fields.Char(string='Container / LTA')
    so_place_of_delivery = fields.Char(string='Place of Delivery')
    so_incoterm_id = fields.Many2one('account.incoterms', string='Inco Terms')

    # ── Packing List ─────────────────────────────────────────────────────
    so_bl_number = fields.Char(string='Bill of Lading No.')
    so_packing_line_ids = fields.One2many(
        'sale.packing.line', 'order_id', string='Packing Lines')

    # ── Delivery packing lines (from linked stock.picking → packing lines) ─
    so_delivery_packing_line_ids = fields.One2many(
        'stock.packing.line', 'sale_id',
        string='Delivery Packing Lines',
        readonly=True,
    )

    # ── Packing totals (computed) ─────────────────────────────────────────
    so_total_cartons = fields.Integer(
        string='Total Cartons',
        compute='_compute_packing_totals', store=True)
    so_total_net_weight = fields.Float(
        string='Total Net Weight (kg)',
        compute='_compute_packing_totals', store=True)
    so_total_gross_weight = fields.Float(
        string='Total Gross Weight (kg)',
        compute='_compute_packing_totals', store=True)

    @api.depends('so_packing_line_ids.qty_cartons',
                 'so_packing_line_ids.total_net_weight',
                 'so_packing_line_ids.total_gross_weight')
    def _compute_packing_totals(self):
        for o in self:
            o.so_total_cartons      = sum(l.qty_cartons        for l in o.so_packing_line_ids)
            o.so_total_net_weight   = sum(l.total_net_weight   for l in o.so_packing_line_ids)
            o.so_total_gross_weight = sum(l.total_gross_weight for l in o.so_packing_line_ids)

    # ── Invoice / Payment notes ──────────────────────────────────────────
    so_payment_note = fields.Text(
        string='Payment Term Note',
        default='30% advance payment, and 50% after shipping against '
                'documents and 20% after arrival and quality approval')
    so_conditions = fields.Char(
        string='Conditions',
        default='This invoice is valid for 7 days from invoice date')
    so_terms = fields.Text(string='Terms & Conditions')

    # ── Bank details (copied from company on create, editable per SO) ────
    so_bank_name        = fields.Char(
        related="company_id.ibic_bank_name",
        string='Bank Name')
    so_bank_branch      = fields.Char(
        related="company_id.ibic_bank_branch",
        string='Bank Branch / Currency')
    so_bank_beneficiary = fields.Char(
        related="company_id.ibic_bank_beneficiary",
        string='Beneficiary')
    so_bank_account     = fields.Char(
        related="company_id.ibic_bank_account",
        string='Account Number')
    so_bank_iban        = fields.Char(
        related="company_id.ibic_bank_iban",
        string='IBAN')
    so_bank_swift       = fields.Char(
        related="company_id.ibic_bank_swift",
        string='SWIFT Code')
    so_bank_tel         = fields.Char(
        related="company_id.ibic_bank_tel",
        string='Bank Tel')
    so_bank_fax         = fields.Char(
        related="company_id.ibic_bank_fax",
        string='Bank Fax')
    so_bank_address     = fields.Char(
        related="company_id.ibic_bank_address",
        string='Bank Address')

    # ── Amount in words (computed) ────────────────────────────────────────
    so_amount_in_words = fields.Char(
        string='Amount In Words',
        compute='_compute_amount_in_words',
        store=True)

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_in_words(self):
        for o in self:
            try:
                from num2words import num2words
                whole = int(o.amount_total)
                words = num2words(whole, lang='en').title()
                o.so_amount_in_words = f"{words} {o.currency_id.name or 'Dollars'}"
            except Exception:
                o.so_amount_in_words = f"{o.amount_total:,.2f} {o.currency_id.name or ''}"

    # ── Auto-fill bank from company on create ────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id') or self.env.company.id
            company = self.env['res.company'].browse(company_id)
            # Only fill if not explicitly provided
            for field, company_field in [
                ('so_bank_name',        'ibic_bank_name'),
                ('so_bank_branch',      'ibic_bank_branch'),
                ('so_bank_beneficiary', 'ibic_bank_beneficiary'),
                ('so_bank_account',     'ibic_bank_account'),
                ('so_bank_iban',        'ibic_bank_iban'),
                ('so_bank_swift',       'ibic_bank_swift'),
                ('so_bank_tel',         'ibic_bank_tel'),
                ('so_bank_fax',         'ibic_bank_fax'),
                ('so_bank_address',     'ibic_bank_address'),
            ]:
                if not vals.get(field):
                    company_val = getattr(company, company_field, False)
                    if company_val:
                        vals[field] = company_val
        return super().create(vals_list)

    def action_fill_bank_from_company(self):
        """Button to reset bank details from company defaults."""
        for o in self:
            company = o.company_id
            o.write({
                'so_bank_name':        company.ibic_bank_name or '',
                'so_bank_branch':      company.ibic_bank_branch or '',
                'so_bank_beneficiary': company.ibic_bank_beneficiary or '',
                'so_bank_account':     company.ibic_bank_account or '',
                'so_bank_iban':        company.ibic_bank_iban or '',
                'so_bank_swift':       company.ibic_bank_swift or '',
                'so_bank_tel':         company.ibic_bank_tel or '',
                'so_bank_fax':         company.ibic_bank_fax or '',
                'so_bank_address':     company.ibic_bank_address or '',
            })

    # ── Bank account selector (pre-fills bank detail fields) ─────────────
    so_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        help='Select a company bank account to pre-fill the bank details below.',
    )

    @api.onchange('so_bank_id')
    def _onchange_so_bank_id(self):
        b = self.so_bank_id
        if b:
            self.so_bank_name        = b.bank_id.name or ''
            self.so_bank_branch      = b.bank_id.street or ''
            self.so_bank_beneficiary = b.partner_id.name or ''
            self.so_bank_account     = b.acc_number or ''
            self.so_bank_iban        = b.acc_number or ''
            self.so_bank_swift       = b.bank_id.bic or ''

    # ── Signature / Stamp images ─────────────────────────────────────────
    so_shipper_stamp = fields.Binary(
        related='company_id.ibic_shipper_stamp',
        string='Shipper Stamp & Signature',
        readonly=True,
        help='Taken from the company record. Edit it there to change.',
    )

    # ── Proforma table layout: LB mode hides carton columns ──────────────
    def _ibic_proforma_lb_mode(self):
        """
        True when every product line on the order is sold in an LB-kind UOM.
        In that case the proforma table swaps the Carton columns for
        LB Price / LB Quantity columns.
        """
        self.ensure_one()
        prod_lines = self.order_line.filtered(
            lambda l: not l.display_type and l.product_id)
        return bool(prod_lines) and all(
            l.product_uom_id.ibic_uom_kind == 'lb' for l in prod_lines
        )

    # ── Helper used in Packing List template ─────────────────────────────
    def _int_to_words(self, number, suffix=''):
        try:
            from num2words import num2words
            return num2words(int(number), lang='en').title() + (' ' + suffix if suffix else '')
        except Exception:
            return f"{int(number):,}" + (' ' + suffix if suffix else '')

    # ── Freight Booking link ──────────────────────────────────────────────
    booking_id = fields.Many2one(
        'shipment.freight.booking',
        string='Freight Booking',
        copy=False,
        tracking=True,
    )

    def action_create_freight_booking(self):
        """Create a new freight booking from the shipping info page,
        pre-filling shipper = company partner, consignee = SO customer."""
        self.ensure_one()
        booking = self.env['shipment.freight.booking'].create({
            'shipper_id':   self.company_id.partner_id.id,
            'consignee_id': self.partner_id.id,
            'sale_id':      self.id,
        })
        self.booking_id = booking.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Freight Booking',
            'res_model': 'shipment.freight.booking',
            'res_id': booking.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_freight_booking(self):
        """Open the linked freight booking."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Freight Booking',
            'res_model': 'shipment.freight.booking',
            'res_id': self.booking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
