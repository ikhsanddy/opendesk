"""OD Notification → core Notification Log, names preserved.

All rows migrate: nothing reaps Notification Log by default, so there is no
retention boundary that would make old rows pointless. Every row references
its ticket; mentions and reactions additionally carry their Comment as the
source (valid because the comments patch runs first), so a reader lands on
the exact comment. "Ticket Reopened" fixes the historical mislabel of reopen
notifications as "Reaction".
"""

import frappe
from frappe.query_builder.functions import Coalesce, Concat
from pypika import Case
from pypika.terms import ExistsCriterion, ValueWrapper

from opendesk.patches.utils import iter_name_chunks

NOTIFICATION_COLUMNS = [
    "name",
    "creation",
    "modified",
    "modified_by",
    "owner",
    "docstatus",
    "type",
    "document_type",
    "document_name",
    "source_doctype",
    "source_name",
    "for_user",
    "from_user",
    "read",
    "subject",
    "title",
    "app",
]


def execute():
    for lower, upper in iter_name_chunks("OD Notification"):
        copy_chunk(lower, upper)
        frappe.db.commit()  # nosemgrep: sanctioned patch idiom, resumable chunks
    resolve_name_collisions()
    frappe.clear_cache()


def copy_chunk(lower: str, upper: str) -> None:
    ODNotification = frappe.qb.DocType("OD Notification")  # source
    NotificationLog = frappe.qb.DocType("Notification Log")  # target
    User = frappe.qb.DocType("User")  # full_name lookup
    existing = (
        frappe.qb.from_(NotificationLog)
        .select(NotificationLog.name)
        .where(NotificationLog.name == ODNotification.name)
    )
    from_name = Coalesce(User.full_name, ODNotification.user_from)
    (
        frappe.qb.into(NotificationLog)
        .columns(*NOTIFICATION_COLUMNS)
        .from_(ODNotification)
        .left_join(User)
        .on(User.name == ODNotification.user_from)
        .select(
            ODNotification.name,
            ODNotification.creation,
            ODNotification.modified,
            ODNotification.modified_by,
            ODNotification.owner,
            ValueWrapper(0),
            get_notification_log_type_case(ODNotification),
            ValueWrapper("OD Ticket"),
            ODNotification.reference_ticket,
            get_source_doctype_case(ODNotification),
            ODNotification.reference_comment,
            ODNotification.user_to,
            ODNotification.user_from,
            ODNotification.read,
            get_subject_case(ODNotification, from_name),
            get_subject_case(ODNotification, from_name),
            ValueWrapper("opendesk"),
        )
        .where(ODNotification.name > lower)
        .where(ODNotification.name <= upper)
        .where(
            ExistsCriterion(existing).negate()
        )  # for each notification, only insert if it doesn't already exist in Notification Log, might have been migrated in a previous chunk or migrated in a previous run of the patch, and the patch failed for some reason, so we can resume the patch without duplicating notifications.
        .run()
    )


def get_notification_log_type_case(ODNotification) -> Case:
    return (
        Case()
        .when(ODNotification.notification_type == "Mention", "Mention")
        .when(ODNotification.notification_type == "Assignment", "Assignment")
        .when(
            (ODNotification.notification_type == "Reaction")
            & ODNotification.reference_comment.isnotnull(),
            "Reaction",
        )
        .else_("Ticket Reopened")
    )


def get_source_doctype_case(ODNotification) -> Case:
    return (
        Case().when(ODNotification.reference_comment.isnotnull(), "Comment").else_(None)
    )


def get_subject_case(ODNotification, from_name) -> Case:
    def about_ticket(verb: str):
        return Concat(
            from_name, ValueWrapper(verb + " ticket #"), ODNotification.reference_ticket
        )

    return (
        Case()
        .when(
            ODNotification.notification_type == "Mention",
            about_ticket(" mentioned you in"),
        )
        .when(
            ODNotification.notification_type == "Assignment",
            about_ticket(" assigned you"),
        )
        .when(
            (ODNotification.notification_type == "Reaction")
            & ODNotification.reference_comment.isnotnull(),
            Coalesce(ODNotification.message, ValueWrapper("reacted to your comment")),
        )
        .else_(about_ticket(" reopened"))
    )


def resolve_name_collisions() -> None:
    """Same twin check as the comments patch, on immutable creation. Nothing
    links notification names, so a fresh name is the whole fix."""
    ODNotification = frappe.qb.DocType("OD Notification")  # source
    NotificationLog = frappe.qb.DocType("Notification Log")  # target
    Twin = frappe.qb.DocType("Notification Log").as_("twin")  # migrated copy
    already_migrated = (
        frappe.qb.from_(Twin)
        .select(Twin.name)
        .where(Twin.creation == ODNotification.creation)
        .where(Twin.for_user == ODNotification.user_to)
        .where(Twin.app == "opendesk")
    )
    # Notification not migrated yet, but its name is already taken by a migrated notification with a different creation timestamp. Reinsert the old notification under a fresh name.
    collisions = (
        frappe.qb.from_(ODNotification)
        .join(NotificationLog)
        .on(NotificationLog.name == ODNotification.name)
        .select(ODNotification.name)
        .where(NotificationLog.creation != ODNotification.creation)
        .where(
            ExistsCriterion(already_migrated).negate()
        )  # filter out already migrated notifications
        .run(pluck=True)
    )
    for old_name in collisions:
        reinsert_with_fresh_name(old_name)


def reinsert_with_fresh_name(old_name: str) -> None:
    row = frappe.db.get_value(
        "OD Notification",
        old_name,
        [
            "creation",
            "modified",
            "modified_by",
            "owner",
            "notification_type",
            "reference_ticket",
            "reference_comment",
            "user_from",
            "user_to",
            "read",
            "message",
        ],
        as_dict=True,
    )
    is_reaction = row.notification_type == "Reaction" and row.reference_comment
    if row.notification_type in ("Mention", "Assignment"):
        notification_type = row.notification_type
    elif is_reaction:
        notification_type = "Reaction"
    else:
        notification_type = "Ticket Reopened"
    from_name = frappe.utils.get_fullname(row.user_from)
    subjects = {
        "Mention": f"{from_name} mentioned you in ticket #{row.reference_ticket}",
        "Assignment": f"{from_name} assigned you ticket #{row.reference_ticket}",
        "Reaction": row.message or "reacted to your comment",
        "Ticket Reopened": f"{from_name} reopened ticket #{row.reference_ticket}",
    }
    subject = subjects[notification_type]
    NotificationLog = frappe.qb.DocType("Notification Log")  # target
    (
        frappe.qb.into(NotificationLog)
        .columns(*NOTIFICATION_COLUMNS)
        .insert(
            frappe.generate_hash(length=10),
            row.creation,
            row.modified,
            row.modified_by,
            row.owner,
            0,
            notification_type,
            "OD Ticket",
            row.reference_ticket,
            "Comment" if row.reference_comment else None,
            row.reference_comment,
            row.user_to,
            row.user_from,
            row.read,
            subject,
            subject,
            "opendesk",
        )
        .run()
    )
