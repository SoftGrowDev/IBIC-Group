# -*- coding: utf-8 -*-

import logging

from odoo.upgrade.util.models import remove_model, rename_model
from odoo.upgrade.util.fields import remove_field, rename_field, change_field_selection_values
from odoo.upgrade.util.records import remove_view, remove_record

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    remove_record(cr, 'bi_account_cheque.model_cheque_update_log_draft')
    remove_record(cr, 'bi_account_cheque.model_update_cheque_no')

    _logger.info("Removed all bi_account_cheque ir.actions.server records")

    remove_record(cr, 'bi_account_cheque.cheque_entry_menu')
    remove_record(cr, 'bi_account_cheque.menu_cheque_reporting')

    remove_record(cr, 'bi_account_cheque.account_cheque_report_action')

    remove_view(cr, 'bi_account_cheque.account_cheque_tree')

    _logger.info("Removed 'Cheque Management > Reporting > Cheque Report' Menu")

    remove_record(cr, 'bi_account_cheque.menu_sub_incoming_cheque')

    remove_record(cr, 'bi_account_cheque.act_incoming_view_form')
    remove_record(cr, 'bi_account_cheque.act_incoming_view_tree')
    remove_record(cr, 'bi_account_cheque.action_incoming_cheque')

    remove_view(cr, 'bi_account_cheque.account_incoming_cheque_form_view')
    remove_view(cr, 'bi_account_cheque.account_incoming_cheque_tree_view')

    _logger.info("Removed 'Cheque Management > Incoming Cheque' Menu")

    remove_record(cr, 'bi_account_cheque.menu_sub_outgoing_cheque')

    remove_record(cr, 'bi_account_cheque.act_outgoing_view_form')
    remove_record(cr, 'bi_account_cheque.act_outgoing_view_tree')
    remove_record(cr, 'bi_account_cheque.action_outgoing_cheque')

    remove_view(cr, 'bi_account_cheque.account_outgoing_cheque_form_view')
    remove_view(cr, 'bi_account_cheque.account_outgoing_cheque_tree_view')

    _logger.info("Removed 'Cheque Management > Outgoing Cheque' Menu")

    remove_record(cr, 'bi_account_cheque.menu_account_cheque')

    _logger.info("Removed 'Cheque Management' Menu")

    remove_field(cr, 'account.cheque', 'sequence')
    remove_field(cr, 'account.cheque', 'bank_account_id')
    rename_field(cr, 'account.cheque', 'account_cheque_type', 'cheque_type')
    rename_field(cr, 'account.cheque', 'cheque_date', 'date')
    rename_field(cr, 'account.cheque', 'payee_user_id', 'partner_id')
    rename_field(cr, 'account.cheque', 'comment', 'description')
    rename_field(cr, 'account.cheque', 'attchment_ids', 'attachment_ids')
    change_field_selection_values(cr, 'account.cheque', 'status', {
        'draft': 'draft',
        'registered': 'register',
        'bounced': 'bounce',
        'bank_collection': 'bank_collect',
        'return': 'return',
        'cashed': 'cash',
        'cancel': 'cancel'
    })
    remove_field(cr, 'account.cheque', 'status', drop_column=False)
    change_field_selection_values(cr, 'account.cheque', 'status1', {
        'draft': 'draft',
        'registered': 'register',
        'bounced': 'bounce',
        'bank_collection': 'bank_collect',
        'return': 'return',
        'deposited': 'deposit',
        'transfered': 'transfer',
        'return_to_customer': 'return_to_customer',
        'cashed': 'cash',
        'cancel': 'cancel'
    })
    rename_field(cr, 'account.cheque', 'status1', 'state')
    change_field_selection_values(cr, 'account.cheque', 'last_log_status', {
        'draft': 'draft',
        'registered': 'register',
        'bounced': 'bounce',
        'bank_collection': 'bank_collect',
        'return': 'return',
        'deposited': 'deposit',
        'transfered': 'transfer',
        'return_to_customer': 'return_to_customer',
        'cashed': 'cash',
        'cancel': 'cancel'
    })
    rename_field(cr, 'account.cheque', 'last_log_status', 'last_log_state')
    rename_field(cr, 'account.cheque', 'attachment_count', 'attachments_count')

    _logger.info("Updated account.cheque Fields")

    remove_record(cr, 'bi_account_cheque.cheque_wizard_action')

    remove_view(cr, 'bi_account_cheque.cheque_wizard_wizard_view')

    remove_model(cr, 'cheque.wizard')

    _logger.info("Removed cheque.wizard Model")

    remove_record(cr, 'bi_account_cheque.cheque_deposit_action')

    remove_view(cr, 'bi_account_cheque.cheque_deposit_view')

    remove_model(cr, 'cheque.deposit')

    _logger.info("Removed cheque.deposit Model")

    remove_record(cr, 'bi_account_cheque.cheque_cheque_return_customer_action')

    remove_view(cr, 'bi_account_cheque.cheque_cheque_return_customer_view')

    remove_model(cr, 'cheque.return.customer')

    _logger.info("Removed cheque.return.customer Model")

    remove_record(cr, 'bi_account_cheque.cheque_cheque_return_action')

    remove_view(cr, 'bi_account_cheque.cheque_cheque_return_view')

    remove_model(cr, 'cheque.return')

    _logger.info("Removed cheque.return Model")

    remove_record(cr, 'bi_account_cheque.bank_collection_action')

    remove_view(cr, 'bi_account_cheque.bank_collection_view')

    remove_model(cr, 'bank.collection')

    _logger.info("Removed bank.collection Model")

    remove_record(cr, 'bi_account_cheque.cheque_transfered_wizard_action')

    remove_view(cr, 'bi_account_cheque.cheque_transfered_wizard_wizard_view')

    remove_model(cr, 'cheque.transfered.wizard')

    _logger.info("Removed cheque.transfered.wizard Model")

    remove_model(cr, 'report.bi_account_cheque.account_cheque_template')

    remove_record(cr, 'bi_account_cheque.account_cheque_report_id')
    remove_record(cr, 'bi_account_cheque.account_cheque_template')
    remove_record(cr, 'bi_account_cheque.account_cheque_report_template_document')

    remove_record(cr, 'bi_account_cheque.menu_account_cheque_report')

    remove_record(cr, 'bi_account_cheque.action_report_wizard')

    remove_view(cr, 'bi_account_cheque.report_form_account_cheque')

    remove_model(cr, 'report.wizard')

    _logger.info("Removed report.wizard Model")

    change_field_selection_values(cr, 'cheque.log', 'state', {
        'draft': 'draft',
        'registered': 'register',
        'bounced': 'bounce',
        'bank_collection': 'bank_collect',
        'return': 'return',
        'deposited': 'deposit',
        'transfered': 'transfer',
        'return_to_customer': 'return_to_customer',
        'cashed': 'cash',
        'cancel': 'cancel'
    })

    _logger.info("Updated cheque.log Fields")

    rename_model(cr, 'cheque.log', 'account.cheque.log')

    _logger.info("Renamed cheque.log Model")

    remove_field(cr, 'account.move.line', 'is_cheque')

    _logger.info("Updated account.move.line Fields")

    remove_record(cr, 'bi_account_cheque.bi_account_cheque_inherit_res_config_view')

    rename_field(cr, 'res.config.settings', 'deposite_account_id', 'deposit_account_id')

    _logger.info("Updated res.config.settings Fields")
