from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=3)

contract = Stock('AAPL', 'SMART', 'USD')
ticker = ib.reqMktData(contract, '', False, False)

ib.sleep(2)
print("AAPL bid/ask/last:", ticker.bid, ticker.ask, ticker.last)

ib.cancelMktData(contract)
ib.disconnect()
