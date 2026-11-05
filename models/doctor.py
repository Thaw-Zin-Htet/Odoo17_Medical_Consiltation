from odoo import models, fields

class Department(models.Model):
    _name = 'consultation.department'
    _description = 'Department'

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)

class Doctor(models.Model):
    _name = 'consultation.doctor'
    _description = 'Doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    department_id = fields.Many2one('consultation.department', string='Department', tracking=True)
    specialization = fields.Char(string='Specialization', tracking=True)
    consultation_fee = fields.Float(string='Consultation Fee', tracking=True)
    user_id = fields.Many2one('res.users', string='User', tracking=True)
    
