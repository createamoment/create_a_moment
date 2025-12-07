// Copyright (c) 2021, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Inquiry', {
	onload: function (frm) {
		frm.set_query("trip", function () {
			return {
				filters: {
					"customer": frm.doc.customer
				}
			};
		});
	},
	refresh: function (frm) {
		if (!frm.is_new()) {
			if (frm.doc.status === "Open") {
				frm.add_custom_button(__("Mark as Completed"), function () {
					frm.set_value("status", "Completed")
					frm.save()
				});
			}

			if (["Processing", "Open", "Completed", "Error"].includes(frm.doc.status)) {
				frm.add_custom_button(__("Cancel Inquiry"), function () {
					frm.set_value("status", "Cancelled")
					frm.save()
				});
			}
		}
	}
});
