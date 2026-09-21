# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountChequeReturn(models.TransientModel):
    _name = 'account.cheque.return'
    _description = 'Account Cheque Return'

    date = fields.Date(required=True)
    reason = fields.Char()

    def action_return(self):
        today = fields.Date.today()
        for cheque_id in self.env['account.cheque'].browse(self._context.get('active_ids')):
            if cheque_id.cheque_type == 'incoming' and cheque_id.state == 'deposit':
                self.env['account.move'].create({
                    'partner_id': cheque_id.partner_id.id,
                    'move_type': 'entry',
                    'date': self.date,
                    'journal_id': cheque_id.journal_id.id,
                    'company_id': cheque_id.company_id.id,
                    'state': 'draft',
                    'ref': cheque_id.cheque_number + ' - Returned',
                    'account_cheque_id': cheque_id.id,
                    'line_ids': [
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.debit_account_id.id,
                            'debit': cheque_id.amount,
                            'date_maturity': self.date,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': today,
                        }),
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.deposit_account_id.id,
                            'credit': cheque_id.amount,
                            'date_maturity': self.date,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': today,
                        }),
                    ],
                }).action_post()

                self.env['account.cheque.log'].create({
                    'account_cheque_id': cheque_id.id,
                    'state': 'return',
                    'date': self.date,
                    'account_id': cheque_id.deposit_account_id.id,
                })

                cheque_id.state = 'return'
                cheque_id.return_reason = self.reason
                cheque_id.cheque_return_date = today
