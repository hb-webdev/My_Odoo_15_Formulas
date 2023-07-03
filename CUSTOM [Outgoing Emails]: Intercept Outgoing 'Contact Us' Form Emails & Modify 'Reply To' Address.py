# AUTOMATED ACTION
# Model: Outgoing Mails
# Trigger: On Creation

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



if "submitted the form from your" in record.subject:
  start_quote_pos = record.subject.find("'")
  end_quote_pos = record.subject.find("'", start_quote_pos + 1) 
  customer_email = record.subject[start_quote_pos + 1:end_quote_pos] 
  record['reply_to'] = customer_email
