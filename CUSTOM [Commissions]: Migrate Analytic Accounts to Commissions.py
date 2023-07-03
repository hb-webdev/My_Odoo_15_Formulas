# SERVER ACTION

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


# For migrating all records from Analytic Accounts to Commissions.
# Recommended to keep the "limit" at 400, and run "offset" at 0, then 400, etc. (i.e. Run in chunks of 400)
# Meant to be "RUN MANUALLY"
def process_records(offset, limit):
    records = env['account.analytic.account'].search([], offset=offset, limit=limit)
    log("CUSTOM: Records found: " + str(len(records)))
    for index, record in enumerate(records):
        log("CUSTOM[" + str(index + offset) + "]: Creating commission for account " + str(record.id) + ". record.id=" + str(record.id) + " | record.company_id[0].id=" + str(record.company_id[0].id))
        model.create({'x_studio_commission_aa': record.id, 'x_studio_company_id': record.company_id[0].id })

    log("CUSTOM: Scheduled action completed.")

# Set the offset value and process the corresponding chunk of records
offset = 3600  # 0 or 400, 800, etc.
limit = 400
process_records(offset, limit)
