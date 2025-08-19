// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Request CD", {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Create JV"), function () {
				let journal_entry = frappe.model.get_new_doc("Journal Entry");
				journal_entry.custom_payment_request_cd_reference = frm.doc.name;
				frappe.set_route("Form", journal_entry.doctype, journal_entry.name);
			}).addClass('btn-primary');
		}
	}
});
