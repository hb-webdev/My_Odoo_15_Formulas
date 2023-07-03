# AUTOMATED ACTION
# Model: Journal Entry
# Trigger: On Update

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



server_action = env['ir.actions.server'].browse(901)
unique_analytic_accounts = set()

if record.invoice_origin != 0:
  invoice_origin_aa = env['account.analytic.account'].search([('name', 'ilike', record.invoice_origin)])
  unique_analytic_accounts.update(invoice_origin_aa)

if record.x_studio_order != 0:
  x_studio_order_aa = env['account.analytic.account'].search([('name', 'ilike', record.x_studio_order)])
  unique_analytic_accounts.update(x_studio_order_aa)
  
  
unique_analytic_accounts |= {line.analytic_account_id for line in record.invoice_line_ids}
for analytic_account in unique_analytic_accounts:
  if analytic_account.id != 0:
    log("analytic_account id: " + str(analytic_account.id))
    server_action.with_context(active_model='account.analytic.account', active_ids=[analytic_account.id]).run()
