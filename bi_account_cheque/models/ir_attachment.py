# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    account_cheque_id = fields.Many2one('account.cheque')
