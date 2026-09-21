# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountChequeDeposit(models.TransientModel):
    _name = 'account.cheque.deposit'
    _description = 'Account Cheque Deposit'

    date = fields.Date(required=True)
    account_id = fields.Many2one('account.account', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        cheque = self.env['account.cheque'].browse(self._context.get('active_id'))
        res['account_id'] = cheque.company_id.deposit_account_id.id
        return res

    def action_deposit(self):
        for cheque_id in self.env['account.cheque'].browse(self._context.get('active_ids')):
            if cheque_id.cheque_type == 'incoming' and cheque_id.state in ('register', 'return'):
                self.env['account.move'].create({
                    'partner_id': cheque_id.partner_id.id,
                    'move_type': 'entry',
                    'date': self.date,
                    'journal_id': cheque_id.journal_id.id,
                    'company_id': cheque_id.company_id.id,
                    'state': 'draft',
                    'ref': cheque_id.cheque_number + ' - Deposited',
                    'account_cheque_id': cheque_id.id,
                    'line_ids': [
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': self.account_id.id,
                            'debit': cheque_id.amount,
                            'date_maturity': self.date,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': self.date,
                        }),
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.debit_account_id.id,
                            'credit': cheque_id.amount,
                            'date_maturity': self.date,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': self.date,
                        }),
                    ],
                }).action_post()

                self.env['account.cheque.log'].create({
                    'account_cheque_id': cheque_id.id,
                    'state': 'deposit',
                    'date': self.date,
                    'account_id': self.account_id.id,
                })

                cheque_id.state = 'deposit'
                cheque_id.deposit_account_id = self.account_id
