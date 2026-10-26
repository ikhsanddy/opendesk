import frappe

from opendesk.opendesk.doctype.od_agent_status.od_agent_status import (
    get_default_agent_status,
)
from opendesk.setup.install import add_default_agent_status


def execute():
    """Add the default OD Agent Status records on sites that predate the feature,
    and set the Active status on existing agents whose availability is unset or invalid.
    """
    add_default_agent_status()

    default_status = get_default_agent_status()

    valid_statuses = frappe.get_all("OD Agent Status", pluck="name")
    agents = frappe.get_all(
        "OD Agent",
        or_filters=[
            ["availability", "is", "not set"],
            ["availability", "=", ""],
            ["availability", "not in", valid_statuses],
        ],
        pluck="name",
    )
    if agents:
        frappe.db.set_value(
            "OD Agent",
            {"name": ["in", agents]},
            "availability",
            default_status,
            update_modified=False,
        )
