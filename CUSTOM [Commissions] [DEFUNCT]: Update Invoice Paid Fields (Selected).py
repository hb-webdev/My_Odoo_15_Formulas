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

for record in records:
  if (record.x_studio_commission_aa.name != 1 and record.x_studio_commission_aa.name != 0):
    invoices = env['account.move'].search(['&', ('invoice_origin', 'ilike', record.x_studio_commission_aa.name), ('state', '=', 'posted')])
    #invoices = self.env['account.move'].search([['invoice_origin', 'like', record.x_studio_commission_aa.name]])
    num_posted = len(invoices)
    num_unpaid = 0
    num_paid = 0
    num_reversed = 0
    num_legacy = 0
    for invoice in invoices:
      if (invoice.payment_state == 'not_paid' or invoice.payment_state == 'partial'):
        num_unpaid += 1
      elif (invoice.payment_state == 'paid' or invoice.payment_state == 'in_payment'):
        num_paid += 1
      elif (invoice.payment_state == 'reversed'):
        num_reversed += 1
      elif (invoice.payment_state == "invoicing_legacy"):
        num_legacy += 1
    num_payable = num_posted - num_reversed - num_legacy
    if (num_payable > 0):
      if (num_unpaid > 0):
        record['x_studio_invoice_paid_date'] = ''
        record['x_studio_invoice_status'] = str(num_paid) + '/' + str(num_payable) + ' Paid'
      elif (num_paid > 0 and num_paid == num_payable):
        payments = env['account.payment'].search([])
        dates_paid = []
        invoice_amount = 0
        for invoice in invoices:
          invoice_amount += invoice.amount_total
          if (invoice.payment_state == 'paid' or invoice.payment_state == 'in_payment'):
            for payment in payments:
              for reconciled_invoice in payment.reconciled_invoice_ids:
                if (reconciled_invoice.id == invoice.id):
                  dates_paid.append(payment.date)
        if (len(dates_paid) == 0 and invoice_amount == 0):
          record['x_studio_invoice_paid_date'] = ''
          record['x_studio_invoice_status'] = '[No Cost]'
        elif(len(dates_paid) == 0):
          record['x_studio_invoice_paid_date'] = ''
          record['x_studio_invoice_status'] = 'Reversed'
        elif(len(dates_paid) > 0):
          record['x_studio_invoice_paid_date'] = max(dates_paid)
          record['x_studio_invoice_status'] = 'Paid'
        else:
          record['x_studio_invoice_paid_date'] = ''
          record['x_studio_invoice_status'] = 'Error'
      else:
        record['x_studio_invoice_paid_date'] = ''
        record['x_studio_invoice_status'] = 'Error'
    else:
      record['x_studio_invoice_paid_date'] = ''
      record['x_studio_invoice_status'] = 'N/A'
  else:
    record['x_studio_invoice_paid_date'] = ''
    record['x_studio_invoice_status'] = ''


