import frappe
from frappe import _

from opendesk.integrations.erpnext.doc_share import sync_shared_docs
from opendesk.integrations.erpnext.user_permission import sync_user_permissions
from opendesk.integrations.erpnext.utils import set_links, should_sync


@frappe.whitelist()
def get_sync_info() -> dict:
    """Drive the ERPNext integration settings UI. `in_sync` gates the 'Sync now'
    action. Whether ERPNext is installed is read on the frontend from the boot
    `apps` list, not from here."""
    if "erpnext" not in frappe.get_installed_apps():
        return {"enabled": False, "in_sync": False}

    if not frappe.has_permission("OD Customer", "read") or not frappe.has_permission(
        "Customer", "read"
    ):
        return {"enabled": False}

    enabled = bool(frappe.db.get_single_value("ERPNext OD Settings", "enabled"))
    if not enabled:
        return {"enabled": False}

    return {"enabled": enabled, "in_sync": in_sync()}


def in_sync() -> bool:
    """True when every OD Customer is linked to an ERP Customer and vice versa.
    Sync is a no-op in this state; the UI uses this to gate the 'Sync Customers'
    button.
    """
    if frappe.db.count("OD Customer", {"erpnext_customer": ["is", "not set"]}):
        return False
    if frappe.db.count("Customer", {"od_customer": ["is", "not set"]}):
        return False
    return True


@frappe.whitelist()
def sync_od_erpnext_customers() -> None:
    frappe.has_permission("Customer", "write", throw=True)
    frappe.has_permission("OD Customer", "write", throw=True)
    if not should_sync():
        frappe.throw(
            _("ERPNext integration is not enabled"), title=_("Cannot Sync Customers")
        )

    frappe.enqueue(
        sync_all_customers,
        queue="long",
        timeout=12000,
        job_id="sync_od_erpnext_customers",
        deduplicate=True,
    )


def sync_all_customers():
    """
    Union-merge OD Customers and ERPNext Customers.

    - Unlinked ERP customers are created or linked in OD Customer.
    - Unlinked OD customers are created or linked in ERP Customer.

    Matching is done by name. If a record with the same name exists on the
    other side but is unlinked, the two are linked instead of creating a duplicate.
    """
    frappe.publish_realtime(
        "opendesk:erpnext-sync-start",
        user=frappe.session.user,
    )

    # ERP → OD
    unlinked_erp = frappe.get_all(
        "Customer",
        filters={"od_customer": ["is", "not set"]},
        fields=["name", "customer_name", "image"],
    )
    for erp in unlinked_erp:
        existing_od = frappe.db.get_value(
            "OD Customer",
            {"name": erp.name, "erpnext_customer": ["is", "not set"]},
            "name",
        )
        if existing_od:
            set_links(erp.name, existing_od)
        elif not frappe.db.exists("OD Customer", erp.name):
            od_doc = frappe.get_doc(
                {
                    "doctype": "OD Customer",
                    "customer_name": erp.name,
                    "erpnext_customer": erp.name,
                    "image": erp.image,
                }
            )
            od_doc.flags.ignore_erpnext_sync = True
            od_doc.insert(ignore_permissions=True)
            set_links(erp.name, od_doc.name)

    # OD → ERP
    unlinked_od = frappe.get_all(
        "OD Customer",
        filters={"erpnext_customer": ["is", "not set"]},
        fields=["name", "customer_name", "image"],
    )
    for od in unlinked_od:
        existing_erp = frappe.db.get_value(
            "Customer",
            {"name": od.name, "od_customer": ["is", "not set"]},
            "name",
        )
        if existing_erp:
            set_links(existing_erp, od.name)
        elif not frappe.db.exists("Customer", od.name):
            erp_doc = frappe.get_doc(
                {
                    "doctype": "Customer",
                    "customer_name": od.customer_name,
                    "od_customer": od.name,
                    "image": od.image,
                }
            )
            erp_doc.flags.ignore_erpnext_sync = True
            erp_doc.insert(ignore_permissions=True)
            set_links(erp_doc.name, od.name)

    sync_user_permissions()
    sync_shared_docs()

    # after_commit so the frontend's get_sync_info reload sees the committed
    # links (in_sync = True) instead of pre-commit state. The job runs as the
    # triggering user (frappe.enqueue → set_user), so this reaches their room.
    frappe.publish_realtime(
        "opendesk:erpnext-sync-end",
        user=frappe.session.user,
        after_commit=True,
    )
