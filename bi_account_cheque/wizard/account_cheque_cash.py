# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountChequeCash(models.TransientModel):
    _name = 'account.cheque.cash'
    _description = 'Account Cheque Cash'

    date = fields.Date(required=True)
    account_id = fields.Many2one('account.account', required=True)
    amount = fields.Float(required=True)

    def action_cash(self):
        today = fields.Date.today()
        for cheque_id in self.env['account.cheque'].browse(self._context.get('active_ids')):
            if cheque_id.state in ('register', 'return', 'cash') and cheque_id.remaining_amount > 0.0:
                if cheque_id.remaining_amount < self.amount:
                    raise ValidationError(_("You can't cash more than the remaining amount."))

                is_outgoing = cheque_id.cheque_type == 'outgoing'

                self.env['account.move'].create({
                    'move_type': 'entry',
                    'date': self.date,
                    'journal_id': cheque_id.journal_id.id,
                    'company_id': cheque_id.company_id.id,
                    'state': 'draft',
                    'ref': cheque_id.cheque_number + ' - Cashed',
                    'account_cheque_id': cheque_id.id,
                    'line_ids': [
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': cheque_id.credit_account_id.id if is_outgoing else self.account_id.id,
                            'debit': self.amount,
                            'date_maturity': today,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': self.date,
                        }),
                        (0, 0, {
                            'partner_id': cheque_id.partner_id.id,
                            'account_id': self.account_id.id if is_outgoing else cheque_id.debit_account_id.id,
                            'credit': self.amount,
                            'date_maturity': today,
                            'company_id': cheque_id.company_id.id,
                            'name': cheque_id.cheque_number,
                            'cheque_date': self.date,
                        }),
                    ],
                }).action_post()

                self.env['account.cheque.log'].create({
                    'account_cheque_id': cheque_id.id,
                    'state': 'cash',
                    'date': self.date,
                    'account_id': self.account_id.id,
                })

                cheque_id.state = 'cash'
                cheque_id.finished_amount += self.amount
                cheque_id.cashed_account_id = self.account_id.id
