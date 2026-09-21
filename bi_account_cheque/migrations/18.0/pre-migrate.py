# -*- coding: utf-8 -*-
# Migration script for upgrading bi_account_cheque from 18.0 to 19.0
# No structural changes required between these versions.
# amount/finished_amount/remaining_amount fields changed from Float to Monetary
# but the underlying DB column type (numeric) is the same, so no column migration needed.

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("bi_account_cheque: pre-migration 18.0 -> 19.0 — no structural changes required.")
