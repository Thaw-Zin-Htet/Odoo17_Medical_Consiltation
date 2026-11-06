import uuid
from datetime import timedelta
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
    invoice_id = fields.Many2one('account.move', string='Invoice', tracking=True)

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

    # Invoice Generation: Create an invoice for the appointment
    def create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            raise ValidationError("An invoice has already been created for this appointment.")
        
        # Ensure patient has a res.partner record to attach the invoice
        partner = getattr(self.patient_id, 'partner_id', None)
        if not partner:
            partner = self.env['res.partner'].create({
                'name':self.patient_id.name,
                'phone':getattr(self.patient_id, 'phone', False),
                'email':self.patient_id.email,
            })
        
        # Programically create an customer invoice 
        invoice_vals ={
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Consultation witn Dr. {self.doctor_id.name} on {self.appointment_date}',
                'quantity': 1,
                'price_unit': self.doctor_id.consultation_fee,
            })],
        }

        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id

        # Return action window to open the created invoice in form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    # action view invoice: Open the invoice related to the appointment
    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise ValidationError("No invoice has been created for this appointment.")
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Invoice',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.invoice_id.id,
                'target': 'current',
            }



    # Business Logic: Automatically set the department based on the selected doctor
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        if self.doctor_id:
            self.department_id = self.doctor_id.department_id

    # Business Logic: Overlapping Prevention
    @api.constrains('doctor_id', 'appointment_date', 'state')
    def _check_overlapping_appointments(self):
        for appointment in self:
            if appointment.appointment_date and appointment.doctor_id and appointment.state != 'cancelled':
                overlapping_appointments = self.env['consultation.appointment'].search([
                    ('doctor_id', '=', appointment.doctor_id.id),
                    ('appointment_date', '=', appointment.appointment_date),
                    ('id', '!=', appointment.id),
                    ('state', '!=', 'cancelled')
                ])
                if overlapping_appointments:
                    raise models.ValidationError(f"The selected doctor ({appointment.doctor_id.name}) already has an appointment scheduled at {appointment.appointment_date}. Please choose a different time or doctor.")
    
    # Business Logic: No Past-Date Appointments
    @api.constrains('appointment_date')
    def _check_past_date_appointments(self):
        for appointment in self:
            if appointment.appointment_date < fields.Datetime.now():
                raise models.ValidationError("You cannot schedule an appointment in the past. Please choose a future date and time.")

    # Business Logic: Department Consistency
    @api.constrains('doctor_id', 'department_id')
    def _check_department_consistency(self):
        for appointment in self:
            if appointment.doctor_id and appointment.department_id:
                if appointment.doctor_id.department_id != appointment.department_id:
                    raise models.ValidationError(f"The selected doctor ({appointment.doctor_id.name}) does not belong to the selected department ({appointment.department_id.name}). Please select a valid department for the doctor.")

    # Business Logic: after one day of the appointment, the status should automatically change to 'done'
    @api.model
    def _cron_update_appointment_status(self):
        appointments = self.search([('state', '=', 'confirmed')])
        for appointment in appointments:
            if appointment.appointment_date and appointment.appointment_date < fields.Datetime.now() - timedelta(days=1):
                appointment.state = 'done'
