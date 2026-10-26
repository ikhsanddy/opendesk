import frappe


def before_insert(doc, method=None):
    if doc.document_type == "OD Ticket" and doc.document_name:
        doc.link = frappe.utils.get_url("/opendesk/tickets/" + str(doc.document_name))
