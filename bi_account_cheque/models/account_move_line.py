# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cheque_id = fields.Many2one(related='move_id.account_cheque_id')
    cheque_date = fields.Date()
