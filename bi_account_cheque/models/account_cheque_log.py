# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountChequeLog(models.Model):
    _name = 'account.cheque.log'
    _description = 'Account Cheque Log'

    account_cheque_id = fields.Many2one('account.cheque')
    state = fields.Selection([('draft', 'Draft'), ('register', 'Registered'), ('bounce', 'Bounced'),
                              ('bank_collect', 'Bank Collected'), ('return', 'Returned'),
                              ('deposit', 'Deposited'), ('transfer', 'Transferred'),
                              ('return_to_customer', 'Returned To Customer'), ('cash', 'Cashed'),
                              ('cancel', 'Cancelled')], string='Status')
    date = fields.Date()
    account_id = fields.Many2one('account.account')
