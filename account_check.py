from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

summary = ib.accountSummary()
for row in summary:
    if row.tag in ("NetLiquidation", "AvailableFunds", "Currency"):
        print(row.tag, row.value, row.currency)

ib.disconnect()
