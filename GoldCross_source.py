import alpaca_trade_api as alp
import numpy as np
import pandas as pd
import statistics
import sys
import time
import datetime as dt
from datetime import datetime, timedelta
from pytz import timezone

api = alp.REST(key_id = 'PKC3Q62740ML0K30TPVC', secret_key = 'TWyyiQcOqpRKyv2xNOt1XLAKZPW8vqvGraHtneMB', base_url="https://paper-api.alpaca.markets")
api.list_positions()
api_time_format = '%Y-%m-%dT%H:%M:%S.%f-04:00'
account = api.get_account()
account.status

today = (dt.datetime.now())
print(today)
equity = float(account.equity)
margin_multiplier = float(account.multiplier)
total_buying_power = margin_multiplier * equity
print(f'Initial total buying power = {total_buying_power}, {total_buying_power*100/equity}%')

now = (dt.datetime.now()).date().strftime(api_time_format)
data = api.get_barset('TSLA',timeframe='day', limit=80, end=now)
sma6 = 0
sma4 = 0
for i in range(1,60):
  sma6 = (sma6 + data['TSLA'][-i].c)
sma6=round(sma6/60,2)

for i in range(1,40):
  sma4 = (sma4 + data['TSLA'][-i].c)
sma4=round(sma4/40,2)

print(f'Simple moving average, 60D:{sma6} 40D:{sma4}')
if sma4 > sma6 :
  print('BUY PHASE')
elif sma6 > sma4:
  print('SELL PHASE')
else:
  print('GOLD CROSS IN COURSE')
  
  