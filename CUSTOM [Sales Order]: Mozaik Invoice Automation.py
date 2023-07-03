# AUTOMATED ACTION
# Model: Sales Order
# Trigger: On Creation & Update

# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - float_compare: Odoo function to compare floats based on specific precisions
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - UserError: Warning Exception to use with raise
#  - Command: x2Many commands namespace
# To return an action, assign: action = {...}


def log_checklist_results(checklist_results, is_valid):
  log('******** BEGIN AUTO-INVOICE LOG ********')
  for result in checklist_results:
    log(result)
  log('OVERALL VALIDITY CHECK: ' + str(is_valid))

def check_requirements(record):
  checklist_results = []
  payment_id = -1
  is_valid = True

  # 1. Check the company
  if record.sudo().company_id.id == 2: #Mozaik's ID
    checklist_results.append('Company Check - Passed')
  else:
    checklist_results.append('Company Check - Failed')
    is_valid = False

  # 2. Check for an existing invoice
  existing_invoices = record.env['account.move'].sudo().search([
    ('invoice_origin', '=', record.name), 
    ('move_type', '=', 'out_invoice'), 
    ('payment_state', '!=', 'reversed')
  ])
  if not existing_invoices:
    checklist_results.append('Existing Invoice Check - Passed')
  else:
    checklist_results.append('Existing Invoice Check - Failed')
    is_valid = False

  # 3. Check the order's Delivery Status
  if record.sudo().x_studio_delivery_status in ['Done', 'Partial']:
    checklist_results.append('Delivery Status Check - Passed')
  else:
    checklist_results.append('Delivery Status Check - Failed')
    is_valid = False

  # 4. Verify the line items' delivered quantities
  all_line_items_valid = True
  for line in record.sudo().order_line:
    if 'Delivery' not in line.name and 'delivery' not in line.name and 'Discount' not in line.name and 'discount' not in line.name and 'Shipping' not in line.name and 'shipping' not in line.name:
      if line.qty_delivered < line.product_uom_qty:
        checklist_results.append('Line Item Delivered Check - Failed for "' + str(line.name) + '"')
        all_line_items_valid = False
      else:
        checklist_results.append('Line Item Delivered Check - Passed for "' + str(line.name) + '"')
    else:
      if line.qty_delivered < line.product_uom_qty:
        line.write({'qty_delivered': line.product_uom_qty})
        checklist_results.append('Line Item Delivered Check - Set Delivery\Discount value in "' + str(line.name) + '"')
      else:
        checklist_results.append('Line Item Delivered Check - Skipped Delivery\Discount in "' + str(line.name) + '"')
  if all_line_items_valid:
    checklist_results.append('Cumulative Line Item Delivered Check - Passed')
  else:
    checklist_results.append('Cumulative Line Item Delivered Check - Failed')
    is_valid = False

  return is_valid, checklist_results, payment_id

if not env.context.get('automatic_update'):
  is_valid, checklist_results, payment_id = check_requirements(record)
  log_checklist_results(checklist_results, is_valid)
  
  if is_valid:
    # 1. Create and confirm the invoice
    invoice = record.sudo().env['account.move'].with_context(default_move_type='out_invoice').with_company(2).create({
      'partner_id': record.partner_id.id,
      'partner_shipping_id': record.partner_shipping_id.id,
      'x_studio_order': record.name,
      'invoice_origin': record.name,
      'fiscal_position_id': record.fiscal_position_id.id if record.fiscal_position_id else 23,
      'invoice_date': datetime.datetime.today() - datetime.timedelta(hours=7),
      'invoice_line_ids': [(0, 0, {
        'name': line.name,
        'quantity': line.product_uom_qty,
        'price_unit': line.price_unit,
        'product_id': line.sudo().product_id.id,
        'tax_ids': [(6, 0, line.tax_id.ids)],
        'analytic_account_id': line.sudo().order_id.analytic_account_id.id,
        'sale_line_ids': [(6, 0, [line.id])],
        'company_id': 2,
      }) for line in record.order_line],
    })
    if invoice:
      invoice.sudo().action_post()
      record.sudo().write({
        'invoice_ids': [(4, invoice.id, None)]
      })
      message = "<p><i>(Automated)</i></p><p>This journal entry has been created from: <a href='#' data-oe-model='sale.order' data-oe-id='" + str(record.id) + "'> " + str(record.name) + "</a></p>"
      invoice.sudo().message_post(body=message, subtype_xmlid="mail.mt_note")  # You can change the subtype_xmlid as needed.
      log('Invoice created and confirmed for order id ' + str(record.id))
    
      # 2. Email the invoice
      template = env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
      if template and invoice:
        invoice.sudo().message_post_with_template(template.id)
        log('Invoice email sent for invoice id ' + str(invoice.id))
  
  log('******** END AUTO-INVOICE LOG ********')
