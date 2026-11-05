# -*- coding: utf-8 -*-
# from odoo import http


# class Consultation(http.Controller):
#     @http.route('/consultation/consultation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/consultation/consultation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('consultation.listing', {
#             'root': '/consultation/consultation',
#             'objects': http.request.env['consultation.consultation'].search([]),
#         })

#     @http.route('/consultation/consultation/objects/<model("consultation.consultation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('consultation.object', {
#             'object': obj
#         })

