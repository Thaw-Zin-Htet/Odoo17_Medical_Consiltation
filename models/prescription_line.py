from odoo import models, fields

class PrescriptionLine(models.Model):
    _name = 'consultation.prescription.line'
    _description = 'Prescription Line'

    appointment_id = fields.Many2one('consultation.appointment', string='Appointment', required=True, ondelete='cascade')
    medicine_name = fields.Char(string='Medicine/Treatment Name', required=True)
    dosage = fields.Char(string='Dosage(eg.,50mg)', required=True)
    frequency = fields.Selection([
        ('1_daily', 'Once Daily'),
        ('2_daily', 'Twice Daily'),
        ('3_daily', 'Thrice Daily'),
        ('4_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed')
    ], string='Frequency', default="2_daily",required=True)
    duration_days = fields.Integer(string='Duration (Days)', required=True)
    notes = fields.Text(string='Instruction/Notes')
