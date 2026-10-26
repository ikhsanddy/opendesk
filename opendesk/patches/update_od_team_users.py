import frappe


def execute():
    teams = frappe.get_all("OD Team", pluck="name")
    for team in teams:
        existing_agents = frappe.get_all(
            "OD Team Item", filters={"team": team}, pluck="parent"
        )  # agents in OD Agent doctype
        team_users = frappe.get_all(
            "OD Team Member", filters={"parent": team}, pluck="user"
        )  # agents in OD Team doctype

        for agent in existing_agents:
            is_agent_active = frappe.get_value("OD Agent", agent, "is_active")
            if is_agent_active and agent not in team_users:
                team_doc = (
                    frappe.get_doc("OD Team", team)
                    .append("users", {"user": agent})
                    .save()
                )
                print("Agent Added")
