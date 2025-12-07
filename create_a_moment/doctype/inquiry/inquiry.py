# -*- coding: utf-8 -*-
# Copyright (c) 2021, ALYF GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document


class Inquiry(Document):
	def validate(self):
		self.validate_inquiry_type_does_not_exist_for_trip()

	def validate_inquiry_type_does_not_exist_for_trip(self):
		inquiry = frappe.get_value(
			"Inquiry",
			{
				"inquiry_type": self.inquiry_type,
				"trip": self.trip,
				"status": ["!=", "Cancelled"],
			},
			"name",
		)

		if self.trip and inquiry and self.name != inquiry:
			frappe.throw(
				_("There is already a <b>{0}</b> Inquiry for Trip <b>{1}</b>.").format(
					self.inquiry_type, self.trip
				)
			)

	def before_insert(self):
		if self.new_user:
			try:
				self.create_user()
				self.create_customer()
				self.create_contact()
				self.create_trip()
				self.create_arrival_event()
			except:
				frappe.log_error(frappe.get_traceback(), "Inquiry processing failed")
				self.status = "Error"
			else:
				self.clear_new_user_date()
				self.status = "Processing"
		else:
			self.create_arrival_event()
			self.update_arrival_event()
			self.status = "Processing"

	def after_insert(self):
		if self.status != "Error":
			self.status = "Open"

		self.on_update()
		self.save(ignore_version=True)

	def on_update(self):
		self.owner = self.get_user()
		self.set_birthday()
		self.update_inquiry_link_in_trip(self.status == "Cancelled")

	def clear_new_user_date(self):
		self.new_user_country = None
		self.new_user_email = None
		self.new_user = 0

	def set_birthday(self):
		self.birthday = frappe.get_value("User", self.get_user(), "birth_date")

	def get_user(self):
		user = frappe.get_all(
			"Contact",
			filters=[
				["Dynamic Link", "link_doctype", "=", "Customer"],
				["Dynamic Link", "link_name", "=", self.customer],
			],
			pluck="user",
		)

		if len(user) != 1:
			# FIXME: Fehlerbehandlung
			pass

		return user[0]

	def create_user(self):
		doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": self.new_user_email,
				"first_name": self.new_user_first_name,
				"last_name": self.new_user_last_name,
				"birth_date": self.new_user_birthday,
				"mobile_no": self.new_user_mobile_no,
				"language": "de",
				"owner": self.new_user_email,
			}
		).insert(ignore_permissions=True)

		doc.add_roles("Customer")

	def create_customer(self):
		doc = frappe.get_doc(
			{
				"doctype": "Customer",
				"type": "Individual",
				"customer_group": "Individual",
				"territory": "All Territories",
				"title": f"{self.new_user_first_name} {self.new_user_last_name}",
				"customer_name": f"{self.new_user_first_name} {self.new_user_last_name}",
			}
		).insert(ignore_permissions=True)

		self.customer = doc.name

	def create_contact(self):
		contact = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": self.new_user_first_name,
				"last_name": self.new_user_last_name,
				"user": self.new_user_email,
			}
		)
		contact.append(
			"email_ids", {"email_id": self.new_user_email, "is_primary": True}
		)
		contact.append(
			"phone_nos",
			{
				"phone": self.new_user_mobile_no,
				"is_primary_mobile_no": True,
			},
		)
		contact.append(
			"links", {"link_doctype": "Customer", "link_name": self.customer}
		)

		contact.insert(ignore_permissions=True)

	def create_trip(self):
		trip = frappe.get_doc(
			{
				"doctype": "Trip",
				"trip_type": "Au Pair"
				if self.inquiry_type == "Au Pair"
				else "Working Holiday",
				"country": self.new_user_country,
				"customer": self.customer,
				"owner": self.new_user_email,
				"sales_partner": self.sales_partner,
			}
		)

		trip.insert(ignore_permissions=True)

		self.trip = trip.name

	def create_arrival_event(self):
		if self.new_user_arrival_date:
			trip_event = frappe.get_doc(
				{
					"doctype": "Trip Event",
					"event_type": "Arrival",
					"date": self.new_user_arrival_date,
					"time": "",
					"trip": self.trip,
				}
			)
			trip_event.insert(ignore_permissions=True)

			set_trip_value(self.trip, "arrival", trip_event.name)

	def update_arrival_event(self):
		if self.inquiry_type == "Starter Package Booking Form":
			arrival_event = frappe.get_doc(
				"Trip Event", frappe.get_value("Trip", self.trip, "arrival")
			)
			arrival_event.date = self.arrival_date
			arrival_event.time = self.arrival_time
			arrival_event.save(ignore_permissions=True)

	def update_inquiry_link_in_trip(self, unlink=False):
		inquiry_mapping = {
			"Starter Package": "starter_package_inquiry",
			"Starter Package Booking Form": "starter_package_booking_form",
			"Au Pair": "au_pair_inquiry",
			"Au Pair Booking Form": "au_pair_booking_form",
			"Flight": "flight_inquiry",
			"Camper Presale": "camper_presale_inquiry",
			"Bank Account": None,
		}

		if inquiry_mapping.get(self.inquiry_type):
			set_trip_value(
				self.trip,
				inquiry_mapping.get(self.inquiry_type),
				self.name if not unlink else None,
			)


def set_trip_value(trip_name, key, value):
	trip = frappe.get_doc("Trip", trip_name)
	setattr(trip, key, value)
	trip.save(ignore_permissions=True)
