{
    "name": "HR Attendance Employee Filter",
    "version": "19.0.0",
    "category": "Human Resources/Attendances",
    "summary": "Filter employees displayed in Attendance and Kiosk Mode",
    "description": """
    HR Attendance Employee Filter
    =============================

    Allows HR users to define which employees participate in Odoo Attendance.

    Employees who do not use Attendance can remain active in Odoo while being
    excluded from Attendance-related employee lists and Kiosk Mode.
    """,
    "author": "Jardel Bernardo",
    "website": "https://github.com/jardellion/hr_attendance_employee_filter",
    "license": "LGPL-3",
    "depends": [
        "hr_attendance",
    ],
    "data": [
        "views/hr_employee_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "hr_attendance_employee_filter/static/src/..."
        ],
    },
    "installable": True,
    "application": False,
}