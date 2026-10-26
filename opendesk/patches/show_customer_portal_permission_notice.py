import frappe


def execute():
    """Enable the one-time customer portal permission change notice.

    Only sites migrated by ``move_contact_dynamic_link_to_od_customer`` are
    affected: their contacts became plain customer members (not managers)
    and lost visibility of their customer's other tickets. Fresh sites with
    no such members never see the notice.
    """
    if frappe.db.exists("OD Customer Member", {"is_manager": 0}):
        frappe.db.set_single_value(
            "OD Settings", "show_customer_portal_permission_notice", 1
        )
