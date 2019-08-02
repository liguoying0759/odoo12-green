# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

# test git
class HarAccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = "时间日期限制24小时"

    @api.onchange('unit_amount')
    def _onchange_unit_amount(self):
        if self.unit_amount and self.unit_amount > 24:
            warning = {
                'title': _('时间范围不规范！'),
                'message':
                    _(
                        '请输入正确的时间范围~')}
            self.unit_amount = False
            return {'warning': warning}