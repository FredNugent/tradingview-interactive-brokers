import redis, json
from ib_insync import *
import asyncio, time, random

# connect to Interactive Brokers (try all 4 options)
ib = IB()
print("Trying to connect...")
try: 
    if not ib.isConnected(): ib.connect('127.0.0.1', 7496, clientId=1) # live account on IB TW
except: a=1
try: 
    if not ib.isConnected(): ib.connect('127.0.0.1', 4001, clientId=1) # live account on IB gateway
except: a=1
try: 
    if not ib.isConnected(): ib.connect('127.0.0.1', 7497, clientId=1) # paper account on IB TW
except: a=1
try: 
    if not ib.isConnected(): ib.connect('127.0.0.1', 4002, clientId=1) # paper account on IB gateway
except: a=1
if not ib.isConnected():
    raise Exception("** IB TW and IB gateway are not running, in live or paper configurations")

# connect to Redis and subscribe to tradingview messages
r = redis.Redis(host='localhost', port=6379, db=0)
p = r.pubsub()
p.subscribe('tradingview')
run = 1

print("Waiting for webhook messages...")
async def check_messages():
    #print(f"{time.time()} - checking for tradingview webhook messages")
    message = p.get_message()
    if message is not None and message['type'] == 'message':
        print(message)

        message_data = json.loads(message['data'])

        # Normalization -- this is where you could check passwords, normalize from "short ETFL" to "long ETFS", etc.
        if message_data['ticker'] == 'NQ1!':
            stock = Future('NQ', '20220916', 'GLOBEX')
        elif message_data['ticker'] == 'ES1!':
            stock = Future('ES', '20220916', 'GLOBEX')
        elif message_data['ticker'] == 'RTY1!':
            stock = Future('RTY', '20220916', 'GLOBEX')
        elif message_data['ticker'] == 'CL1!':
            stock = Future('CL', '20220720', 'NYMEX')
        elif message_data['ticker'] == 'CLU2022':
            stock = Future('CL', '20220822', 'NYMEX')
        elif message_data['ticker'] == 'NG1!':
            stock = Future('NG', '20220628', 'NYMEX')
        elif message_data['ticker'] == 'HG1!':
            stock = Future('HG', '20220928', 'NYMEX')
        elif message_data['ticker'] == '6J1!':
            stock = Future('J7', '20220919', 'GLOBEX')
        elif message_data['ticker'] == 'HEN2022':
            stock = Future('HE', '20220715', 'NYMEX')
        else:
            stock = Stock(message_data['ticker'], 'SMART', 'USD')

        order = MarketOrder(message_data['strategy']['order_action'], message_data['strategy']['order_contracts'])
        #ib.qualifyOrder(order)
        trade = ib.placeOrder(stock, order)
        print(trade)

async def run_periodically(interval, periodic_function):
    global run
    while run < 3600: # quit about once an hour (and let the looping wrapper script restart this)
        await asyncio.gather(asyncio.sleep(interval), periodic_function())
        run = run + 1

asyncio.run(run_periodically(1, check_messages))

ib.run()
