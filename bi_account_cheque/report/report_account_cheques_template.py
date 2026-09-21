# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReportAccountChequesTemplate(models.AbstractModel):
    _name = 'report.bi_account_cheque.report_account_cheques_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'account.cheque',
            'docs': self.env['account.cheque'].browse(data['account_cheque_ids']),
            'data': data,
        }
