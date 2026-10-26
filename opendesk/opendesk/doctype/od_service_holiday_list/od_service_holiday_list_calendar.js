// Copyright (c) 2015, Frappe Technologies and contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["OD Service Holiday List"] = {
  field_map: {
    start: "holiday_date",
    end: "holiday_date",
    id: "name",
    title: "description",
    allDay: "allDay",
  },
  order_by: `from_date`,
  get_events_method:
    "opendesk.opendesk.doctype.od_service_holiday_list.od_service_holiday_list.get_events",
  filters: [
    {
      fieldtype: "Link",
      fieldname: "holiday_list",
      options: "OD Service Holiday List",
      label: __("OD Service Holiday List"),
    },
  ],
};
