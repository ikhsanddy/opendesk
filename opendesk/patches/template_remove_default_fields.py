import frappe
from frappe.query_builder import Case


def execute():
    QBDocField = frappe.qb.DocType("OD Ticket Template DocField")
    case = Case.any(
        [QBDocField.fieldname == "Subject", QBDocField.fieldname == "Description"]
    )
    frappe.qb.from_(QBDocField).delete().where(case).run()
    frappe.db.commit()
