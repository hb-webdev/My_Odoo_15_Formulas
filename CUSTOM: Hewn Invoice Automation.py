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
  if record.sudo().company_id.id == 3: #Hewn's ID
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

  # 5. Check the Payment confirmation
  payment_confirmed = False
  for message in record.sudo().message_ids:
    if 'The transaction with reference' in message.body and 'has been confirmed' in message.body:
      # 5a. Extract the Payment ID from the Note
      start_position = message.body.find('data-oe-id="')
      if start_position != -1:
        start_position += len('data-oe-id="')
        end_position = message.body.find('"', start_position)
        if end_position != -1:
          payment_id = int(message.body[start_position:end_position])
      if payment_id != -1:
        payment_confirmed = True
        break
  if payment_confirmed:
    checklist_results.append('Payment confirmation Check - Passed')
  else:
    checklist_results.append('Payment confirmation Check - Failed')
    is_valid = False

  return is_valid, checklist_results, payment_id

if not env.context.get('automatic_update'):
  is_valid, checklist_results, payment_id = check_requirements(record)
  log_checklist_results(checklist_results, is_valid)
  
  if is_valid:
    # 1. Create and confirm the invoice
    invoice = record.sudo().env['account.move'].with_context(default_move_type='out_invoice').with_company(3).create({
      'partner_id': record.partner_id.id,
      'partner_shipping_id': record.partner_shipping_id.id,
      'x_studio_order': record.name,
      'invoice_origin': record.name,
      'fiscal_position_id': record.fiscal_position_id.id if record.fiscal_position_id else 4,
      'invoice_date': datetime.datetime.today() - datetime.timedelta(hours=7),
      'invoice_line_ids': [(0, 0, {
        'name': line.name,
        'quantity': line.product_uom_qty,
        'price_unit': line.price_unit,
        'product_id': line.sudo().product_id.id,
        'tax_ids': [(6, 0, line.tax_id.ids)],
        'analytic_account_id': line.sudo().order_id.analytic_account_id.id,
        'sale_line_ids': [(6, 0, [line.id])],
        'company_id': 3,
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
    
      # 2. Create the Payment Transaction
      payment_transaction_obj = record.sudo().env['payment.transaction']
      transaction_reference = record.name + "_" + str(invoice.id)
      payment_transaction = env['payment.transaction'].sudo().search([('payment_id', '=', payment_id)], limit=1)
      acquirer = payment_transaction.acquirer_id if payment_transaction else False
      transaction_values = {
        'amount': invoice.amount_total,
        'currency_id': invoice.currency_id.id,
        'partner_id': invoice.partner_id.id,
        'acquirer_id': acquirer.id,
        'reference': transaction_reference,
        'payment_id': payment_id,
        'sale_order_ids': [(4, record.id, 0)],
      }
      transaction = payment_transaction_obj.sudo().create(transaction_values)
      # Link the payment.transaction to the invoice
      invoice.sudo().write({
        'transaction_ids': [(4, transaction.id, 0)]
      })
      
      # 3. Reconcile the payment with the invoice
      # Get all the payment move lines linked to the sales order with a positive credit amount
      sales_order_name = '%' + record.name + '%'
      journal_items = record.env['account.move.line'].sudo().search([
        ('payment_id.id', '=', payment_id),
        ('credit', '>', 0)
      ])
      # Log the number and names of the payments found
      log("1 Found " + str(len(journal_items)) + " payments:")
      for line in journal_items:
        log("Payment " + str(line.payment_id.name) + " for " + str(line.credit))
      # Get all the move lines from the invoice that are not reconciled
      invoice_move_lines = invoice.line_ids.sudo().filtered(lambda l: l.account_internal_type in ('receivable', 'payable') and not l.reconciled and not l.full_reconcile_id)
      # Log the total debit of the invoice_move_lines
      total_debit = sum(line.debit for line in invoice_move_lines)
      log("Total debit of invoice move lines: " + str(total_debit))
      try:
        (journal_items + invoice_move_lines).sudo().reconcile()
        message = "<p><i>(Automated)</i></p><p>Invoice validated.</p><p>Payment status changed to <b>" + str(invoice.payment_state).replace('_', ' ').title() + "</b></p>"
        invoice.sudo().message_post(body=message, subtype_xmlid="mail.mt_note")
      except Exception as e:
        log("Error during reconciliation: " + str(e))
  
  log('******** END AUTO-INVOICE LOG ********')
