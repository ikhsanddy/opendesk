import frappe

from opendesk.opendesk.doctype.od_article.od_article import get_excerpt


def execute():
    for article in frappe.get_all("OD Article", fields=["name", "content"]):
        frappe.db.set_value(
            "OD Article",
            article.name,
            "excerpt",
            get_excerpt(article.content),
            update_modified=False,
        )
