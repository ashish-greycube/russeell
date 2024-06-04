// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visit Plan CD", {
	customer_address: function (frm) {
		erpnext.utils.get_address_display(frm, "customer_address", "address_display", false);
        // frm.save()
	},
});
