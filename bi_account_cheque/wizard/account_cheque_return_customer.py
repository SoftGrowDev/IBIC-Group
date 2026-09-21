# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountChequeReturnCustomer(models.TransientModel):
    _name = 'account.cheque.return.customer'
    _description = 'Account Cheque Return To Customer'

    date = fields.Date(required=True)

    def action_return_customer(self):
        for cheque_id in self.env['account.cheque'].browse(self._context.get('active_ids')):
            if cheque_id.cheque_type == 'incoming' and cheque_id.state == 'return':
                self.env['account.move'].create({
                    'partner_id': cheque_id.partner_id.id,
                    'move_type': 'entry',
                    'date': self.date,
                    'journal_id': cheque_id.journal_id.id,
                    'company_id': cheque_id.company_id.id,
                    'state': 'draft',
                    'ref': cheque_id.cheque_number + ' - Returned To Customer',
                    'account_cheque_id': cheque_id.id,
                    'line_ids': [
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.credit_account_id.id,
                            'debit': cheque_id.amount,
                            'date_maturity': self.date,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                        }),
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.debit_account_id.id,
                            'credit': cheque_id.amount,
                            'date_maturity': self.date,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                        }),
                    ],
                }).action_post()

                self.env['account.cheque.log'].create({
                    'account_cheque_id': cheque_id.id,
                    'state': 'return_to_customer',
                    'date': self.date,
                    'account_id': cheque_id.debit_account_id.id,
                })

                cheque_id.state = 'return_to_customer'
