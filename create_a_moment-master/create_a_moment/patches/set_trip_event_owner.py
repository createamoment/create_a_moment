import frappe


def execute():
	for trip_event in frappe.get_all("Trip Event", pluck="name"):
		trip_event_doc = frappe.get_doc("Trip Event", trip_event)
		trip_event_doc.before_validate()
		trip_event_doc.save()
