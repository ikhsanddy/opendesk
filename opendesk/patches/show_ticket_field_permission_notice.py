import frappe


def execute():
    """Tell existing sites' managers that ticket fields now follow permission levels.

    Fresh sites never run this patch, so they never see the notice.
    """
    if frappe.db.count("OD Ticket"):
        frappe.db.set_single_value(
            "OD Settings", "show_ticket_field_permission_notice", 1
        )
