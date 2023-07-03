# AUTOMATED ACTION
# Model: Outgoing Mails
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


log('Email intercept triggered')
def get_email_domain(email_address):
    email_parts = email_address.split("@")
    domain = ''
    if len(email_parts) > 1:
      domain = email_parts[1].replace('>', '')
    log('domain: ' + domain)
    return domain if len(email_parts) > 1 else ''

def allowed_email_domain(email_address):
    log('email_address: ' + email_address)
    allowed_domains = ['mozaiksc.com', 'henriksenbutler.com', 'hewnfloor.com', 'hbflooringsolutions.com', 'hbdgmain.onmicrosoft.com']
    # Use a loop to check if the email address ends with any of the allowed domains
    for domain in allowed_domains:
      log('current domain: ' + domain)
      if email_address.replace('>','').endswith(domain):
        log('email ends in valid domain')
        return True
    return False

email_to_check = record.email_from
log('email_to_check: ' + email_to_check)

# Get the company_id from the res.company model based on the email domain
mail_mail_company_id = False
email_domain = get_email_domain(record.email_from)
if email_domain:
    company = env['res.company'].search([('email', 'ilike', email_domain)], limit=1)
    if company:
        mail_mail_company_id = company.id
        log('mail_mail_company_id: ' + str(mail_mail_company_id))

if not allowed_email_domain(email_to_check):
    if mail_mail_company_id == 2:
        log('email domain not valid, changing to mozaikscpostmaster')
        new_email_from = 'mozaikscpostmaster@hbdgmain.onmicrosoft.com'
    elif mail_mail_company_id == 3:
        log('email domain not valid, changing to customerservice@hewnfloor.com')
        new_email_from = 'customerservice@hewnfloor.com'
    else:
        # If company ID is not defined, provide a fallback email address
        log('email domain not valid, defaulting to mozaikscpostmaster')
        new_email_from = 'mozaikscpostmaster@hbdgmain.onmicrosoft.com'
    
    # Update the 'From' address
    record['email_from'] = new_email_from
else:
  log('email_domain ' + str(email_domain) + ' is a valid domain. Not changing from address')
