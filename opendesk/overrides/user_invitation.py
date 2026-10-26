import frappe
from frappe import _
from frappe.core.doctype.user_invitation.user_invitation import UserInvitation

from opendesk.opendesk.doctype.od_customer.od_customer import (
    CUSTOMER_ROLES,
    is_customer_manager,
)


class OpendeskUserInvitation(UserInvitation):
    def validate_invite(self) -> None:
        """Lets a batch refuse before `insert` mails anyone."""
        self._validate_invite()

    def _get_allowed_roles(self):
        allowed_roles = super()._get_allowed_roles()
        if self.app_name == "opendesk" and self._is_from_a_customer_manager():
            allowed_roles.extend(CUSTOMER_ROLES)
        return allowed_roles

    def _is_from_a_customer_manager(self) -> bool:
        return frappe.db.get_single_value(
            "OD Settings", "allow_customer_managers_to_invite"
        ) and is_customer_manager(self.customer)

    def _get_email_title(self):
        # Use the org's brand name (set during onboarding) in the invitation
        # subject — "You've been invited to join <brand> on Opendesk" — falling
        # back to the framework app title when it isn't set. The override class
        # is registered site-wide, so invitations from other apps (ERPNext,
        # etc.) must keep their own app title.
        if self.app_name != "opendesk":
            return super()._get_email_title()
        brand = frappe.db.get_single_value("OD Settings", "brand_name")
        if not brand:
            return super()._get_email_title()
        return _("{0} on {1}").format(brand, super()._get_email_title())
