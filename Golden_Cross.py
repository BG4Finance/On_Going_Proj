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
        self.account = self.api.get_account()
        self.account.status
        self.time_format = time_format
        #Useful elements to be recalled later on
        self.portfolio = self.api.list_positions()
        self.clock = self.api.get_clock()
        self.orders = self.api.list_orders(status = "open")

    def status(self):
        today = (dt.datetime.now().strftime(self.time_format))
        print("Today is: {}".format(today))
        print("Position list:")
        print(self.portfolio)
        equity = float(self.account.equity)
        margin_multiplier = float(self.account.multiplier)
        print('Margin multiple: %s' %(margin_multiplier) + 'X')
        tot_buy_pow = margin_multiplier * equity
        tot_buy_pow_pc = tot_buy_pow * 100/equity
        print('Actual total buying power = {0}, {1}%'.format(tot_buy_pow, tot_buy_pow_pc))
        print('- - - -')
        print('')


    def tradable(self, asset = 'AAPL'):
        if type(asset) is str:
            asset = [asset]
        try:
            asset_query = self.api.get_asset(asset)
            if asset_query.tradable:
                print('We can trade {}.'.format(asset))
        except Exception as e:
            print('{} Not available'.format(asset))


    def get_data(self, stock, time, obs_limit = 80, show_data = False):
        if type(stock) is str:
            stock = [stock]
        now = (dt.datetime.now()).date().strftime(self.time_format)
        self.data = pd.DataFrame()
        self.volume = pd.DataFrame()

        for ass in stock:
            ass_data = self.api.get_barset(stock ,timeframe = time, limit = obs_limit, end=now)[ass]
            #Extract close values!
            self.initial = ass_data[0].c
            self.close = ass_data[-1].c

            price = np.array(ass_data[0].c)
            for i in range(1,obs_limit):
                price = np.vstack((price,ass_data[i].c))
            price = pd.DataFrame(price,columns=[ass])
            self.data = pd.concat([self.data, price], axis=1)

            vol = np.array(ass_data[0].v)
            for i in range(1,obs_limit):
                vol = np.vstack((vol,ass_data[i].v))
            vol = pd.DataFrame(vol,columns=[ass])
            self.volume = pd.concat([self.volume, vol], axis=1)

            if show_data == True:
                print(ass)
                print('Close: {0}; @Vol: {1}'.format(self.close, int(self.volume[ass].tail(1))))
                print('Change in the period: {}%'.format(round(float(self.close/self.initial-1)*100,4)))
                print(self.data)
                #Localize data with:
                #self.data.loc[1,ass]
                print('- - - -')


    #V2 aim to be a shorter verision of sma_check
    def sma_v2(self, stock = 'TSLA', time = 'day', short_obs = 40, long_obs = 60):
        if type(stock) is str:
            stock = [stock]
        sma_st = 0
        sma_lt = 0
        for ass in stock:
            self.get_data(ass, time, obs_limit=long_obs, show_data=False)
            #self.data.loc[0,'TSLA'][i]
            for i in range((len(self.data[ass])-long_obs),len(self.data[ass])):
                sma_lt +=  self.data.loc[i,ass]
            sma_lt=round(sma_lt/long_obs,2)

            for i in range((len(self.data[ass])-short_obs),len(self.data[ass])):
                sma_st += self.data.loc[i,ass]
            sma_st=round(sma_st/short_obs,2)

            print(ass)
            print('Close: {0}; @Vol: {1}'.format(self.close, int(self.volume[ass].tail(1))))
            print('Change in the period ({0} Obs): {1}%'.format(long_obs, round(float(self.close/self.initial-1)*100,4)))
            print('Simple moving average: {0}obs: {1}; {2}obs: {3}.'.format(long_obs, sma_lt, short_obs, sma_st))
            print('- - - - - -')
            print('')

            # Get a list of all of our positions
            if sma_st > sma_lt :
                self.side = 'buy'
                print('BUY PHASE')
            elif sma_lt > sma_st:
                self.side = 'sell'
                print('SELL PHASE')
            else:
                self.side = 'wait'
                print('GOLD CROSS IN COURSE')



    def GX (self, stock = 'TSLA', time = 'day', short_obs = 40, long_obs = 60):
        if type(stock) is str:
            stock = [stock]
        print(self.portfolio)
        print(self.orders)
        for ass in stock:
            self.sma_v2(ass,time,short_obs,long_obs)
            if self.side == 'buy':
                pass



# Print the quantity of shares for each position.
#for position in portfolio:
#print("{} shares of {}".format(position.qty, position.symbol))
