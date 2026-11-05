from odoo import models, fields

class Department(models.Model):
    _name = 'consultation.department'
    _description = 'Department'

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    doctor_ids = fields.One2many('consultation.doctor', 'department_id', string='Doctors')

class Doctor(models.Model):
    _name = 'consultation.doctor'
    _description = 'Doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    department_id = fields.Many2one('consultation.department', string='Department', tracking=True)
    patient_ids = fields.Many2many('consultation.patient', string='Patients', tracking=True)
    
