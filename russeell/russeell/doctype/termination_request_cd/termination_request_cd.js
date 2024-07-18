// // Copyright (c) 2024, GreyCube Technologies and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Termination Request CD", {
// 	so_reference: function(frm) {
//         if(frm.doc.so_reference){
//             frappe.call({
//                 method:"russeell.russeell.doctype.termination_request.termination_request.get_no_of_credit_note_for_advance",
//                 args: {
//                     so_name: frm.doc.so_reference,
//                     to_date: frm.doc.date
//                 },
//                 callback: function(r) {
//                     if(r.message){
//                         // console.log(r.message)

//                         let no_of_visit_done = r.message[0]
//                         let no_of_pending_visit = r.message[1]

//                         frm.set_value('no_of_visit_done', no_of_visit_done)
//                         frm.set_value('no_of_pending_visit', no_of_pending_visit)

//                         // console.log(no_of_visit_done, 'no_of_visit_done', no_of_pending_visit, 'no_of_pending_visit')
//                     }
//                 }
//             })
//         }
// 	},
// });
