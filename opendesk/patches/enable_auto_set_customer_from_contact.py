import frappe


def execute():
    frappe.db.set_single_value(
        "OD Settings",
        "auto_set_customer_from_contact",
        1,
    )
