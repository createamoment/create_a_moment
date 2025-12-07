# Copyright (c) 2021, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.model.document import Document


class Trip(Document):
	def before_validate(self):
		self.hostel_location = (
			"NZ Choice Backpackers"
			if self.hostel_location == "Choice Backpackers"
			else self.hostel_location
		)

	def before_save(self):
		self.clear_trip_data()
		self.update_status()

	def on_update(self):
		self.generate_payment_entry_for_sales_invoice()

	def generate_payment_entry_for_sales_invoice(self):
		if (
			self.payment_received
			and self.starter_package_sales_invoice
			and frappe.get_value(
				"Sales Invoice", self.starter_package_sales_invoice, "status"
			)
			!= "Paid"
			and frappe.get_value(
				"Sales Invoice", self.starter_package_sales_invoice, "docstatus"
			)
			== 1
		):
			get_payment_entry(
				"Sales Invoice", self.starter_package_sales_invoice
			).save().submit()

	def update_status(self):
		mapping = {
			"starter_package_inquiry_received": ["starter_package_inquiry"],
			"au_pair_inquiry_received": ["au_pair_inquiry"],
			"waiting_for_payment": ["starter_package_sales_invoice_attach"],
			"waiting_for_starter_package_booking_form": [
				"payment_received",
				"starter_package_inquiry",
			],
			"starter_package_booking_form_received": ["starter_package_booking_form"],
			"waiting_for_au_pair_booking_form": ["payment_received", "au_pair_inquiry"],
			"au_pair_booking_form_received": ["au_pair_booking_form"],
			"hostel_booked": ["hostel_booking_number", "hostel_booking_confirmation"],
			"bank_opening_date_arranged": [
				"bank_account_number",
				"bank_account_opening",
			],
			"airport_shuttle_booked": ["shuttle_number", "ticket"],
			"free_walking_tour_booked": [
				"free_walking_tour",
				"free_walking_tour_booking_number",
			],
			"prep_call_date_arranged": ["prep_call"],
			"flight_inquiry_received": ["flight_inquiry"],
			"camper_presale_inquiry_received": ["camper_presale_inquiry"],
			"camper_pick_up_date_arranged": ["camper_pick_up"],
		}

		for item in mapping.items():
			setattr(self, item[0], all([getattr(self, x) for x in item[1]]))

	def clear_trip_data(self):
		mapping = {
			"arrival": ["arrival_date", "arrival_time"],
			"prep_call": ["prep_call_date", "prep_call_time"],
			"bank_account_opening": [
				"bank_account_opening_date",
				"bank_account_opening_time",
			],
			"free_walking_tour": ["free_walking_tour_date", "free_walking_tour_time"],
			"starter_package_inquiry": [],
			"starter_package_booking_form": [],
			"au_pair_booking_form": [],
			"flight_inquiry": [],
			"camper_presale_inquiry": [],
			"camper_pick_up": ["camper_pick_up_date", "camper_pick_up_time"],
			"starter_package_sales_invoice": ["payment_due_date"],
		}

		for item in mapping.items():
			if not getattr(self, item[0]):
				for i in item[1]:
					setattr(self, i, None)
