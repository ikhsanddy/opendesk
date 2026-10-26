import json

import frappe

from opendesk.opendesk.doctype.od_form_script.od_form_script import get_form_script
from opendesk.ticket_fields import TicketFields
from opendesk.utils import check_permissions, get_customers, is_agent

DOCTYPE_TEMPLATE = "OD Ticket Template"


@frappe.whitelist()
def get_one(name: str):
    check_permissions(DOCTYPE_TEMPLATE, None)
    template = frappe.db.get_value(
        DOCTYPE_TEMPLATE, name, ["about", "description_template"], as_dict=True
    )
    if not template:
        return {"about": None, "fields": []}
    fields = TicketFields(name).get_form()
    if frappe.db.get_single_value("OD Settings", "auto_set_customer_from_contact"):
        set_customer_field(fields)

    return {
        "about": template.about,
        "fields": fields,
        "description_template": template.description_template,
        "_form_script": get_form_script(
            "OD Ticket", apply_on_new_page=True, is_customer_portal=False
        ),
    }


def set_customer_field(fields: list) -> None:
    """Scope the customer field to the session contact's own customers on the
    customer portal.

    Agents get the template's customer field untouched. Portal contacts get it
    filtered to their customers; when the template has no customer field and the
    contact belongs to multiple customers, a required field is injected so they
    can pick one. Selection is enforced server side in ODTicket.set_customer.
    """
    if is_agent():
        return

    customers = get_customers()
    link_filters = json.dumps([["OD Customer", "name", "in", list(customers)]])
    customer_field = next((f for f in fields if f.fieldname == "customer"), None)

    if customer_field:
        customer_field.link_filters = link_filters
        if len(customers) > 1:
            customer_field.required = 1
    elif len(customers) > 1:
        fields.append(
            frappe._dict(
                fieldname="customer",
                fieldtype="Link",
                label="Customer",
                options="OD Customer",
                link_filters=link_filters,
                required=1,
            )
        )
