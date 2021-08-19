

**Instrument backtester (BT)**

The Instrument backtester(BT) is a windows console application, which acts for instance like a MT4/MT5 terminal.

The main characteristics of the BT are:

 - The BT has a history of M1 bars from 2016 onwards (over 5 years) The source is Dukascopy.
 - For the 28 basic instruments data will be available.
 - The data/bars are synchronized. For every instrument same amount of bars and equal dates.
 - Multi instrument/multi time frame strategies can be tested.
 - All time frames are deducted from these M1 bars (M5, M10, M15, M20, M30, H1, H2, H3, H4, H6, H8, H12, D1)
 - Stepping through the history in M1 bar increment or multiple M1 bar increments.
 - Opening & closing of trades (pendings, market).
 - Orders and positions will be updated every increment.
 - Tracking of minimum and maximum profit of open positions.
 - Additional comments for trades, like open conditions and/or close conditions.

Planned:
 - Renko bars and volume bars
 - Red news (FF).


The communication is based on sockets(server/client). The BT is the server and a python script is the client.
The communication with the BT server is all done in a python script "*Pytrader_BT_V1_01.py*" by easy to understand function calls.

For switching to live trading a "*Pytrader_API*" for MT4 and MT5 are available. Function calls are for 95% the same.
For more information see [here](https://github.com/TheSnowGuru/PyTrader-python-mt4-mt5-trading-api-connector-drag-n-drop)

Extended documentation is available and also a "*BT_Demo.py*" in which it is easy to see how to use the system.

There is also a [discord channel](https://discord.gg/zWaBpz3S) for support.

This is a licensed product. In demo EURUSD, USDJPY and AUDNZD work in full function. For a license see [here](https://www.mql5.com/en/market/product/70885?source=Site+Market+MT4+Indicator+Search+Rating005%3aMT4+instrument).
