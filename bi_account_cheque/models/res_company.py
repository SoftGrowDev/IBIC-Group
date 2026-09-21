# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    in_credit_account_id = fields.Many2one('account.account', string='Credit Account')
    in_debit_account_id = fields.Many2one('account.account', string='Debit Account')

    out_credit_account_id = fields.Many2one('account.account', string='Credit Account')
    out_debit_account_id = fields.Many2one('account.account', string='Debit Account')

    deposit_account_id = fields.Many2one('account.account', string='Deposit Account')
    specific_journal_id = fields.Many2one('account.journal', string='Specific Journal')
