import frappe


def execute():
    QBTicket = frappe.qb.DocType("OD Ticket")
    frappe.qb.update(QBTicket).set(
        QBTicket.service_level_agreement_creation, QBTicket.creation
    ).where(QBTicket.service_level_agreement_creation.isnull()).run()
