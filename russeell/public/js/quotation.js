//Quotation
frappe.ui.form.on("Quotation", {

    refresh: function(frm) {
        frm.set_query("item_code", "items", function (doc, cdt, cdn) {
            if (doc.custom_quotation_type == "Visit" || doc.custom_quotation_type == "Station"){
              return {
                "filters": {
                    "customer": undefined,
                    "is_sales_item":1,
                    "has_variants":0,
                    "is_stock_item": 0
                },
              };
            }
            else {
                return {
                    "filters": {
                    "customer": undefined,
                    "is_sales_item":1,
                    "has_variants":0
                },
                }
            }
        });
    },
   
    setup: function (frm){ 
        set_options_for_service_type(frm)   
    },
    custom_visit_type: function(frm){
        set_options_for_visit_type(frm)
    },
    custom_service_type:  function (frm){
        set_options_for_service_type(frm)
    },
    custom_total_hours: function(frm){
        frm.doc.custom_man_power_cost.forEach(function (row) {
            if (row.cost_per_hour) {
                let total_cost = (row.qty * row.cost_per_hour* (frm.doc.custom_total_hours || 0)).toFixed(2)
                frappe.model.set_value(row.doctype, row.name, 'normal_hour_total_cost', parseFloat(total_cost) )
            }
        })
    },
    custom_actual_overtime_hours: function(frm){
        frm.doc.custom_man_power_cost.forEach(function (row) {
            if (row.overtime_per_hour) {
                let total_cost = ((row.qty * row.overtime_per_hour ) * frm.doc.custom_actual_overtime_hours).toFixed(2)
                frappe.model.set_value(row.doctype, row.name, 'overtime_hour_total_cost', parseFloat(total_cost))
            }
        })
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
        calculate_admin_fees(frm)
    },
    custom_admin_fees:function (frm){
        calculate_total_estimated_cost(frm)
        calculate_suggested_sales_rate(frm)
    },
    custom_no_of_visits:function(frm){
        calculate_total_visit(frm)
    },
    custom_no_of_locations:function(frm){
        calculate_total_visit(frm)
    },
    custom_total_no_of_visits:function(frm){
        calculate_total_hours(frm)
        set_item_qty_in_table(frm)
    },
    custom_visit_duration_hrs:function(frm){
        calculate_total_hours(frm)
    },
    custom_suggested_sales_amount: function(frm){
        set_suggested_sales_rate_per_visit(frm) 
    },
    custom_suggested_sales_per_visits:function(frm){
        set_item_rate_in_table(frm)  
        // set_suggested_sales_rate_per_visit(frm) 
    }
})

let set_options_for_visit_type = function(frm){
    let options = [""]
    if (frm.doc.custom_visit_type == "Contract"){
        options = [
            "",
            "GPC",
            "Fumigation",    
            "Bird-Control"
        ];
    }
    if (frm.doc.custom_visit_type == "Job"){
        options = [
            "",
            "Fumigation",
            "Termite",
            "Bird-Control",
            "Supply",
            "Disinfection",
            "GPC"
        ];
    }

    set_field_options("custom_service_type",options.join("\n"));
}

