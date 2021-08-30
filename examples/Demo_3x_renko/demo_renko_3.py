# Example how to use renko bars/candles in the back tester.
# 3 different brick sizes are defined.
# history is build for the backtester, set 200000, to be sure for enough renko candles
# candles are retrieved and put in plotly chart

import numpy as np
import pandas as pd
import configparser
from datetime import datetime
import pytz
from utils.api.Pytrader_BT_API_V1_02 import Pytrader_BT_API
from utils.api.Pytrader_API_V1_06a import Pytrader_API

from utils.utils import Timer
from utils.helper.LogHelper import Logger

from plotly.subplots import make_subplots
import plotly.graph_objects as go

# add a logger for keeping track of what happens
log = Logger()
log.configure(logfile='BT_renko_demo_3.log')

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

MT_Back = Pytrader_BT_API()                                                                                     # back tester instance

# connect to the back tester
Connected = MT_Back.Connect(
    server='127.0.0.1',
    port=10014,
    instrument_lookup=brokerInstrumentsLookup)

print(Connected)
if (Connected):
    log.debug('Connected to back tester.')


# reset the back tester
ok = MT_Back.Reset_backtester()

# check for license, not needed for demo instruments
license = MT_Back.Check_license(server = '127.0.0.1', port = 5555)
log.debug(license)

# the back tester has no account at start, so we have to set a value
# margin call is not used at the moment
ok = MT_Back.Set_account_parameters(balance = 1000.0, max_pendings = 50, margin_call= 50.0)

# set the directory of the M1 data files, In this directory the back trader will look for the M1 data files
ok = MT_Back.Set_data_directory(data_directory='C:\\Temp\\Bar_files\\data_sync')
if (ok == False):
    log.debug('Error in setting data directory')
    log.debug(MT_Back.command_return_error)


# set the comma or dot annotation.
# depending on your country / region reals are written with a dot or a comma
ok = MT_Back.Set_comma_or_dot(mode='comma')

# set bartype
ok = MT_Back.Set_bartype(bar_type='RENKO')

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

log.debug('Connected to MT terminal is: ' + str(Connected))

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

log.debug('Disconnected from MT terminal.')

ok = MT_Back.Set_bartype_parameters_for_renko(brick_list_in_pips=['7.0', '10.0', '12.0'])
log.debug('Renko brick sizes are set: ' + str(ok))

# set the start for building history, in this case 200000 M1 bars from start 2016-01-01
ok = MT_Back.Set_index_for_start(200000)

# retrieve 200 candles for bricksize 1
candles_B1 = MT_Back.Get_last_x_renko_bars_from_now(instrument='EURUSD', brick_code='B1', nbrofbars=200)
if type(candles_B1) != pd.DataFrame:
        candles_B1 = pd.DataFrame(candles_B1)
candles_B1.rename(columns = {'tick_volume':'volume'}, inplace = True)
candles_B1['date'] = pd.to_datetime(candles_B1['date'], unit='s')

# retrieve 150 candles for bricksize 12
candles_B2 = MT_Back.Get_last_x_renko_bars_from_now(instrument='EURUSD', brick_code='B2', nbrofbars=150)
if type(candles_B2) != pd.DataFrame:
        candles_B2 = pd.DataFrame(candles_B2)
candles_B2.rename(columns = {'tick_volume':'volume'}, inplace = True)
candles_B2['date'] = pd.to_datetime(candles_B2['date'], unit='s')

# retrieve 100 candles for bricksize 3
candles_B3 = MT_Back.Get_last_x_renko_bars_from_now(instrument='EURUSD', brick_code='B1', nbrofbars=100)
if type(candles_B3) != pd.DataFrame:
        candles_B3 = pd.DataFrame(candles_B3)
candles_B3.rename(columns = {'tick_volume':'volume'}, inplace = True)
candles_B3['date'] = pd.to_datetime(candles_B3['date'], unit='s')

ok = MT_Back.Disconnect()
log.debug('Disconnected from Back tester')

# create a plotly chart with 3x  renko

fig = make_subplots(
                        rows=1, 
                        cols=3, 
                        #shared_xaxes=True,
                        print_grid=False, 
                        vertical_spacing=0.03,
                        #row_heights=[0.5, 0.25, 0.25]
                    )
fig.add_trace(go.Candlestick(
                                x=candles_B1['date'].index,
                                open=candles_B1["open"],
                                high=candles_B1["high"],
                                low=candles_B1["low"],
                                close=candles_B1["close"],
                                name='Brick size: 7.0',
                                showlegend=True
                            ), 
                            row=1, 
                            col=1
                    )
fig.add_trace(go.Candlestick(
                                x=candles_B2['date'].index,
                                open=candles_B2["open"],
                                high=candles_B2["high"],
                                low=candles_B2["low"],
                                close=candles_B2["close"],
                                name='Brick size 10.0',
                                showlegend=True
                            ), 
                            row=1, 
                            col=2
                    )
                
fig.add_trace(go.Candlestick(
                                x=candles_B3['date'].index,
                                open=candles_B3["open"],
                                high=candles_B3["high"],
                                low=candles_B3["low"],
                                close=candles_B3["close"],
                                name='Brick size: 12.0',
                                showlegend=True
                            ), 
                            row=1, 
                            col=3
                    )

#fig.update(layout_xaxis_rangeslider_visible=False)

fig.update_layout(
                template='plotly_dark',
                margin={
                    "r": 10,
                    "t": 20,
                    "b": 10,
                    "l": 25,
                },
                height=900, #self._height,
                bargap=0.35,
                font={"family": "Raleway", "size": 13},
                plot_bgcolor="#1f2536", 
                paper_bgcolor="#1f2536", 
                autosize=True,
                uirevision=False,
                xaxis={
                    "autorange": True,
                    "showline": True,
                    #"title": "Date",
                    "showgrid": False,
                    "zeroline": False,
                    #"type": "category",
                    "color": "#cccccc",
                },
                yaxis={
                    "autorange": True,
                    "showgrid": False,
                    "showline": True,
                    #"title": "Price",
                    #"type": "linear",
                    "zeroline": True,
                    "color": "#cccccc",
                },)

fig.show()
