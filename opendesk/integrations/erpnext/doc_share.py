import frappe
from frappe.model.document import Document

from opendesk.integrations.erpnext import mirror_sync
from opendesk.integrations.erpnext.utils import should_sync

# Keeps OD Customer / ERPNext Customer DocShares mirrored bidirectionally when
# the integration is enabled.


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
        "doctype_field": "share_doctype",
        "value_field": "share_name",
        "extra_flags": _extra_flags,
    }


def _extra_flags(mirror: Document):
    mirror.flags.ignore_share_permission = True


def sync_shared_docs():
    """Bulk-sync DocShares between OD Customer and Customer. Idempotent — safe
    to call repeatedly. Used by the ERPNext settings 'Sync Customers' action."""
    if not should_sync():
        return

    od_customer_shares = frappe.get_list(
        "DocShare",
        filters={"share_doctype": "OD Customer"},
        fields=["*"],
    )
    erpnext_customer_shares = frappe.get_list(
        "DocShare",
        filters={"share_doctype": "Customer"},
        fields=["*"],
    )

    existing_od_shares = {(s.user, s.share_name) for s in od_customer_shares}
    existing_erp_shares = {(s.user, s.share_name) for s in erpnext_customer_shares}

    # ERP → OD
    for share in erpnext_customer_shares:
        od_customer = frappe.db.get_value("Customer", share.share_name, "od_customer")
        if not od_customer:
            continue
        if (share.user, od_customer) in existing_od_shares:
            continue
        doc = frappe.get_doc(
            {
                **share,
                "doctype": "DocShare",
                "share_doctype": "OD Customer",
                "share_name": od_customer,
            }
        )
        doc.flags.ignore_share_permission = True
        doc.flags.ignore_erpnext_sync = True
        doc.insert(ignore_permissions=True)
        existing_od_shares.add((share.user, od_customer))

    # OD → ERP
    for share in od_customer_shares:
        erpnext_customer = frappe.db.get_value(
            "OD Customer", share.share_name, "erpnext_customer"
        )
        if not erpnext_customer:
            continue
        if (share.user, erpnext_customer) in existing_erp_shares:
            continue
        doc = frappe.get_doc(
            {
                **share,
                "doctype": "DocShare",
                "share_doctype": "Customer",
                "share_name": erpnext_customer,
            }
        )
        doc.flags.ignore_share_permission = True
        doc.flags.ignore_erpnext_sync = True
        doc.insert(ignore_permissions=True)
        existing_erp_shares.add((share.user, erpnext_customer))
