# -*- coding: utf-8 -*-

import logging

from odoo.upgrade.util.helpers import table_of_model
from odoo.upgrade.util.pg import remove_column

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("UPDATE account_cheque SET state = status WHERE cheque_type = 'outgoing'")

    remove_column(cr, table_of_model(cr, 'account.cheque'), 'status')

    _logger.info("Dropped account_cheque Status Column")
