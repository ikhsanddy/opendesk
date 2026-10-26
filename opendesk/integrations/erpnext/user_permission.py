import frappe
from frappe.model.document import Document
from frappe.utils import cstr

from opendesk.integrations.erpnext import mirror_sync
from opendesk.integrations.erpnext.utils import should_sync

# Keeps OD Customer / ERPNext Customer User Permissions mirrored bidirectionally
# when the integration is enabled.


def before_validate(doc: Document, method: str | None = None):
    mirror_sync.before_validate(doc, _config())


def after_insert(doc: Document, method: str | None = None):
    mirror_sync.after_insert(doc, _config())


def on_update(doc: Document, method: str | None = None):
    mirror_sync.on_update(doc, _config())


def on_trash(doc: Document, method: str | None = None):
    mirror_sync.on_trash(doc, _config())


def _config() -> dict:
    return {
        "user_field": "user",
        "doctype_field": "allow",
        "value_field": "for_value",
        "extra_dedup_keys": _extra_dedup_keys,
    }


def _extra_dedup_keys(doc: Document) -> dict:
    # Frappe's validate_user_permission() dedups on these 5 keys; mirror that
    # here so we don't insert a row the parent's validate() would reject as a
    # duplicate.
    return {
        "applicable_for": cstr(doc.applicable_for),
        "apply_to_all_doctypes": doc.apply_to_all_doctypes,
    }


def sync_user_permissions():
    """Bulk-sync User Permissions between OD Customer and Customer. Idempotent."""
    if not should_sync():
        return

    od_customer_user_perms = frappe.get_list(
        "User Permission",
        filters={"allow": "OD Customer"},
        fields=["*"],
    )
    erpnext_customer_user_perms = frappe.get_list(
        "User Permission",
        filters={"allow": "Customer"},
        fields=["*"],
    )

    existing_od_perms = {(p.user, p.for_value) for p in od_customer_user_perms}
    existing_erp_perms = {(p.user, p.for_value) for p in erpnext_customer_user_perms}

    # ERP → OD
    for perm in erpnext_customer_user_perms:
        od_customer = frappe.db.get_value("Customer", perm.for_value, "od_customer")
        if not od_customer:
            continue
        if (perm.user, od_customer) in existing_od_perms:
            continue
        doc = frappe.get_doc(
            {
                **perm,
                "doctype": "User Permission",
                "allow": "OD Customer",
                "for_value": od_customer,
            }
        )
        doc.flags.ignore_erpnext_sync = True
        doc.insert(ignore_permissions=True)
        existing_od_perms.add((perm.user, od_customer))

    # OD → ERP
    for perm in od_customer_user_perms:
        erpnext_customer = frappe.db.get_value(
            "OD Customer", perm.for_value, "erpnext_customer"
        )
        if not erpnext_customer:
            continue
        if (perm.user, erpnext_customer) in existing_erp_perms:
            continue
        doc = frappe.get_doc(
            {
                **perm,
                "doctype": "User Permission",
                "allow": "Customer",
                "for_value": erpnext_customer,
            }
        )
        doc.flags.ignore_erpnext_sync = True
        doc.insert(ignore_permissions=True)
        existing_erp_perms.add((perm.user, erpnext_customer))
