import frappe


def execute():
    """The color Select on OD Ticket Status shipped with a lowercase "purple"
    option, which misses every capitalized colorMap lookup on the frontend."""
    frappe.db.set_value(
        "OD Ticket Status",
        {"color": "purple"},
        "color",
        "Purple",
        update_modified=False,
    )
