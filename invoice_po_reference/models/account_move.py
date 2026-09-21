# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    po_reference = fields.Char(
        string="PO Reference",
        copy=False,
        help="Customer's Purchase Order reference for this invoice. "
        "Required before the invoice can be confirmed.",
    )

    @api.constrains("po_reference", "state", "move_type")
    def _check_po_reference_required(self):
        for move in self:
            if (
                move.move_type in ("out_invoice", "out_refund")
                and move.state == "posted"
                and not (move.po_reference and move.po_reference.strip())
            ):
                raise ValidationError(
                    _("PO Reference is mandatory before confirming a customer invoice/credit note (%s).")
                    % move.name
                )
