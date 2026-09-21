from odoo import fields, models


class AnalyticLineReportWizard(models.TransientModel):
    _name = 'analytic.line.report.wizard'
    _description = 'Analytic Line Report Wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_print_pdf(self):
        return self.env.ref(
            'analytic_usd_report.action_analytic_line_pdf_report'
        ).report_action(self)

    def action_export_xlsx(self):
        lines = self.env['account.analytic.line'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Analytic Lines',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', lines.ids)],
        }
