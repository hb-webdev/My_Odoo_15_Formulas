# AUTOMATED ACTION
# Model: Analytic Account
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


server_action = env['ir.actions.server'].browse(898)

active_ids = env.context.get('active_ids', [])
log("GOT HERE. active_ids: " + str(active_ids))

if len(active_ids) > 0:
  records = env['account.analytic.account'].search([('id', 'in', active_ids)])
else:
  records = env['account.analytic.account'].search([['id', 'in', [record.id]]])

record_ids = [temp_record.id for temp_record in records]
commissions_entries = env['x_commissions'].search([['x_studio_commission_aa', 'in', record_ids]])

for record in records:
  if server_action and len(commissions_entries) > 0:
    for entry in commissions_entries:
      log("entry: " + str(entry) + " record: " + str(record))
      entry['x_name'] = str(record.name) + (' - ' + str(record.partner_id.name) if record.partner_id.name not in (0, 1) else '')
      entry['x_studio_salesperson'] = record.partner_id.user_id
      entry['x_studio_credit'] = record.credit
      entry['x_studio_debit'] = record.debit
      entry['x_studio_balance'] = record.balance
      
      if entry['x_studio_credit'] > 0 and entry['x_studio_balance'] >= 0:
        entry['x_studio_analytic_account_margin'] = entry.x_studio_balance / entry.x_studio_credit
      else:
        entry['x_studio_analytic_account_margin'] = 0.25
      
      if entry['x_studio_analytic_account_margin'] >=.25:
        entry['x_studio_total_account_commission'] = entry.x_studio_balance * .25
      else:
        entry['x_studio_total_account_commission'] = entry.x_studio_balance * entry.x_studio_analytic_account_margin
      
      entry['x_studio_commission_balance'] = entry.x_studio_total_account_commission - entry.x_studio_commissions_paid
      
      server_action.with_context(active_model='x_commissions', active_ids=[entry.id]).run()
    
