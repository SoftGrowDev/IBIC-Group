# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # ── Default bank details stored on the company ──────────────────────
    # These are copied to each new Sale Order and can be edited per SO.
    ibic_bank_name        = fields.Char(string='Default Bank Name')
    ibic_bank_branch      = fields.Char(string='Default Bank Branch / Currency')
    ibic_bank_beneficiary = fields.Char(string='Default Beneficiary')
    ibic_bank_account     = fields.Char(string='Default Account Number')
    ibic_bank_iban        = fields.Char(string='Default IBAN')
    ibic_bank_swift       = fields.Char(string='Default SWIFT Code')
    ibic_bank_tel         = fields.Char(string='Default Bank Tel')
    ibic_bank_fax         = fields.Char(string='Default Bank Fax')
    ibic_bank_address     = fields.Char(string='Default Bank Address')

    # ── Shipper Stamp (shown on proforma invoice) ────────────────────────
    ibic_shipper_stamp = fields.Binary(
        string='Shipper Stamp & Signature', attachment=True,
        help='Company-wide stamp/signature printed on the Proforma Invoice.')
