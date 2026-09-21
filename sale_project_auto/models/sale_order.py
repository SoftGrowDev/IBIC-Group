from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Linked Project',
        copy=False,
        tracking=True,
        help='Project automatically created when this sale order is confirmed.',
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        copy=False,
        tracking=True,
        help='Analytic account automatically created and linked to the project on confirmation.',
    )

    def _create_analytic_account_for_order(self):
        """Create an analytic account named after the sale order."""
        self.ensure_one()
        AnalyticAccount = self.env['account.analytic.account']

        # Resolve the default analytic plan (required in Odoo 17+/19)
        plan = self.env['account.analytic.plan'].search([], limit=1)
        vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
        }
        if plan:
            vals['plan_id'] = plan.id

        analytic_account = AnalyticAccount.create(vals)
        return analytic_account

    def _create_project_for_order(self, analytic_account):
        """Create a project named after the sale order and link the analytic account."""
        self.ensure_one()
        Project = self.env['project.project']

        vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'account_id': analytic_account.id,
            'user_id': self.user_id.id if self.user_id else False,
        }
        project = Project.create(vals)
        return project

    def _assign_analytic_to_order_lines(self, analytic_account):
        """Assign the analytic account to all sale order lines."""
        self.ensure_one()
        for line in self.order_line:
            # Odoo 17+/19 uses analytic_distribution (a JSON dict {analytic_account_id: percentage})
            line.analytic_distribution = {str(analytic_account.id): 100}

    def action_confirm(self):
        """Override confirm to auto-create project and analytic account."""
        res = super().action_confirm()

        for order in self:
            # Skip if project/analytic already exist (e.g. re-confirm after cancel)
            if order.project_id or order.analytic_account_id:
                continue

            # 1. Create the analytic account
            analytic_account = order._create_analytic_account_for_order()

            # 2. Create the project and link the analytic account
            project = order._create_project_for_order(analytic_account)

            # 3. Write back references on the sale order
            order.write({
                'analytic_account_id': analytic_account.id,
                'project_id': project.id,
            })

            # 4. Assign analytic account to all order lines
            order._assign_analytic_to_order_lines(analytic_account)

        return res

    def action_open_project(self):
        """Smart button to open the linked project."""
        self.ensure_one()
        if not self.project_id:
            raise UserError(_('No project linked to this sale order.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_analytic_account(self):
        """Smart button to open the linked analytic account."""
        self.ensure_one()
        if not self.analytic_account_id:
            raise UserError(_('No analytic account linked to this sale order.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.account',
            'res_id': self.analytic_account_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
