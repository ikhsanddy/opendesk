import frappe

from opendesk.consts import DEFAULT_ARTICLE_CATEGORY


def execute():
    default_category = frappe.db.exists(
        "OD Article Category", {"category_name": DEFAULT_ARTICLE_CATEGORY}
    )
    if not default_category:
        default_category = frappe.get_doc(
            {
                "doctype": "OD Article Category",
                "category_name": DEFAULT_ARTICLE_CATEGORY,
            }
        ).insert()
        default_category = default_category.get("name")

    articles = frappe.get_all("OD Article", filters={"category": ""}, pluck="name")
    # create one default article for general category
    if len(articles) == 0:
        frappe.new_doc(
            "OD Article", title="New Article", category=default_category
        ).insert()
    else:
        for article in articles:
            frappe.db.set_value("OD Article", article, "category", default_category)
