"""Flip the doctype labels beside preserved comment names.

Reaction child rows, File attachments, and the Attachment comment frappe
stamps beside each file already point at the right names; only the doctype
label flips. parentfield stays ``reactions`` because the custom field on
Comment reuses the same fieldname.

``Deleted`` comments keep their old label: they are tombstones for comments
removed long before the migration, so nothing recreates their target and
relabelling would claim a Comment that will never exist.
"""

import frappe


def execute():
    frappe.db.set_value(
        "OD Comment Reaction",
        {"parenttype": "OD Ticket Comment"},
        "parenttype",
        "Comment",
        update_modified=False,
    )
    frappe.db.set_value(
        "File",
        {"attached_to_doctype": "OD Ticket Comment"},
        "attached_to_doctype",
        "Comment",
        update_modified=False,
    )
    frappe.db.set_value(
        "Comment",
        {
            "reference_doctype": "OD Ticket Comment",
            "comment_type": ["in", ["Attachment", "Attachment Removed"]],
        },
        "reference_doctype",
        "Comment",
        update_modified=False,
    )
