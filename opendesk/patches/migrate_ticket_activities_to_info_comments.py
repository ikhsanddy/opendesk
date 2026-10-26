"""Migrate to Info comments the OD Ticket Activity rows whose only copy is that table.

Tag changes, auto-close reasons, and split markers never saved the ticket, so
no Version row exists; they become backdated Info comments. Field-change rows
stay behind by design: Version rows (track_changes since 2019) already cover
them, and migrating both would double every status change in the feed.
"""

import frappe
from pypika import Criterion
from pypika.terms import ExistsCriterion, ValueWrapper

from opendesk.patches.utils import iter_name_chunks

MIGRATED_ACTION_PREFIXES = [
    "added tag%",
    "removed tag%",
    "automatically closed%",
    "split the ticket%",
]


def execute():
    # chunk over the whole table; the prefix filter lives in the insert-select
    for lower, upper in iter_name_chunks("OD Ticket Activity"):
        copy_chunk(lower, upper)
        frappe.db.commit()  # nosemgrep: sanctioned patch idiom, resumable chunks
    resolve_name_collisions()


def copy_chunk(lower: str, upper: str) -> None:
    ODTicketActivity = frappe.qb.DocType("OD Ticket Activity")  # source
    Comment = frappe.qb.DocType("Comment")  # target
    existing = (
        frappe.qb.from_(Comment)
        .select(Comment.name)
        .where(Comment.name == ODTicketActivity.name)
    )
    (
        frappe.qb.into(Comment)
        .columns(
            "name",
            "creation",
            "modified",
            "modified_by",
            "owner",
            "docstatus",
            "comment_type",
            "comment_email",
            "content",
            "reference_doctype",
            "reference_name",
        )
        .from_(ODTicketActivity)
        .select(
            ODTicketActivity.name,
            ODTicketActivity.creation,
            ODTicketActivity.modified,
            ODTicketActivity.modified_by,
            ODTicketActivity.owner,
            ValueWrapper(0),
            ValueWrapper("Info"),
            ODTicketActivity.owner,
            ODTicketActivity.action,
            ValueWrapper("OD Ticket"),
            ODTicketActivity.ticket,
        )
        .where(ODTicketActivity.name > lower)
        .where(ODTicketActivity.name <= upper)
        .where(migrated_actions_criterion(ODTicketActivity))
        .where(ExistsCriterion(existing).negate())
        .run()
    )


def migrated_actions_criterion(ODTicketActivity) -> Criterion:
    return Criterion.any(
        ODTicketActivity.action.like(prefix) for prefix in MIGRATED_ACTION_PREFIXES
    )


def resolve_name_collisions() -> None:
    """Activity and comment names come from the same hash space, so a migrated
    row's name may already belong to a migrated comment. Same twin check as
    the comments patch; nothing external links activity names, so a fresh
    name is enough."""
    ODTicketActivity = frappe.qb.DocType("OD Ticket Activity")  # source
    Comment = frappe.qb.DocType("Comment")  # target
    Twin = frappe.qb.DocType("Comment").as_("twin")  # migrated copy
    already_migrated = (
        frappe.qb.from_(Twin)
        .select(Twin.name)
        .where(Twin.creation == ODTicketActivity.creation)
        .where(Twin.reference_doctype == "OD Ticket")
        .where(Twin.comment_type == "Info")
        .where(Twin.owner == ODTicketActivity.owner)
    )
    collisions = (
        frappe.qb.from_(ODTicketActivity)
        .join(Comment)
        .on(Comment.name == ODTicketActivity.name)
        .select(ODTicketActivity.name)
        .where(migrated_actions_criterion(ODTicketActivity))
        .where(
            (Comment.creation != ODTicketActivity.creation)
            | (Comment.comment_type != "Info")
        )
        .where(ExistsCriterion(already_migrated).negate())
        .run(pluck=True)
    )
    for old_name in collisions:
        reinsert_with_fresh_name(old_name)


def reinsert_with_fresh_name(old_name: str) -> None:
    row = frappe.db.get_value(
        "OD Ticket Activity",
        old_name,
        ["creation", "modified", "modified_by", "owner", "action", "ticket"],
        as_dict=True,
    )
    Comment = frappe.qb.DocType("Comment")  # target
    new_name = frappe.generate_hash(length=10)
    (
        frappe.qb.into(Comment)
        .columns(
            "name",
            "creation",
            "modified",
            "modified_by",
            "owner",
            "docstatus",
            "comment_type",
            "comment_email",
            "content",
            "reference_doctype",
            "reference_name",
        )
        .insert(
            new_name,
            row.creation,
            row.modified,
            row.modified_by,
            row.owner,
            0,
            "Info",
            row.owner,
            row.action,
            "OD Ticket",
            row.ticket,
        )
        .run()
    )
    frappe.log_error(
        title="Activity migration rename",
        message=f"OD Ticket Activity {old_name} collided with an existing Comment; migrated as {new_name}",
    )
