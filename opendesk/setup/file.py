import frappe


def create_opendesk_folder():
    f = frappe.new_doc("File")
    f.file_name = "Opendesk"
    f.is_folder = 1
    f.folder = "Home"
    f.insert(ignore_if_duplicate=True)
