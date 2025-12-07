# Copyright (c) 2021, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TripEvent(Document):
	def before_validate(self):
		if self.trip:
			self.owner = frappe.db.get_value("Trip", self.trip, "owner")

		self.bank_location = "" if self.bank_location == "0" else self.bank_location

	def validate(self):
		trip_event = frappe.get_value(
			"Trip Event",
			{
				"event_type": self.event_type,
				"trip": self.trip,
			},
			"name",
		)
		if self.trip and trip_event and self.name != trip_event:
			frappe.throw(_("Duplicate Trip Event"))

	def before_save(self):
		self.title = f"{self.customer}\n{str(self.time)[:-3] + ' ' if self.time else ''}{self.event_type}"
		self.cleanup_trip_event()
		self.set_color()

	def on_update(self):
		self.set_trip_event()

	def set_trip_event(self):
		trip_event_mapping = {
			"Prep Call": "prep_call",
			"Arrival": "arrival",
			"Bank Account Opening": "bank_account_opening",
			"Free Walking Tour": "free_walking_tour",
			"Camper Pick Up": "camper_pick_up",
		}

		if self.trip:
			set_trip_value(
				self.trip, trip_event_mapping.get(self.event_type), self.name
			)

		if (
			self._doc_before_save
			and self._doc_before_save.trip
			and self._doc_before_save.trip != self.trip
		):
			set_trip_value(
				self._doc_before_save.trip,
				trip_event_mapping.get(self.event_type),
				None,
			)

	def cleanup_trip_event(self):
		mapping = {"trip": ["country", "customer"]}

		for item in mapping.items():
			if not getattr(self, item[0]):
				for i in item[1]:
					setattr(self, i, None)

	def set_color(self):
		color_mapping = {
			"Prep Call": "#b9b8fa",
			"Arrival": "#fdae8c",
			"Bank Account Opening": "#fca4a4",
			"Free Walking Tour": "#82c49b",
			"Camper Pick Up": "#7cbcf5",
		}

		self.color = color_mapping[self.event_type]


def set_trip_value(trip_name, key, value):
	trip = frappe.get_doc("Trip", trip_name)
	setattr(trip, key, value)
	trip.save(ignore_permissions=True)
