from frappe import _


def get_data():
    return {
        "fieldname": "sla",
        "transactions": [{"label": _("OD Ticket"), "items": ["OD Ticket"]}],
    }