let set_options_for_service_type =  function(frm){
    let options = [""]
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

    if (frm.doc.custom_service_type == "Supply" || frm.doc.custom_service_type == "Disinfection") {
        options = [];
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

let set_item_rate_in_table = function(frm){
    if (frm.doc.items.length === 0){
        frappe.throw(__('Please Fill Item Table First.'))
    }
    else{
        let item = frm.doc.items[0] 
        frappe.model.set_value('Quotation Item', item.name, 'rate', parseFloat(frm.doc.custom_suggested_sales_per_visits.toFixed(2)))
        frappe.show_alert({
            message: __("Set rate in item table"),
            indicator: "green",
        });
    }
}

let calculate_total_visit = function(frm){
    let total_visit = (frm.doc.custom_no_of_visits || 0) * (frm.doc.custom_no_of_locations || 0)
    frm.set_value('custom_total_no_of_visits', total_visit)
}

let calculate_total_hours = function(frm){
    let total_hours = (frm.doc.custom_visit_duration_hrs || 0) * (frm.doc.custom_total_no_of_visits || 0)
    frm.set_value("custom_total_hours", total_hours);

    frappe.db.get_single_value('Russeell Setting', 'no_of_hours_in_a_month')
    .then(hours => {
        if (frm.doc.custom_total_hours >= hours){
            frm.set_value("custom_normal_hours_without_overtime", hours);
            
            let overtime_hour = frm.doc.custom_total_hours - frm.doc.custom_normal_hours_without_overtime
            frm.set_value("custom_calculated_overtime_hours", overtime_hour);
        }
        else {
            frm.set_value("custom_normal_hours_without_overtime", frm.doc.custom_total_hours);
            frm.set_value("custom_calculated_overtime_hours", 0);
        }
    })
}

let calculate_admin_fees = function(frm){
    frappe.db.get_single_value('Russeell Setting', 'admin_fees_percentage')
    .then(fees => {
        let sub_total = (frm.doc.custom_man_power_grand_total || 0
            + frm.doc.custom_consumption_tools_grand_total || 0
            + frm.doc.custom_equipment_grand_total || 0
            + frm.doc.custom_vehicle_grand_total || 0
            + frm.doc.custom_other_cost_grand_total || 0 )
        let admin_fees = parseFloat(((sub_total * fees) / 100).toFixed(2))

    frm.set_value("custom_sub_grand_total", parseFloat(sub_total.toFixed(2)));
    frm.set_value("custom_admin_fees", parseFloat(admin_fees.toFixed(2)));
    })
}

let calculate_total_estimated_cost = function(frm){
    let total_estimated_cost = (frm.doc.custom_sub_grand_total + frm.doc.custom_admin_fees)

    frm.set_value("custom_total_estimated_cost", parseFloat(total_estimated_cost.toFixed(2)));
}

let calculate_suggested_sales_rate = function(frm){
    frappe.db.get_single_value('Russeell Setting', 'suggested_sales_markup_percentage')
    .then(sales => {
        let sales_rate = parseFloat(((frm.doc.custom_total_estimated_cost * sales) / 100).toFixed(2)) + frm.doc.custom_total_estimated_cost;
        frm.set_value("custom_suggested_sales_amount", parseFloat(sales_rate.toFixed(2)));
    })
}

let set_suggested_sales_rate_per_visit = function(frm){
    if(frm.doc.custom_sales_qty){
        let suggested_sales_per_visits = (frm.doc.custom_suggested_sales_amount / frm.doc.custom_sales_qty).toFixed(2)
        frm.set_value('custom_suggested_sales_per_visits',  parseFloat(suggested_sales_per_visits) )
    }
}

let set_item_qty_in_table = function(frm){
    frm.set_value('custom_sales_qty', frm.doc.custom_total_no_of_visits)
    if (frm.doc.items.length === 0){
        frappe.throw(__('Please Fill Item Table First.'))
    }
    else{
        let item = frm.doc.items[0] 
        frappe.model.set_value('Quotation Item', item.name, 'qty', frm.doc.custom_total_no_of_visits)
    }
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
    total_cost:function(frm, cdt, cdn){
        calculate_consumption_items_grand_total(frm,cdt,cdn)
       },
    custom_consumption_table_remove:function(frm, cdt, cdn){
        calculate_consumption_items_grand_total(frm,cdt,cdn)
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
        let total_cost = (row.qty * row.cost_per_hour.toFixed(2) * (frm.doc.custom_total_hours || 0)).toFixed(2)
        frappe.model.set_value(cdt, cdn, 'normal_hour_total_cost',parseFloat(total_cost))
    }
}

let overtime_hour_total_cost = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.overtime_per_hour) {
        let total_cost = (row.qty * row.overtime_per_hour  * (frm.doc.custom_actual_overtime_hours || 0)).toFixed(2)
        frappe.model.set_value(cdt, cdn, 'overtime_hour_total_cost', parseFloat(total_cost))
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
        let total_cost = row.qty * row.valuation_rate.toFixed(2)
        frappe.model.set_value(cdt, cdn, 'total_cost', parseFloat(total_cost) )
    }

    frappe.call({
        method: "russeell.api.get_default_warehouse_for_consumed_item",
        args: {
            item_code: row.consumption_item_code,
            company: frm.doc.company,
        },
        callback: function (r) {
            default_warehouse = r.message
            frappe.model.set_value(cdt, cdn, 'warehouse', default_warehouse)
           
        }
    })
}

let calculate_net_cost = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.cost_per_hour) {
        let total_cost = (row.qty * row.cost_per_hour.toFixed(2))
        frappe.model.set_value(cdt, cdn, 'net_total', parseFloat(total_cost))
    }
}

let calculate_man_power_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_man_power_cost.forEach(function (cost) {
        grand_total = (grand_total + cost.net_total)
    })
    frm.set_value("custom_man_power_grand_total", parseFloat(grand_total.toFixed(2)));
}

let calculate_consumption_items_grand_total =  function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_consumption_table.forEach(function (cost) {
        grand_total = grand_total + cost.total_cost
    })
    frm.set_value("custom_consumption_tools_grand_total", parseFloat(grand_total.toFixed(2)));
}

let calculate_equipments_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_equipments_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })
    frm.set_value("custom_equipment_grand_total", parseFloat(grand_total.toFixed(2)));
}

let calculate_vehicle_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_vehicles_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })
    frm.set_value("custom_vehicle_grand_total", parseFloat(grand_total.toFixed(2)));
}

let calculate_other_cost_grand_total = function (frm, cdt, cdn) {
    let grand_total = 0
    frm.doc.custom_other_cost.forEach(function (cost) {
        grand_total = grand_total + cost.net_total
    })
    frm.set_value("custom_other_cost_grand_total", parseFloat(grand_total.toFixed(2)));
}