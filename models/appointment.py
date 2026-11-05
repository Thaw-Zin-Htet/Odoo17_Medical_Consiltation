import uuid
from odoo import models, fields, api

class Appointment(models.Model):
    _name = 'consultation.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Appointment Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('consultation.patient', string='Patient', required=True, tracking=True)
    doctor_id = fields.Many2one('consultation.doctor', string='Doctor', required=True, tracking=True)
    department_id = fields.Many2one('consultation.department', string='Department', required=True, tracking=True)
    appointment_date = fields.Datetime(string='Appointment Date', required=True, tracking=True)

    consultation_type = fields.Selection([
        ('in_person', 'In Person'),
        ('video_call', 'Video Call'),
        ('phone_call', 'Phone Call')
    ], string='Consultation Type', required=True, tracking=True)

    meeting_url = fields.Char(string='Meeting URL', tracking=True)
    phone_number = fields.Char(string='Phone Number', tracking=True, related='patient_id.phone')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('consultation.appointment') or 'New'

            if vals.get('consultation_type') == 'video_call' and not vals.get('meeting_url'):
                unique_token = uuid.uuid4().hex[:8]
                vals['meeting_url'] = f"https://meet.jit.si/ClinicConsultation-{unique_token}"
    
        return super(Appointment, self).create(vals_list)

    @api.onchange('consultation_type')
    def _onchange_consultation_type(self):
        if self.consultation_type == 'video_call':
            unique_token = uuid.uuid4().hex[:8]
            self.meeting_url = f"https://meet.jit.si/ClinicConsultation-{unique_token}"
        elif self.consultation_type != 'video_call':
            self.meeting_url = False
