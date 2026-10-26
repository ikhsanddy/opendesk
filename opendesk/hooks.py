app_name = "opendesk"
app_title = "Opendesk"
app_publisher = "Opendesk"
app_description = "Open Source Customer Service Software"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "ikhsanddy@users.noreply.github.com"
app_license = "AGPLv3"
# As org/app, so `bench get-app opendesk` fetches whichever is missing.
required_apps = ["frappe/telephony"]
require_type_annotated_api_methods = True

add_to_apps_screen = [
    {
        "name": "opendesk",
        "logo": "/assets/opendesk/desk/favicon.svg",
        "title": "Opendesk",
        "route": "/opendesk",
        "has_permission": "opendesk.api.permission.has_app_permission",
    }
]

get_site_info = "opendesk.activation.get_site_info"

after_install = "opendesk.setup.install.after_install"
before_uninstall = "opendesk.setup.install.before_uninstall"
after_migrate = [
    "opendesk.search.build_index_in_background",
    "opendesk.search.download_corpus",
]


# Full Text Search
# ------------------

sqlite_search = [
    "opendesk.search_sqlite.OpendeskSearch",
]

scheduler_events = {
    "all": [
        "opendesk.search.build_index_if_not_exists",
        "opendesk.search.download_corpus",
    ],
    "daily": [
        "opendesk.opendesk.doctype.od_ticket.od_ticket.close_tickets_after_n_days"
    ],
    "hourly_long": [
        "opendesk.opendesk.doctype.od_ticket.od_ticket.update_sla_status_in_ticket"
    ],
}


website_route_rules = [
    {
        "from_route": "/opendesk/<path:app_path>",
        "to_route": "opendesk",
    },
]

# Ticket emails and the new ticket form lived here before they moved under my-tickets.
website_redirects = [
    {
        "source": r"/help/tickets/(.+)",
        "target": r"/help/my-tickets/\1",
        "forward_query_parameters": True,
    },
]

user_invitation = {
    "allowed_roles": {
        "Agent Manager": [
            "Agent",
            "Agent Manager",
            "OD Customer",
            "OD Customer Manager",
        ],
        "System Manager": [
            "Agent",
            "Agent Manager",
            "System Manager",
            "OD Customer",
            "OD Customer Manager",
        ],
    },
    "after_accept": "opendesk.opendesk.hooks.user_invitation.after_accept",
    "extra_invite_params": ["customer", "contact"],
}

studio_app_boot = {"opendesk": "opendesk.opendesk.hooks.studio_app.get_boot"}
update_website_context = "opendesk.opendesk.hooks.studio_app.update_website_context"

doc_events = {
    "Assignment Rule": {
        "on_trash": "opendesk.extends.assignment_rule.on_assignment_rule_trash",
        "validate": "opendesk.extends.assignment_rule.on_assignment_rule_validate",
    },
    "Customer": {
        "after_insert": "opendesk.integrations.erpnext.customer.after_insert",
        "on_update": "opendesk.integrations.erpnext.customer.on_update",
        "before_rename": "opendesk.integrations.erpnext.customer.before_rename",
        "after_rename": "opendesk.integrations.erpnext.customer.after_rename",
        "on_trash": "opendesk.integrations.erpnext.customer.on_trash",
    },
    "User Permission": {
        "before_validate": "opendesk.integrations.erpnext.user_permission.before_validate",
        "after_insert": "opendesk.integrations.erpnext.user_permission.after_insert",
        "on_update": "opendesk.integrations.erpnext.user_permission.on_update",
        "on_trash": "opendesk.integrations.erpnext.user_permission.on_trash",
    },
    "DocShare": {
        "before_validate": "opendesk.integrations.erpnext.doc_share.before_validate",
        "after_insert": "opendesk.integrations.erpnext.doc_share.after_insert",
        "on_update": "opendesk.integrations.erpnext.doc_share.on_update",
        "on_trash": "opendesk.integrations.erpnext.doc_share.on_trash",
    },
    "Notification Log": {
        "before_insert": "opendesk.extends.notification_log.before_insert",
    },
    "Comment": {
        "before_insert": "opendesk.extends.comment.before_insert",
        "validate": "opendesk.extends.comment.validate",
        "on_trash": "opendesk.extends.comment.on_trash",
    },
    "ToDo": {
        "on_update": "opendesk.opendesk.doctype.od_ticket.od_ticket.publish_assignment_update",
    },
}

# For List View
permission_query_conditions = {
    "OD Ticket": "opendesk.opendesk.doctype.od_ticket.od_ticket.permission_query",
    "OD Article": "opendesk.opendesk.doctype.od_article.od_article.permission_query",
    "OD Article Category": "opendesk.opendesk.doctype.od_article_category.od_article_category.permission_query",
    "OD Saved Reply": "opendesk.opendesk.doctype.od_saved_reply.od_saved_reply.permission_query",
    "OD Customer": "opendesk.opendesk.doctype.od_customer.od_customer.permission_query",
}


has_permission = {
    "OD Agent": "opendesk.opendesk.doctype.od_agent.od_agent.has_permission",
    "OD Ticket": "opendesk.opendesk.doctype.od_ticket.od_ticket.has_permission",
    "OD Article": "opendesk.opendesk.doctype.od_article.od_article.has_permission",
    "OD Article Category": "opendesk.opendesk.doctype.od_article_category.od_article_category.has_permission",
    "OD Saved Reply": "opendesk.opendesk.doctype.od_saved_reply.od_saved_reply.has_permission",
    "OD Customer": "opendesk.opendesk.doctype.od_customer.od_customer.has_permission",
    "Comment": "opendesk.extends.comment.has_permission",
}

override_whitelisted_methods = {
    "frappe.realtime.has_permission": "opendesk.overrides.realtime.has_permission",
    "frappe.desk.form.activity.get_activity_timeline": "opendesk.overrides.activity.get_activity_timeline",
    "frappe.desk.form.activity.get_more_email_activities": "opendesk.overrides.activity.get_more_email_activities",
    "frappe.desk.form.load.getdoc": "opendesk.overrides.activity.getdoc",
    "frappe.desk.form.load.get_docinfo": "opendesk.overrides.activity.get_docinfo",
    "frappe.desk.form.load.get_communications": "opendesk.overrides.activity.get_communications",
}

# The article search index; frappe.clear_cache() would otherwise empty it until the next rebuild
persistent_cache_keys = ["search_doc:*", "search_doc_sections:*"]

notification_skip_email_types = [
    "Reaction",
    "Ticket Reopened",
]


# DocType Class
# ---------------
# Override standard doctype classes
override_doctype_class = {
    "Email Account": "opendesk.overrides.email_account.CustomEmailAccount",
    "Assignment Rule": "opendesk.overrides.assignment_rule.OpendeskAssignmentRule",
    "User Invitation": "opendesk.overrides.user_invitation.OpendeskUserInvitation",
}

ignore_links_on_delete = [
    "OD Notification",
    "OD Ticket Comment",
]

# setup wizard
# setup_wizard_requires = "assets/opendesk/js/setup_wizard.js"
# setup_wizard_stages = "opendesk.setup.setup_wizard.get_setup_stages"
setup_wizard_complete = "opendesk.setup.setup_wizard.setup_complete"


# Testing
# ---------------

before_tests = "opendesk.test_utils.before_tests"
auth_hooks = ["opendesk.auth.authenticate"]
