# -*- coding: utf-8 -*-
from odoo import http

# class HarztecSendTaskMessage(http.Controller):
#     @http.route('/hz_pm_ex/hz_pm_ex/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hz_pm_ex/hz_pm_ex/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hz_pm_ex.listing', {
#             'root': '/hz_pm_ex/hz_pm_ex',
#             'objects': http.request.env['hz_pm_ex.hz_pm_ex'].search([]),
#         })

#     @http.route('/hz_pm_ex/hz_pm_ex/objects/<model("hz_pm_ex.hz_pm_ex"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hz_pm_ex.object', {
#             'object': obj
#         })