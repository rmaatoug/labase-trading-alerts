from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=6)

contract = Stock('AAPL', 'SMART', 'USD')
ib.qualifyContracts(contract)

bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='2 D',
    barSizeSetting='5 mins',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1
)

last = bars[-1]
print("Dernière barre 5min:", last.date, "O/H/L/C:", last.open, last.high, last.low, last.close)

ib.disconnect()
