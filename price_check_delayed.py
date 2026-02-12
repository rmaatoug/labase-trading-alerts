from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=5)

# 3 = delayed, 4 = delayed-frozen (selon droits)
ib.reqMarketDataType(3)

contract = Stock('AAPL', 'SMART', 'USD')
ticker = ib.reqMktData(contract, '', False, False)

ib.sleep(2)
print("AAPL delayed bid/ask/last:", ticker.bid, ticker.ask, ticker.last)

ib.cancelMktData(contract)
ib.disconnect()
