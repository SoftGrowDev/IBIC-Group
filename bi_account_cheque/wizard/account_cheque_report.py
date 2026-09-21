# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountChequeReport(models.TransientModel):
    _name = 'account.cheque.report'

    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)
    cheques_type = fields.Selection([('incoming', 'Incoming'), ('outgoing', 'Outgoing')])

    def action_print(self):
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]

        if self.cheques_type:
            domain.append(('cheque_type', '=', self.cheques_type))

        account_cheque_ids = self.env['account.cheque'].search(domain)

        if not account_cheque_ids:
            raise UserError(_('There are no %s from %s to %s.' % (
                (self.cheques_type + ' cheques') if self.cheques_type else 'cheques', self.from_date, self.to_date
            )))

        return self.env.ref('bi_account_cheque.report_account_cheques').report_action(self, data={
            'from_date': self.from_date,
            'to_date': self.to_date,
            'cheques_type': self.cheques_type,
            'account_cheque_ids': account_cheque_ids.ids
        })
