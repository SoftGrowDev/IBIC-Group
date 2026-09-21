# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountChequeTransfer(models.TransientModel):
    _name = 'account.cheque.transfer'
    _description = 'Account Cheque Transfer'

    date = fields.Date(required=True)
    contact_id = fields.Many2one('res.partner', required=True)

    def action_transfer(self):
        today = fields.Date.today()
        for cheque_id in self.env['account.cheque'].browse(self._context.get('active_ids')):
            if cheque_id.cheque_type == 'incoming' and cheque_id.state == 'register':
                self.env['account.move'].create({
                    'partner_id': self.contact_id.id,
                    'move_type': 'entry',
                    'date': self.date,
                    'journal_id': cheque_id.journal_id.id,
                    'company_id': cheque_id.company_id.id,
                    'state': 'draft',
                    'ref': cheque_id.cheque_number + ' - Transferred',
                    'account_cheque_id': cheque_id.id,
                    'line_ids': [
                        (0, 0, {
                            'partner_id': self.contact_id.id,
                            'account_id': self.contact_id.property_account_payable_id.id,
                            'debit': cheque_id.amount,
                            'date_maturity': today,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': today,
                        }),
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.debit_account_id.id,
                            'credit': cheque_id.amount,
                            'date_maturity': today,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': today,
                        }),
                    ],
                }).action_post()

                self.env['account.cheque.log'].create({
                    'account_cheque_id': cheque_id.id,
                    'state': 'transfer',
                    'date': self.date,
                    'account_id': cheque_id.debit_account_id.id,
                })

                cheque_id.state = 'transfer'
