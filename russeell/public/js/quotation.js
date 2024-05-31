//Quotation
frappe.ui.form.on("Quotation", {
    setup: function (frm){ 
        set_options_for_service_type(frm)     
    },
    custom_service_type:  function (frm){
        set_options_for_service_type(frm)
    },

    custom_man_power_grand_total: function (frm){
        calculate_admin_fees(frm)
    },
    custom_consumption_tools_grand_total: function (frm){
        calculate_admin_fees(frm)
    },
    custom_equipment_grand_total: function (frm){
        calculate_admin_fees(frm)
    },
    custom_vehicle_grand_total:function (frm){
        calculate_admin_fees(frm)
    },
    custom_other_cost_grand_total:function (frm){
        calculate_total_estimated_cost(frm)
    },
    custom_admin_fees:function (frm){
        calculate_total_estimated_cost(frm)
    },
    custom_total_estimated_cost:function (frm){
        calculate_suggested_sales_rate(frm)
    },
    custom_no_of_visits:function(frm){
        calculate_total_hours(frm)
    },
    custom_visit_duration_hrs:function(frm){
        calculate_total_hours(frm)
    },
})

let set_options_for_service_type =  function(frm){
    let options = [""];
    if (frm.doc.custom_service_type == "Fumigation") {
        options = [
            "",
            "Silo",
            "Bulk",
            "Container"
        ];
    }
    
    if (frm.doc.custom_service_type == "Termite") {
        options = [
            "",
            "Pre-Construction",
            "Post-Construction",
        ];
    }

    if (frm.doc.custom_service_type == "Bird-Control") {
        options = [
            "",
            "Gel",
            "Net",
            "Spike",
            "Shooting"
        ];
    }

    if (frm.doc.custom_service_type == "GPC") {
        options = [
            "",
            "GPC Only",
            "GPC plus Birds",
            "GPC plu Bed Bugs",
            "GPC plus Wild Animal",
            "GPC All Covered",
        ];
    }

    set_field_options("custom_sub_type",options.join("\n"));
}

let calculate_total_hours = function(frm){
    let total_hours = (frm.doc.custom_visit_duration_hrs || 0) * (frm.doc.custom_no_of_visits || 0)
    frm.set_value("custom_total_hours", total_hours);

    frappe.db.get_single_value('Rsusseel Setting', 'no_of_hours_in_a_month')
    .then(hours => {
        if (frm.doc.custom_total_hours >= hours){
            frm.set_value("custom_normal_hours_without_overtime", hours);
            
            let overtime_hour = frm.doc.custom_total_hours - frm.doc.custom_normal_hours_without_overtime
            frm.set_value("custom_overtime_hours", overtime_hour);
        }
        else {
            frm.set_value("custom_normal_hours_without_overtime", frm.doc.custom_total_hours);
            frm.set_value("custom_overtime_hours", 0);
        }
    })
}

let calculate_admin_fees = function(frm){
    frappe.db.get_single_value('Rsusseel Setting', 'admin_fees_percentage')
    .then(fees => {
        let sub_total = (frm.doc.custom_man_power_grand_total 
            + frm.doc.custom_consumption_tools_grand_total 
            + frm.doc.custom_equipment_grand_total 
            + frm.doc.custom_vehicle_grand_total
            + frm.doc.custom_other_cost_grand_total)
        let admin_fees = (sub_total * fees) / 100

    frm.set_value("custom_sub_grand_total", sub_total);
    frm.set_value("custom_admin_fees", admin_fees);
    })
}

let calculate_total_estimated_cost = function(frm){
    let total_estimated_cost = (frm.doc.custom_sub_grand_total + frm.doc.custom_admin_fees)

    frm.set_value("custom_total_estimated_cost", total_estimated_cost);
}

let calculate_suggested_sales_rate = function(frm){
    frappe.db.get_single_value('Rsusseel Setting', 'suggested_sales_markup_percentage')
    .then(sales => {
        let sales_rate = (frm.doc.custom_total_estimated_cost * sales) / 100;
        frm.set_value("custom_suggested_sales_rate", sales_rate);
    })
}

