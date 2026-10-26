import frappe


def get_site_info(site_info):
    # called via hook
    return {"activation": get_sales_data(site_info)}


def get_sales_data(site_info):
    activation_level = site_info.get("activation", {}).get("activation_level", 0)
    sales_data = site_info.get("activation", {}).get("sales_data", [])
    doctypes = [
        "OD Ticket",
        "Communication",
        "OD Saved Reply",
        "OD Service Level Agreement",
        "OD Form Script",
        "OD Article",
        "OD Customer",
        "OD Team",
    ]

    for doctype in doctypes:
        count = frappe.db.count(doctype)
        sales_data.append({doctype: count})

    # ticket comments live in core Comment now; keep the historical key
    sales_data.append(
        {
            "OD Ticket Comment": frappe.db.count(
                "Comment",
                {"reference_doctype": "OD Ticket", "comment_type": "Comment"},
            )
        }
    )

    return {"activation_level": activation_level, "sales_data": sales_data}
