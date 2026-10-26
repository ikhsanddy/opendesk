import frappe


def execute():
    for ticket in frappe.get_all("OD Ticket", ["name", "first_responded_on"]):
        first_communication_creation = frappe.db.get_value(
            "Communication",
            filters={
                "reference_doctype": "OD Ticket",
                "reference_name": ticket.name,
                "sent_or_received": "Sent",
            },
            order_by="creation asc",
            fieldname="creation",
        )
        if not first_communication_creation or (
            ticket.first_responded_on
            and first_communication_creation >= ticket.first_responded_on
        ):
            # Already set correctly, or no communication found.
            continue

        ticket = frappe.get_doc("OD Ticket", ticket.name)
        modified = ticket.modified
        ticket.first_responded_on = first_communication_creation
        ticket.save()
        ticket.db_set("modified", modified, update_modified=False)
        frappe.db.commit()
