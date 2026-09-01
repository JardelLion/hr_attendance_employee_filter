from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    use_attendance = fields.Boolean(
    string="Use Attendance",
    default=True,
    help="If enabled, this employee is included in Attendance "
    "management and kiosk selection.",
)