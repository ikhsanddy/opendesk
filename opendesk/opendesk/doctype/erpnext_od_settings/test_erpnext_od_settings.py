# Copyright (c) 2026, Frappe Technologies and contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestERPNextODSettings(FrappeTestCase):
    """
    Integration tests for ERPNextODSettings.
    Use this class for testing interactions between multiple components.
    """

    @patch("frappe.get_installed_apps", return_value=["frappe", "opendesk", "erpnext"])
    def test_validate_with_erpnext_installed(self, mock_get_installed_apps):
        settings_doc = frappe.get_single("ERPNext OD Settings")
        settings_doc.enabled = 1
        try:
            settings_doc.save()
        except Exception as e:
            self.fail(f"Validation failed when ERPNext is installed: {e}")
