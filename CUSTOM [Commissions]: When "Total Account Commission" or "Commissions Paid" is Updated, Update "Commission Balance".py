# AUTOMATED ACTION
# Model: Commissions
# Action To Do: Update the Record
# Trigger: On Update

# Field:
# Commission Balance (x_commissions)

# Evaluation Type:
# Python expression

# Value:
record.x_studio_total_account_commission - record.x_studio_commissions_paid
