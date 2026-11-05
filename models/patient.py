from odoo import models, fields, api
from datetime import date

class Patient(models.Model):
    _name = 'consultation.patient'
    _description = 'Patient'

    name = fields.Char(string='Name', required=True , tracking =True)
    dob = fields.Date(string='Date of Birth', required=True, tracking =True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True , inverse='_inverse_age', tracking =True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', tracking=True)
    phone = fields.Char(string='Phone Number', tracking=True)
    email = fields.Char(string='Email')
    address = fields.Text(string='Address',tracking=True)
    appointment_ids = fields.One2many('consultation.appointment', 'patient_id', string='Appointments')
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')

    @api.depends('dob')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.dob:
                record.age = today.year - record.dob.year - ((today.month, today.day) < (record.dob.month, record.dob.day))
            else:
                record.age = 0

    def _inverse_age(self):
        today = date.today()
        for record in self:
            if record.age:
                record.dob = date(today.year - record.age, today.month, today.day)
            else:
                record.dob = False
    
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)
