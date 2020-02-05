import alpaca_trade_api as alp
import numpy as np
import pandas as pd
import statistics
import sys
import time
import datetime as dt
from datetime import datetime, timedelta
from pytz import timezone
from alpaca_keys import keyid, secretkey, baseurl

#You can obtain the folowing API credential for free by visiting https://alpaca.markets/
#You can always opt for a paer account, as I did, or get a real one in action.
id = keyid
key = secretkey
url = baseurl

class alpaca_GB:
    def __init__(self, user = id, password = key, url = url, time_format = "%m/%d/%Y, %H:%M:%S"):
        self.id = user
        self.key = password
        self.api = alp.REST(key_id = self.id, secret_key = self.key, base_url = url)
        self.portfolio = self.api.list_positions()
        self.portfolio
        self.account = self.api.get_account()
        self.account.status
        self.time_format = time_format

    def status(self):
        today = (dt.datetime.now().strftime(self.time_format))
        print(today)

        equity = float(self.account.equity)
        margin_multiplier = float(self.account.multiplier)
        print('Margin multiple: %s' %(margin_multiplier) + 'X')
        tot_buy_pow = margin_multiplier * equity
        tot_buy_pow_pc = tot_buy_pow * 100/equity
        print('Actual total buying power = {0}, {1}%'.format(tot_buy_pow, tot_buy_pow_pc))

    def tradable(self, asset = 'AAPL'):
        asset_query = self.api.get_asset(asset)
        if asset_query.tradable:
            print('We can trade {}.'.format(asset))
        else:
            print('{} Not available'.format(asset))


    def get_data(self, stock = 'TSLA', time = 'day', print_data = False):
        now = (dt.datetime.now()).date().strftime(self.time_format)
        self.data = []
        for ass in stock:
            ass_data = self.api.get_barset(stock ,timeframe = time, limit=80, end=now)[ass]
            close = ass_data[-1].c
            print(ass)
            if print_data == True:
                print(ass_data)
            print('Close: {0}; Vol: {1}'.format(close, ass_data[-1].v))
            self.data.append(ass_data)

    #MIX of data plus mov avg.
    def sma_check(self, stock = 'TSLA', time = 'day', short_obs = 40, long_obs = 60):
        now = (dt.datetime.now()).date().strftime(self.time_format)
        self.data = []
        for ass in stock:
            ass_data = self.api.get_barset(stock ,timeframe = time, limit=long_obs+2, end=now)[ass]
            close = ass_data[-1].c
            print(ass)
            print('Close: {0}; Vol: {1}'.format(close, ass_data[-1].v))
            self.data.append(ass_data)
            #Mov avg calculation and evaluation for strategy
            sma_st = 0
            sma_lt = 0
            for i in range(1,long_obs):
                sma_lt += ass_data[-i].c
            sma_lt=round(sma_lt/long_obs,2)

            for i in range(1,short_obs):
                sma_st = (sma_st + ass_data[-i].c)
            sma_st=round(sma_st/short_obs,2)

            print('Simple moving average: {0}obs: {1}; {2}obs: {3}.'.format(long_obs, sma_lt, short_obs, sma_st))
            if sma_st > sma_lt :
                self.status = 'buy'
                print('BUY PHASE')
            elif sma_lt > sma_st:
                self.status = 'sell'
                print('SELL PHASE')
            else:
                self.status = 'wait'
                print('GOLD CROSS IN COURSE')

    def sma_trade (self):
        pass

        # Get a list of all of our positions.

# Print the quantity of shares for each position.
#for position in portfolio:
#    print("{} shares of {}".format(position.qty, position.symbol))