//Man Power Cost CT
frappe.ui.form.on("Man Power Cost CT", {

    employee_type: function (frm, cdt, cdn) {
        calculate_normal_hour_total_cost(frm, cdt, cdn)
    },

    qty: function (frm, cdt, cdn) {
        calculate_normal_hour_total_cost(frm, cdt, cdn)
        overtime_hour_total_cost(frm, cdt, cdn)
    },

    overtime_per_hour: function (frm, cdt, cdn) {
        overtime_hour_total_cost(frm, cdt, cdn)
    },

    normal_hour_total_cost: function (frm, cdt, cdn) {
        calculate_net_total(frm, cdt, cdn)
    },

    overtime_hour_total_cost: function (frm, cdt, cdn) {
        calculate_net_total(frm, cdt, cdn)
    },
    net_total: function (frm, cdt, cdn) {
        calculate_man_power_grand_total(frm, cdt, cdn)
    },
    custom_man_power_cost_remove: function (frm, cdt, cdn) {
        calculate_man_power_grand_total(frm, cdt, cdn)
    },
});

frappe.ui.form.on("Consumption Table CT", {
    consumption_item_code:function(frm, cdt, cdn){
        calculate_total_cost_of_item(frm,cdt,cdn)
       },
    qty:function(frm, cdt, cdn){
        calculate_total_cost_of_item(frm,cdt,cdn)
       },
})  


//Equipments Cost CT
frappe.ui.form.on("Equipments Cost CT", {
    equipment_name: function (frm, cdt, cdn) {
        calculate_net_cost(frm, cdt, cdn)
    },
    qty: function (frm, cdt, cdn) {
        calculate_net_cost(frm, cdt, cdn)
    },
    net_total: function (frm, cdt, cdn) {
        calculate_equipments_grand_total(frm, cdt, cdn)
    },
    custom_equipments_cost_remove: function (frm, cdt, cdn) {
        calculate_equipments_grand_total(frm, cdt, cdn)
    },
})

//Vehicles Cost CT
frappe.ui.form.on("Vehicles Cost CT", {
    vehicle_name: function (frm, cdt, cdn) {
        calculate_net_cost(frm, cdt, cdn)
    },
    qty: function (frm, cdt, cdn) {
        calculate_net_cost(frm, cdt, cdn)
    },
    net_total: function (frm, cdt, cdn) {
        calculate_vehicle_grand_total(frm, cdt, cdn)
    },
    custom_vehicles_cost_remove: function (frm, cdt, cdn) {
        calculate_vehicle_grand_total(frm, cdt, cdn)
    },
})

//Other Cost Table CT
frappe.ui.form.on("Other Cost Table CT", {
    other_cost: function (frm, cdt, cdn) {
        calculate_net_cost(frm, cdt, cdn)
    },
    qty: function (frm, cdt, cdn) {
        calculate_net_cost(frm, cdt, cdn)
    },
    net_total: function (frm, cdt, cdn) {
        calculate_other_cost_grand_total(frm, cdt, cdn)
    },
    custom_other_cost_remove: function (frm, cdt, cdn) {
        calculate_other_cost_grand_total(frm, cdt, cdn)
    },
})

let calculate_normal_hour_total_cost = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.cost_per_hour) {
        let total_cost = row.qty * row.cost_per_hour * (frm.doc.custom_total_hours || 0)
        frappe.model.set_value(cdt, cdn, 'normal_hour_total_cost', total_cost)
    }
}

let overtime_hour_total_cost = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.overtime_per_hour) {
        let total_cost = row.qty * row.overtime_per_hour
        frappe.model.set_value(cdt, cdn, 'overtime_hour_total_cost', total_cost)
    }
}

let calculate_net_total = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.normal_hour_total_cost || row.overtime_hour_total_cost) {
        let total_cost = (row.normal_hour_total_cost || 0) + (row.overtime_hour_total_cost || 0)
        frappe.model.set_value(cdt, cdn, 'net_total', total_cost)
    }
}

let calculate_total_cost_of_item = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.valuation_rate) {
        let total_cost = row.qty * row.valuation_rate
        frappe.model.set_value(cdt, cdn, 'total_cost', total_cost)
    }
}

let calculate_net_cost = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.cost_per_hour) {
        let total_cost = row.qty * row.cost_per_hour
        frappe.model.set_value(cdt, cdn, 'net_total', total_cost)
    }
}

let calculate_man_power_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_man_power_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })

    frm.set_value("custom_man_power_grand_total", grand_total);
}

let calculate_equipments_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_equipments_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })
    frm.set_value("custom_equipment_grand_total", grand_total);
}

let calculate_vehicle_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_vehicles_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })
    frm.set_value("custom_vehicle_grand_total", grand_total);
}

let calculate_other_cost_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_other_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })
    frm.set_value("custom_other_cost_grand_total", grand_total);
}