

**Instrument backtester (BT)**

The Instrument backtester(BT) is a windows console application, which acts as  a MT4/MT5 terminal.
The main characteristics of the BT are:

 - The BT has a history of M1 bars from 2016 onwards (over 5 years) The source is Dukascopy.
 - For the 28 basic instruments data will be avaialble.
 - The data/bars will be synchronized. For every instrument same amount of bars and equal dates.
 - Multi instrument/multi time frame strategies can be tested.
 - All time frames are deducted from these M1 bars (M5, M10, M15, M20, M30, H1, H2, H3, H4, H6, H8, H12, D1)
 - Stepping through the history in M1 bar increment or multiple M1 bar increments.
 - Orders and positions will be updated every increment.
