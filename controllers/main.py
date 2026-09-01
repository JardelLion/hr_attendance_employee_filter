from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.http import request
from odoo import http, _
from odoo.fields import Domain
from odoo.exceptions import UserError
from odoo.tools.image import image_data_uri
from odoo.service.common import exp_version
from odoo.tools import py_to_js_locale

class HrAttendanceInherit(HrAttendance):

    @http.route('/hr_attendance/employees_infos', type="jsonrpc", auth="public")
    def employees_infos(self, token, limit, offset, domain):
        for condition in domain:
            if not isinstance(condition, (list, tuple)) or len(condition) != 3:
                continue
            field_name, operator, _value = condition  # Force '&' implicit syntax
            if field_name not in ('name', 'department_id') or operator not in ('=', 'ilike'):
                raise UserError(_(
            "Invalid domain, use 'name' and/or 'department_id' fields "
            "with '=' and/or 'ilike' operators.",
        ))

        company = self._get_company(token)
        if company:
            domain = Domain(domain) & Domain('company_id', '=', company.id) & Domain('use_attendance', '=', True)
            employees = request.env['hr.employee'].sudo().search_fetch(domain, ['id', 'display_name', 'job_id'],
            limit=limit, offset=offset, order="name, id")
            employees_data = [{
                'id': employee.id,
                'display_name': employee.display_name,
                'job_id': employee.job_id.name,
                'avatar': image_data_uri(employee.avatar_128),
                'status': employee.attendance_state,
                'mode': employee.last_attendance_id.in_mode
            } for employee in employees]
            return {'records': employees_data, 'length': request.env['hr.employee'].sudo().search_count(domain)}
        return []
    

    @http.route(["/hr_attendance/<token>"], type='http', auth='public', website=True, sitemap=True)
    def open_kiosk_mode(self, token, from_trial_mode=False):
        company = self._get_company(token)
        if not company:
            return request.not_found()
        else:
            # department_list = [
            #     {"id": dep["id"], "name": dep["name"], "count": dep["total_employee"]}
            #     for dep in request.env["hr.department"]
            #     .with_context(allowed_company_ids=[company.id])
            #     .sudo()
            #     .search_read(
            #         domain=[("company_id", "=", company.id)],
            #         fields=["id", "name", "total_employee"],
            #     )
            # ]
            departments = request.env["hr.department"].with_context(
                allowed_company_ids=[company.id]
            ).sudo().search([
                ("company_id", "=", company.id),
            ])

            department_list = []

            for department in departments:
                count = request.env["hr.employee"].sudo().search_count([
                    ("company_id", "=", company.id),
                    ("department_id", "=", department.id),
                    ("use_attendance", "=", True),
                ])
                if count > 0:
                    department_list.append({
                        "id": department.id,
                        "name": department.name,
                        "count": count,
                    })


            has_password = self.has_password()
            if not from_trial_mode and has_password:
                request.session.logout(keep_db=True)
                if (from_trial_mode or (not has_password and not request.env.user.is_public)):
                    kiosk_mode = "settings"
                else:
                    kiosk_mode = company.attendance_kiosk_mode
                    version_info = exp_version()
                    return request.render(
                'hr_attendance.public_kiosk_mode',
                {
                    'kiosk_backend_info': {
                        'token': token,
                        'company_id': company.id,
                        'company_name': company.name,
                        'departments': department_list,
                        'kiosk_mode': kiosk_mode,
                        'from_trial_mode': from_trial_mode,
                        'barcode_source': company.attendance_barcode_source,
                        'device_tracking_enabled': company.attendance_device_tracking,
                        'lang': py_to_js_locale(company.partner_id.lang or company.env.lang),
                        'server_version_info': version_info.get('server_version_info'),
                    },
                }
            )