import numpy as np
import pandas as pd
import configparser
from datetime import datetime
import pytz
from utils.Pytrader_DLL_API_V1_02 import Pytrader_DLL_API
from utils.Pytrader_API_V2_07 import Pytrader_API

from utils.utils import Timer
from utils.LogHelper import Logger

# add a logger for keeping track of what happens
log = Logger()
log.configure(logfile='BT_DLL_Demo.log')


# instruments to be used, if more then 1 instrument the instruments have to be synchronised.
# this means data filoes need to have same amount of bars and the dates have to be exactly same.
# otherwise the calculated bars will run out of order/time
_instrument_list = ['EURUSD']

# definition of the timeframes that we be used
# limit to what is for your stategy, no need to take care of timeframes not used.
# this will spoil capacity
timeframe_list = ['M1', 'M15', 'H1']

# broker instrument lookup list, just for compatibility
brokerInstrumentsLookup = {
    'EURUSD': 'EURUSD',
    'GBPNZD': 'GBPNZD',
    'GOLD': 'XAUUSD',
    'DAX': 'GER30'}

MT = Pytrader_API()                                                                                             # for retrieving instrument information

MT_Back = Pytrader_DLL_API()                                                                                    # back tester instance

# connect to the back tester
Connected = MT_Back.Connect(
    server='127.0.0.1',                                                                                         # compatibility
    port=10014,                                                                                                 # compatibility
    instrument_lookup=brokerInstrumentsLookup)

print(Connected)
if (Connected):
    log.debug('Connected to back tester.')

# check for license

license = MT_Back.Check_license(server = '127.0.0.1', port = 5555)
print(license)

# reset of backtester
ok = MT_Back.Reset_backtester()
if (ok == False):
    log.debug('Error in resetting the back tester')
    log.debug(MT_Back.command_return_error)


# the back tester has no account at start, so we have to set a value
# margin call is not used at the moment
ok = MT_Back.Set_account_parameters(balance = 1000.0, max_pendings = 50, margin_call= 50.0)

# set the directory of the M1 data files, In this directory the back trader will look for the M1 data files
ok = MT_Back.Set_data_directory(data_directory='C:\\Temp\\Bar_files')
if (ok == False):
    log.debug('Error in setting data directory')
    log.debug(MT_Back.command_return_error)

# set the comma or dot annotation.
# depending on your country / region reals are written with a dot or a comma
ok = MT_Back.Set_comma_or_dot(mode='comma')    

# set the instruments to trade, this will take a while depending on the number of instruments and the size of the datafiles
# Only if M1 datafiles are synchronized more the one instrument should be defined
ok = MT_Back.Set_instrument_list(instrument_list=_instrument_list)
if (ok == False):
    log.debug('Error in setting instruments and/or reading the datafiles')
    log.debug(MT_Back.command_return_error)

# set instrument parameters like max lotsize, min lotsize, ............(needed for trading)
# for getting these parameters make connection with MT4/5 terminal and get then from there.
# you can of course also define them yourselve

# first we  connect to a MT4/5 terminal
Connected = MT.Connect(
    server='127.0.0.1',
    port=1122,
    instrument_lookup=brokerInstrumentsLookup)

# retrieve the instrument info and set in the back tester
for _instrument in _instrument_list:
    _info = MT.Get_instrument_info(instrument = _instrument)
    print (_info)
    ok = MT_Back.Set_instrument_parameters(instrument=_info['instrument'], digits=_info['digits'], \
                                    max_lotsize=_info['max_lotsize'], min_lotsize=_info['min_lotsize'], \
                                    lot_stepsize=_info['lot_step'], point=_info['point'], tick_size=_info['tick_size'], tick_value=_info['tick_value'], \
                                    swap_long=_info['swap_long'], swap_short=_info['swap_short'] )

# disconnect
MT.Disconnect()


# set the time frames, like described above
ok = MT_Back.Set_timeframes(timeframe_list=timeframe_list)

# if you like to run more times the startegy and you do now want to start from the beginning, use this function.
# only the raw M1 data will be kept. all other info/pointers/... will be reset
# ok = MT_Back.Reset_backtester_pointers()                                                                    # keep the input of bars, and instrument information

# if we want to know how many M1 bars the backtester has in history and the dates of the first and last bar
# we can call this function
BT_info = MT_Back.Get_datafactory_info(instrument='EURUSD')
print(BT_info)

# at start there will be no history for bars witha period > M1.
# depending 0n your stategy the back tester has to move formwars x M1 bars to build all the needed bars for the used time frames
ok = MT_Back.Set_index_for_start(144000)                                         # this is 100 days ahead

# retrieving some bars, call is same as for pytrader_api
candles = MT_Back.Get_last_x_bars_from_now(instrument='EURUSD', timeframe=MT_Back.get_timeframe_value('M15'), nbrofbars=1000)
if type(candles) != pd.DataFrame:
        candles = pd.DataFrame(candles)
candles.rename(columns = {'tick_volume':'volume'}, inplace = True)
candles['date'] = pd.to_datetime(candles['date'], unit='s')

print(candles.tail(5))

# speed test reading 1000x 100 bars and measure time elapsed
# on this machine it takes about 1.3 seconds for 1000 reads
print(datetime.now())
for index in range (0,1000):
    candles = MT_Back.Get_last_x_bars_from_now(instrument='EURUSD', timeframe=MT_Back.get_timeframe_value('M15'), nbrofbars=100)
print(datetime.now())
print('')

# open a market order
new_order = MT_Back.Open_order(
                                instrument='EURUSD',
                                ordertype='buy',
                                volume=0.01,
                                openprice=0.0,
                                slippage=5,
                                magicnumber=500,
                                stoploss=0.0,
                                takeprofit=0.0,
                                comment='demo',
                                open_log='trial')

if (new_order > 0):
    log.debug('Market order opened with ticket: ' + str(new_order))


# increment x ticks/M1 bars
MT_Back.Go_x_increments_forwards(increments = 500)                      # about 6 hours   

# check open positions
open_positions = MT_Back.Get_all_open_positions()

# convert date 
open_positions['open_time'] = pd.to_datetime(open_positions['open_time'], unit='s')
print(open_positions)
print('')

# close position
MT_Back.Close_position_by_ticket(ticket=new_order, close_log='manual close')

# check for closed positions
closed_positions = MT_Back.Get_all_closed_positions()
closed_positions['open_time'] = pd.to_datetime(closed_positions['open_time'], unit='s')
closed_positions['close_time'] = pd.to_datetime(closed_positions['close_time'], unit='s')
print(closed_positions)


MT_Back.Disconnect()

