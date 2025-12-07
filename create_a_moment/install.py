# Copyright (c) 2021, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe


def after_install():
	update_system_settings()
	update_website_settings()
	update_portal_settings()

	frappe.db.commit()


def update_system_settings():
	update_settings(
		"System Settings", {"date_format": "dd.mm.yyyy", "time_format": "HH:mm"}
	)


def update_website_settings():
	update_settings(
		"Website Settings",
		{
			"home_page": "login",
			"top_bar_items": None,
			"hide_footer_signup": True,
			"disable_signup": True,
		},
	)


def update_portal_settings():
	update_settings(
		"Portal Settings",
		{
			"default_role": "Customer",
			"default_portal_home": "/trip",
			"hide_standard_menu": "1",
			"custom_menu": [
				{
					"title": "Trip",
					"enabled": 1,
					"route": "/trip",
					"reference_doctype": "Trip",
					"role": "Customer",
				},
				{
					"title": "Inquiry",
					"enabled": 1,
					"route": "/inquiry",
					"reference_doctype": "Inquiry",
					"role": "Customer",
				},
			],
		},
	)


def update_settings(doctype: str, settings: dict):
	doc = frappe.get_single(doctype)
	doc.update(settings)
	doc.save()
