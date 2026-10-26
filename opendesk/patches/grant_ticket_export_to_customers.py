import frappe
from frappe.permissions import update_permission_property

from opendesk.patches.harden_od_ticket_field_permissions import CUSTOMER_ROLES


def execute():
    """Custom DocPerm rows override the JSON perms."""
    roles = frappe.get_all(
        "Custom DocPerm",
        filters={
            "parent": "OD Ticket",
            "permlevel": 0,
            "read": 1,
            "role": ["in", CUSTOMER_ROLES],
        },
        pluck="role",
    )
    for role in roles:
        update_permission_property("OD Ticket", role, 0, "export", 1, validate=False)
