# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("bi_account_cheque: post-migration 18.0 -> 19.0 — completed successfully.")
