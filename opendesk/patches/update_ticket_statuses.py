import frappe

from opendesk.setup.install import add_default_status


def execute():
    add_default_status()

    if frappe.db.get_single_value("OD Settings", "auto_update_status"):
        frappe.db.set_single_value("OD Settings", "update_status_to", "Replied")

    frappe.db.set_single_value("OD Settings", "default_ticket_status", "Open")
    frappe.db.set_single_value("OD Settings", "ticket_reopen_status", "Open")
    if frappe.db.get_single_value("OD Settings", "auto_close_tickets"):
        frappe.db.set_single_value("OD Settings", "auto_close_status", "Replied")

    frappe.db.sql("DELETE FROM `tabOD Pause Service Level Agreement On Status`")
    frappe.db.sql("DELETE FROM `tabOD Service Level Agreement Fulfilled On Status`")
