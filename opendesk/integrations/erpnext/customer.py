import frappe
from frappe.model.document import Document

from opendesk.integrations.erpnext.utils import (
    cascade_rename,
    in_cascade,
    map_source_to_target_values,
    set_links,
    should_sync,
    sync_related_fields,
    validate_rename_conflict,
)


def after_insert(doc: Document, method: str | None = None):
    if not should_sync() or doc.flags.get("ignore_erpnext_sync"):
        return

    if frappe.db.exists("OD Customer", {"erpnext_customer": doc.name}):
        return

    od_doc = frappe.get_doc(
        {
            "doctype": "OD Customer",
            "customer_name": doc.customer_name,
            "erpnext_customer": doc.name,
            **map_source_to_target_values(doc),
        }
    )
    od_doc.flags.ignore_erpnext_sync = True
    od_doc.insert(ignore_permissions=True)
    set_links(doc.name, od_doc.name)


def on_update(doc: Document, method: str | None = None):
    if not should_sync() or doc.flags.get("ignore_erpnext_sync"):
        return

    sync_related_fields(doc)


def before_rename(
    doc: Document, method: str | None, olddn: str, newdn: str, merge: bool = False
):
    validate_rename_conflict("Customer", olddn, newdn, merge)


def after_rename(
    doc: Document, method: str | None, olddn: str, newdn: str, merge: bool = False
):
    cascade_rename("Customer", olddn, newdn, merge)


def on_trash(doc: Document, method: str | None = None):
    if in_cascade() or not should_sync():
        return

    od_customer = frappe.db.get_value(
        "OD Customer", {"erpnext_customer": doc.name}, "name"
    )
    if od_customer:
        # Clear the back-link first so OD Customer's on_trash won't try to
        # delete this Customer again (it's already being deleted).
        frappe.db.set_value("OD Customer", od_customer, "erpnext_customer", None)
        frappe.delete_doc("OD Customer", od_customer, ignore_permissions=True)
