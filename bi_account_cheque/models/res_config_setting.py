# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    in_credit_account_id = fields.Many2one(related='company_id.in_credit_account_id', readonly=False)
    in_debit_account_id = fields.Many2one(related='company_id.in_debit_account_id', readonly=False)

    out_credit_account_id = fields.Many2one(related='company_id.out_credit_account_id', readonly=False)
    out_debit_account_id = fields.Many2one(related='company_id.out_debit_account_id', readonly=False)

    deposit_account_id = fields.Many2one(related='company_id.deposit_account_id', readonly=False)
    specific_journal_id = fields.Many2one(related='company_id.specific_journal_id', readonly=False)
