# AUTOMATED ACTION
# Model: Commissions
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



record['x_name'] = str(record.x_studio_commission_aa.name) + (' - ' + str(record.x_studio_commission_aa.partner_id.name) if record.x_studio_commission_aa.partner_id.name not in (0, 1) else '')

server_action = env['ir.actions.server'].browse(898)
server_action.with_context(active_model='x_commissions', active_ids=[record.id]).run()
