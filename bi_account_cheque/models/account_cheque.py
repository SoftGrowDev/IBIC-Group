# -*- coding: utf-8 -*-

from datetime import datetime
import ast

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountCheque(models.Model):
    _name = 'account.cheque'
    _inherit = ['mail.thread']
    _description = 'Account Cheque'
    _order = 'id desc'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('register', 'Registered'),
        ('bounce', 'Bounced'),
        ('bank_collect', 'Bank Collected'),
        ('return', 'Returned'),
        ('deposit', 'Deposited'),
        ('transfer', 'Transferred'),
        ('return_to_customer', 'Returned To Customer'),
        ('cash', 'Cashed'),
        ('cancel', 'Cancelled'),
    ], default='draft', string='Status', copy=False, index=True, tracking=True)

    journal_items_count = fields.Integer(compute='_compute_journal_items_count')

    name = fields.Char(required=True)

    cheque_type = fields.Selection([('incoming', 'Incoming'), ('outgoing', 'Outgoing')], required=True, readonly=True)
    bank_id = fields.Many2one('res.bank')
    cheque_number = fields.Char(required=True)
    amount = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
        store=True,
    )
    remaining_amount = fields.Monetary(compute='_compute_remaining_amount', currency_field='currency_id')
    finished_amount = fields.Monetary(currency_field='currency_id')

    partner_id = fields.Many2one('res.partner', required=True)
    date = fields.Date(default=fields.Date.context_today)
    cheque_given_date = fields.Date()
    cheque_receive_date = fields.Date()
    cheque_return_date = fields.Date()

    credit_account_id = fields.Many2one('account.account')
    debit_account_id = fields.Many2one('account.account')
    journal_id = fields.Many2one('account.journal', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    return_reason = fields.Char(readonly=True)

    description = fields.Text()

    invoice_ids = fields.One2many('account.move', 'account_cheque_id', string='Invoices')

    attachment_ids = fields.One2many('ir.attachment', 'account_cheque_id', string='Attachments')
    attachments_count = fields.Integer(compute='_get_attachments_count')

    cheque_log_ids = fields.One2many('account.cheque.log', 'account_cheque_id')

    last_log_state = fields.Selection([
        ('draft', 'Draft'),
        ('register', 'Registered'),
        ('bounce', 'Bounced'),
        ('bank_collect', 'Bank Collected'),
        ('return', 'Returned'),
        ('deposit', 'Deposited'),
        ('transfer', 'Transferred'),
        ('return_to_customer', 'Returned To Customer'),
        ('cash', 'Cashed'),
        ('cancel', 'Cancelled'),
    ], compute='_compute_last_log', store=True)
    last_log_date = fields.Date(compute='_compute_last_log', store=True)
    last_log_account_id = fields.Many2one('account.account', compute='_compute_last_log', store=True)

    deposit_account_id = fields.Many2one('account.account')
    cashed_account_id = fields.Many2one('account.account')

    _sql_constraints = [('unique_cheque_number', 'UNIQUE(cheque_number)', 'Cheque Number must be unique')]

    @api.depends('invoice_ids')
    def _compute_journal_items_count(self):
        for rec in self:
            rec.journal_items_count = len(
                self.env['account.move'].search([('account_cheque_id', '=', rec.id)]).mapped('line_ids')
            )

    @api.depends('amount', 'finished_amount')
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = (rec.amount - rec.finished_amount) if rec.amount else 0.0

    @api.depends('attachment_ids')
    def _get_attachments_count(self):
        for rec in self:
            rec.attachments_count = len(rec.attachment_ids)

    @api.depends('cheque_log_ids', 'state', 'debit_account_id')
    def _compute_last_log(self):
        for rec in self:
            if rec.cheque_log_ids:
                last = rec.cheque_log_ids[-1]
                rec.last_log_state = last.state
                rec.last_log_date = last.date
                rec.last_log_account_id = last.account_id.id
            else:
                rec.last_log_state = rec.state
                rec.last_log_date = False
                rec.last_log_account_id = rec.debit_account_id.id if rec.state == 'register' else False

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        if res.get('company_id'):
            company = self.env['res.company'].browse(res['company_id'])

            if self._context.get('default_cheque_type') == 'incoming':
                res['credit_account_id'] = company.in_credit_account_id.id
                res['debit_account_id'] = company.in_debit_account_id.id
            else:
                res['credit_account_id'] = company.out_credit_account_id.id
                res['debit_account_id'] = company.out_debit_account_id.id

            res['journal_id'] = company.specific_journal_id.id

        return res

    def action_view_journal_items(self):
        self.ensure_one()
        return {
            'name': _('Journal Items'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move.line',
            'domain': [('id', 'in', self.env['account.move'].search([
                ('account_cheque_id', '=', self.id)
            ]).mapped('line_ids').ids)],
        }

    def action_view_payment_matching(self):
        self.ensure_one()

        action_values = self.env['ir.actions.act_window']._for_xml_id(
            'account_accountant.action_move_line_posted_unreconciled'
        )

        if self.partner_id:
            context = ast.literal_eval(action_values['context'])
            context.update({'search_default_partner_id': self.partner_id.id})
            if self.cheque_type == 'incoming':
                context.update({'search_default_trade_receivable': 1})
            else:
                context.update({'search_default_trade_payable': 1})
            action_values['context'] = context

        return action_values

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'ir.attachment',
            'domain': [('account_cheque_id', '=', self.id)],
        }

    def action_register(self):
        for rec in self:
            if not (rec.credit_account_id and rec.debit_account_id):
                raise ValidationError(_('Must specify credit account and debit account before submitting.'))

            move_date = rec.cheque_receive_date if rec.cheque_type == 'incoming' else rec.cheque_given_date

            self.env['account.move'].create({
                'name': rec.name,
                'date': move_date,
                'journal_id': rec.journal_id.id,
                'company_id': rec.company_id.id,
                'state': 'draft',
                'ref': rec.cheque_number + ' - Registered',
                'account_cheque_id': rec.id,
                'line_ids': [
                    (0, 0, {
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.debit_account_id.id,
                        'debit': rec.amount,
                        'date_maturity': rec.date,
                        'company_id': rec.company_id.id,
                        'name': rec.cheque_number,
                        'cheque_date': rec.date,
                    }),
                    (0, 0, {
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.credit_account_id.id,
                        'credit': rec.amount,
                        'date_maturity': rec.date,
                        'company_id': rec.company_id.id,
                        'name': rec.cheque_number,
                        'cheque_date': rec.date,
                    }),
                ],
            }).action_post()

            self.env['account.cheque.log'].create({
                'account_cheque_id': rec.id,
                'state': 'register',
                'date': move_date,
                'account_id': rec.credit_account_id.id,
            })

            rec.state = 'register'

    def action_cancel(self):
        for rec in self:
            self.env['account.move'].search([('account_cheque_id', '=', rec.id)]).button_cancel()

            self.env['account.cheque.log'].create({
                'account_cheque_id': rec.id,
                'state': 'cancel',
                'date': fields.Date.today(),
                'account_id': rec.debit_account_id.id,
            })

            rec.state = 'cancel'
