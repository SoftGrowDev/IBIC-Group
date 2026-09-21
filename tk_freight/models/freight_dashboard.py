# -*- coding: utf-8 -*-
# Copyright 2020 - Today Techkhedut.
# Part of Techkhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime


class DashboardDetails(models.Model):
    _name = 'dashboard.details'
    _description = 'Freight Dashboard'

    name = fields.Char(translate=True)

    @api.model
    def get_freight_info(self):
        fright_shipment = self.env['freight.shipment'].sudo()
        direct_count = fright_shipment.search_count([('operation', '=', 'direct')])
        house_count = fright_shipment.search_count([('operation', '=', 'house')])
        master_count = fright_shipment.search_count([('operation', '=', 'master')])
        pending_booking = self.env['shipment.freight.booking'].search_count([('state', '=', 'draft')])
        total_port = self.env['freight.port'].search_count([])
        total_packages = self.env['freight.package'].search_count([])
        air = fright_shipment.search_count([('transport', '=', 'air')])
        ocean = fright_shipment.search_count([('transport', '=', 'ocean')])
        land = fright_shipment.search_count([('transport', '=', 'land')])
        import_count = fright_shipment.search_count([('direction', '=', 'import')])
        export_count = fright_shipment.search_count([('direction', '=', 'export')])

        data = {
            'air': air,
            'ocean': ocean,
            'land': land,
            'direct_count': direct_count,
            'house_count': house_count,
            'master_count': master_count,
            'pending_booking': pending_booking,
            'total_port': total_port,
            'total_packages': total_packages,
            'transport': [['Air Shipment', 'Ocean Shipment', 'Land Shipment'], [air, ocean, land]],
            'fright_operation': [[direct_count, house_count, master_count],
                                 ['Direct Shipment', 'House Shipment', 'Master Shipment']],
            'top_consign': self.get_top_consignee(),
            'move_type': self.get_move_type(),
            'freight_direction': [['Import', 'Export'], [import_count, export_count]],
            'get_shipment_month': [
                self.get_shipment_month(),
                self.get_air_shipment_month(),
                self.get_land_shipment_month(),
                self.get_ocean_shipment_month(),
            ],
            'top_shipper': self.get_top_shipper(),
            'get_bill_invoice': [
                self.get_shipment_month(),
                self.get_freight_bills(),
                self.get_freight_invoice(),
            ],
        }

        stages, shipment_counts = [], []
        stage_ids = self.env['freight.shipment.stages'].search([], order='sequence asc')
        for stg in stage_ids:
            shipment_counts.append(fright_shipment.search_count([('stage_id', '=', stg.id)]))
            stages.append(stg.name)
        data['shipment_stages'] = [stages, shipment_counts]
        return data

    def get_top_consignee(self):
        partner, amount = [], []
        consignee_ids = self.env['res.partner'].search([('consignee', '=', True)]).ids
        # Odoo 19: _read_group replaces read_group for aggregations
        groups = self.env['account.move']._read_group(
            domain=[('partner_id', 'in', consignee_ids)],
            groupby=['partner_id'],
            aggregates=['amount_total:sum'],
        )
        # Sort by amount descending, take top 5
        groups_sorted = sorted(groups, key=lambda g: g[1], reverse=True)[:5]
        for partner_rec, total in groups_sorted:
            if partner_rec:
                partner.append(partner_rec.name)
                amount.append(total)
        return [partner, amount]

    def get_move_type(self):
        move_type, counts = [], []
        for mtype in self.env['freight.move.type'].search([]):
            counts.append(self.env['freight.shipment'].search_count([('move_type', '=', mtype.id)]))
            move_type.append(mtype.name)
        return [move_type, counts]

    def get_shipment_month(self):
        return ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December']

    def _count_by_month(self, transport=None):
        year = fields.date.today().year
        data_dict = {m: 0 for m in self.get_shipment_month()}
        domain = []
        if transport:
            domain = [('transport', '=', transport)]
        for ship in self.env['freight.shipment'].search(domain):
            if ship.create_datetime and ship.create_datetime.year == year:
                month_name = ship.create_datetime.strftime("%B")
                if month_name in data_dict:
                    data_dict[month_name] += 1
        return list(data_dict.values())

    def get_air_shipment_month(self):
        return self._count_by_month('air')

    def get_ocean_shipment_month(self):
        return self._count_by_month('ocean')

    def get_land_shipment_month(self):
        return self._count_by_month('land')

    def get_top_shipper(self):
        # Odoo 19: use _read_group instead of read_group
        groups = self.env['freight.shipment']._read_group(
            domain=[],
            groupby=['shipper_id'],
            aggregates=['__count'],
        )
        shipper = {}
        for shipper_rec, count in groups:
            if shipper_rec:
                shipper[shipper_rec.name] = count
        shipper = dict(sorted(shipper.items(), key=lambda x: x[1], reverse=True)[:10])
        return [list(shipper.keys()), list(shipper.values())]

    def _get_monthly_amounts(self, move_type_filter):
        year = fields.date.today().year
        data_dict = {m: 0 for m in self.get_shipment_month()}
        for move in self.env['account.move'].search([]):
            if move.invoice_date and move.invoice_date.year == year \
                    and move.move_type == move_type_filter and move.freight_operation_id:
                month_name = move.invoice_date.strftime("%B")
                if month_name in data_dict:
                    data_dict[month_name] += move.amount_total
        return list(data_dict.values())

    def get_freight_bills(self):
        return self._get_monthly_amounts('in_invoice')

    def get_freight_invoice(self):
        return self._get_monthly_amounts('out_invoice')
