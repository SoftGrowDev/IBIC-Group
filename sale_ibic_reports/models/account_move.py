# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ── Shipping / Transport ─────────────────────────────────────────────
    inv_country_of_origin_id = fields.Many2one(
        'res.country', string='Country of Origin')
    inv_board_date    = fields.Date(string='Boarding Date')
    inv_carriage_by   = fields.Many2one(
        'res.partner',
        string='Carriage By')
    inv_port_of_loading   = fields.Many2one(
        'freight.port',
        string='Port of Loading')
    inv_port_of_discharge = fields.Many2one(
    'freight.port',
    string='Port of Discharge')
    inv_waybill_no        = fields.Char(string='Waybill No.')
    inv_container_lta     = fields.Char(string='Container / LTA')
    inv_place_of_delivery = fields.Char(string='Place of Delivery')
    inv_incoterm_id = fields.Many2one('account.incoterms', string='Inco Terms')

    # ── Packing List ─────────────────────────────────────────────────────
    inv_bl_number = fields.Char(string='Bill of Lading No.')
    inv_packing_line_ids = fields.One2many(
        'invoice.packing.line', 'move_id', string='Packing Lines')

    # ── Packing totals (computed) ─────────────────────────────────────────
    inv_total_cartons = fields.Integer(
        string='Total Cartons',
        compute='_compute_packing_totals', store=True)
    inv_total_net_weight = fields.Float(
        string='Total Net Weight (kg)',
        compute='_compute_packing_totals', store=True)
    inv_total_gross_weight = fields.Float(
        string='Total Gross Weight (kg)',
        compute='_compute_packing_totals', store=True)

    @api.depends('inv_packing_line_ids.qty_cartons',
                 'inv_packing_line_ids.total_net_weight',
                 'inv_packing_line_ids.total_gross_weight')
    def _compute_packing_totals(self):
        for inv in self:
            inv.inv_total_cartons      = sum(l.qty_cartons        for l in inv.inv_packing_line_ids)
            inv.inv_total_net_weight   = sum(l.total_net_weight   for l in inv.inv_packing_line_ids)
            inv.inv_total_gross_weight = sum(l.total_gross_weight for l in inv.inv_packing_line_ids)

    # ── Invoice / Payment notes ──────────────────────────────────────────
    inv_payment_note = fields.Text(
        string='Payment Term Note',
        default='30% advance payment, and 50% after shipping against '
                'documents and 20% after arrival and quality approval')
    inv_conditions = fields.Char(
        string='Conditions',
        default='This invoice is valid for 7 days from invoice date')
    inv_terms = fields.Text(string='Terms & Conditions')

    # ── Bank details (copied from company on create, editable per invoice) ────
    inv_bank_name        = fields.Char(string='Bank Name')
    inv_bank_branch      = fields.Char(string='Bank Branch / Currency')
    inv_bank_beneficiary = fields.Char(string='Beneficiary')
    inv_bank_account     = fields.Char(string='Account Number')
    inv_bank_iban        = fields.Char(string='IBAN')
    inv_bank_swift       = fields.Char(string='SWIFT Code')
    inv_bank_tel         = fields.Char(string='Bank Tel')
    inv_bank_fax         = fields.Char(string='Bank Fax')
    inv_bank_address     = fields.Char(string='Bank Address')

    # ── Amount in words (computed) ────────────────────────────────────────
    inv_amount_in_words = fields.Char(
        string='Amount In Words',
        compute='_compute_amount_in_words',
        store=True)

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_in_words(self):
        for inv in self:
            try:
                from num2words import num2words
                whole = int(inv.amount_total)
                words = num2words(whole, lang='en').title()
                inv.inv_amount_in_words = f"{words} {inv.currency_id.name or 'Dollars'}"
            except Exception:
                inv.inv_amount_in_words = f"{inv.amount_total:,.2f} {inv.currency_id.name or ''}"

    # ── Auto-copy from sale order when invoice is created ────────────────────────────
    def _reverse_moves(self, default_values_list=None, cancel=False):
        """Override to copy fields to credit notes"""
        reverse_moves = super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        for move, reverse_move in zip(self, reverse_moves):
            if move.move_type in ('out_invoice', 'out_refund'):
                self._copy_shipping_data(move, reverse_move)
        return reverse_moves

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            # Only for customer invoices
            if move.move_type in ('out_invoice', 'out_refund'):
                # Copy from sale order if linked
                if move.invoice_line_ids and move.invoice_line_ids[0].sale_line_ids:
                    sale_order = move.invoice_line_ids[0].sale_line_ids[0].order_id
                    self._copy_from_sale_order(move, sale_order)
                
                # Fill bank details from company if not from sale order
                if not move.inv_bank_name:
                    self._fill_bank_from_company(move)
        return moves

    def _copy_from_sale_order(self, invoice, sale_order):
        """Copy all shipping and packing data from sale order to invoice"""
        if not sale_order:
            return
        
        # Copy shipping fields
        invoice.write({
            'inv_country_of_origin_id': sale_order.so_country_of_origin_id.id,
            'inv_board_date': sale_order.so_board_date,
            'inv_carriage_by': sale_order.so_carriage_by.id,
            'inv_port_of_loading': sale_order.so_port_of_loading.id,
            'inv_port_of_discharge': sale_order.so_port_of_discharge.id,
            'inv_waybill_no': sale_order.so_waybill_no,
            'inv_container_lta': sale_order.so_container_lta,
            'inv_place_of_delivery': sale_order.so_place_of_delivery,
            'inv_incoterm_id': sale_order.so_incoterm_id.id,
            'inv_bl_number': sale_order.so_bl_number,
            'inv_payment_note': sale_order.so_payment_note,
            'inv_conditions': sale_order.so_conditions,
            'inv_terms': sale_order.so_terms,
            'inv_bank_name': sale_order.so_bank_name,
            'inv_bank_branch': sale_order.so_bank_branch,
            'inv_bank_beneficiary': sale_order.so_bank_beneficiary,
            'inv_bank_account': sale_order.so_bank_account,
            'inv_bank_iban': sale_order.so_bank_iban,
            'inv_bank_swift': sale_order.so_bank_swift,
            'inv_bank_tel': sale_order.so_bank_tel,
            'inv_bank_fax': sale_order.so_bank_fax,
            'inv_bank_address': sale_order.so_bank_address,
            'inv_shipper_stamp': sale_order.so_shipper_stamp,
            # 'inv_buyer_stamp': sale_order.so_buyer_stamp,
        })
        
        # Copy packing lines
        for so_packing_line in sale_order.so_packing_line_ids:
            self.env['invoice.packing.line'].create({
                'move_id': invoice.id,
                'sequence': so_packing_line.sequence,
                'container_no': so_packing_line.container_no,
                'product_id': so_packing_line.product_id.id,
                'item_description': so_packing_line.item_description,
                'origin_country_id': so_packing_line.origin_country_id.id,
                'qty_cartons': so_packing_line.qty_cartons,
                'unit_weight_kg': so_packing_line.unit_weight_kg,
                'tare_per_carton': so_packing_line.tare_per_carton,
            })

    def _copy_shipping_data(self, source, target):
        """Copy shipping data from one invoice to another"""
        target.write({
            'inv_country_of_origin_id': source.inv_country_of_origin_id.id,
            'inv_board_date': source.inv_board_date,
            'inv_carriage_by': source.inv_carriage_by,
            'inv_port_of_loading': source.inv_port_of_loading.id,
            'inv_port_of_discharge': source.inv_port_of_discharge.id,
            'inv_waybill_no': source.inv_waybill_no,
            'inv_container_lta': source.inv_container_lta,
            'inv_place_of_delivery': source.inv_place_of_delivery,
            'inv_incoterm_id': source.inv_incoterm_id.id,
            'inv_bl_number': source.inv_bl_number,
            'inv_payment_note': source.inv_payment_note,
            'inv_conditions': source.inv_conditions,
            'inv_terms': source.inv_terms,
            'inv_bank_name': source.inv_bank_name,
            'inv_bank_branch': source.inv_bank_branch,
            'inv_bank_beneficiary': source.inv_bank_beneficiary,
            'inv_bank_account': source.inv_bank_account,
            'inv_bank_iban': source.inv_bank_iban,
            'inv_bank_swift': source.inv_bank_swift,
            'inv_bank_tel': source.inv_bank_tel,
            'inv_bank_fax': source.inv_bank_fax,
            'inv_bank_address': source.inv_bank_address,
        })

    def _fill_bank_from_company(self, invoice):
        """Fill bank details from company"""
        company = invoice.company_id
        invoice.write({
            'inv_bank_name':        company.ibic_bank_name or '',
            'inv_bank_branch':      company.ibic_bank_branch or '',
            'inv_bank_beneficiary': company.ibic_bank_beneficiary or '',
            'inv_bank_account':     company.ibic_bank_account or '',
            'inv_bank_iban':        company.ibic_bank_iban or '',
            'inv_bank_swift':       company.ibic_bank_swift or '',
            'inv_bank_tel':         company.ibic_bank_tel or '',
            'inv_bank_fax':         company.ibic_bank_fax or '',
            'inv_bank_address':     company.ibic_bank_address or '',
        })

    def action_fill_bank_from_company(self):
        """Button to reset bank details from company defaults."""
        for inv in self:
            self._fill_bank_from_company(inv)

    # ── Signature / Stamp images ─────────────────────────────────────────
    inv_shipper_stamp = fields.Binary(
        string='Shipper Stamp & Signature', attachment=True)
    inv_buyer_stamp = fields.Binary(
        string='Buyer Stamp & Signature', attachment=True)

    # ── Helper used in Packing List template ─────────────────────────────
    def _int_to_words(self, number, suffix=''):
        try:
            from num2words import num2words
            return num2words(int(number), lang='en').title() + (' ' + suffix if suffix else '')
        except Exception:
            return f"{int(number):,}" + (' ' + suffix if suffix else '')
