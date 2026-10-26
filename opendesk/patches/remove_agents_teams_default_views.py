import frappe


def execute():
    print("Removing default views of agents")
    frappe.db.delete("OD View", {"dt": "OD Agent"})
    print("Removed default views of agents")
    print("--------------------")
    print("Removing default views of teams")
    frappe.db.delete("OD View", {"dt": "OD Team"})
    print("Removed default views of teams")
