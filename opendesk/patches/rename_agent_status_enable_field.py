from frappe.model.utils.rename_field import rename_field


def execute():
    """Rename enable to enabled to match OD Ticket Status. Skips if the old
    column is already gone."""
    rename_field("OD Agent Status", "enable", "enabled")
