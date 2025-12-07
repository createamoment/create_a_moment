// Copyright (c) 2021, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.views.calendar['Trip Event'] = {
    fields: ["date", "name", "title", "all_day", "color"],
    field_map: {
        'start': 'date',
        'end': 'date',
        'id': 'name',
        'allDay': 'all_day',
        'title': 'title',
        'color': 'color'
    },
    order_by: 'starts_on',
    get_events_method: 'frappe.desk.calendar.get_events'
}