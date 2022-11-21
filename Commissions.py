# Paid Date (Text)
for record in self:
  if (record.x_name != 1 and record.x_name != 0):
    invoices = self.env['account.move'].search(['&', ('invoice_origin', '=', record.x_name.split(' ')[0]), ('state', '=', 'posted')])
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
        record['x_studio_paid_date'] = str(num_paid) + ' of ' + str(num_payable)
      elif (num_paid > 0 and num_paid == num_payable):
        payments = self.env['account.payment'].search([])
        dates_paid = []
        for invoice in invoices:
          if (invoice.payment_state == 'paid' or invoice.payment_state == 'in_payment'):
            for payment in payments:
              for reconciled_invoice in payment.reconciled_invoice_ids:
                if (reconciled_invoice.id == invoice.id):
                  dates_paid.append(payment.date)
        if (len(dates_paid) == 0 and record.amount_total == 0):
          record['x_studio_paid_date'] = '[No Cost]'
        elif(len(dates_paid) == 0):
          record['x_studio_paid_date'] = '[Not Found] (Reversed?)'
        elif(len(dates_paid) > 0):
          record['x_studio_paid_date'] = max(dates_paid)
        else:
          record['x_studio_paid_date'] = 'Error'
      else:
        record['x_studio_paid_date'] = 'Error'
    else:
      record['x_studio_paid_date'] = 'N/A'
  else:
    record['x_studio_paid_date'] = ''
    
    
# Num Total Invoices
for record in self:
  if (record.x_studio_commission_aa.name != 1 and record.x_studio_commission_aa.name != 0):
    invoices = self.env['account.move'].search([['invoice_origin', '=', record.x_studio_commission_aa.name]])
    num_invoices = len(invoices)
    record['x_studio_test_field_invoices'] = num_invoices
  else:
    record['x_studio_test_field_invoices'] = 0
    
    
# All Invoice Names
for record in self:
  if(record.x_studio_commission_aa.name != 0 and record.x_studio_commission_aa.name != 1):
    invoices = self.env['account.move'].search([['invoice_origin', '=', record.x_studio_commission_aa.name]])
    invoice_names = ""
    for invoice in invoices:
      invoice_names = invoice_names + ' || ' + invoice.name
    else:
      record['x_studio_test_field'] = str(invoice_names)
  else:
    record['x_studio_test_field'] = ''
    
  
  # Num Open Invoices
  for record in self:
  if (record.x_studio_commission_aa.name != 1 and record.x_studio_commission_aa.name != 0):
    invoices = self.env['account.move'].search([['invoice_origin', '=', record.x_studio_commission_aa.name]])
    num_unpaid = 0
    for invoice in invoices:
      if (invoice.payment_state == 'not_paid' or invoice.payment_state == 'partial'):
        num_unpaid += 1
    record['x_studio_total_open_invoices_text'] = str(num_unpaid)
  else:
    record['x_studio_total_open_invoices_text'] = ''
