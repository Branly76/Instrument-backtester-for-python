import socket
import numpy as np
import pandas as pd
import math
from datetime import datetime


ERROR_DICT = {}
ERROR_DICT['00101'] = 'IP address error'
ERROR_DICT['00102'] = 'Port number error'
ERROR_DICT['00103'] = 'Connection error with license EA'
ERROR_DICT['00104'] = 'Undefined answer from license EA'
ERROR_DICT['00301'] = 'Unknown instrument'
ERROR_DICT['00302'] = 'No instruments defined/configured'
ERROR_DICT['00501'] = 'No instrument defined/configured'
ERROR_DICT['00601'] = 'Data directory name error'
ERROR_DICT['01001'] = 'Error in account settings'
ERROR_DICT['01101'] = 'Instrument already done'
ERROR_DICT['01102'] = 'Error in one of the settings'
ERROR_DICT['01103'] = 'Unknown instrument'
ERROR_DICT['01301'] = 'In demo mode not all instruments can be configured'
ERROR_DICT['01302'] = 'Reset first the back tester'
ERROR_DICT['01303'] = 'Can set instruments only once, first reset the back tester'
ERROR_DICT['01304'] = 'Error in creating data factory'
ERROR_DICT['01305'] = 'Error in reading the M1 bar data from file'
ERROR_DICT['01306'] = 'Data file does not exist'
ERROR_DICT['01501'] = 'Wrong low spread value'
ERROR_DICT['01502'] = 'Wrong high spread value' 
ERROR_DICT['01601'] = 'Index > 0'
ERROR_DICT['01602'] = 'Index wrong type'
ERROR_DICT['01603'] = 'No instruments defined'
ERROR_DICT['01604'] = 'index > max bars'
ERROR_DICT['01605'] = 'Undefined error'
ERROR_DICT['01901'] = 'Wrong time frame value'
ERROR_DICT['04101'] = 'Unknown instrument'
ERROR_DICT['04201'] = 'History to short for the requested amount of bars'
ERROR_DICT['04202'] = 'No data available, instrument not defined!!!'
ERROR_DICT['04203'] = 'Error in start bar value' 
ERROR_DICT['04204'] = 'Error in number of bar value' 
ERROR_DICT['04205'] = 'Error in max bar value' 
ERROR_DICT['07001'] = 'Instrument not defined' 
ERROR_DICT['07002'] = 'Error unknown' 
ERROR_DICT['07003'] = 'Wrong lot size' 
ERROR_DICT['07004'] = 'Order type unknown'
ERROR_DICT['07005'] = 'Error in one of the parameters' 
ERROR_DICT['07006'] = 'Wrong TP value' 
ERROR_DICT['07007'] = 'Wrong SL value'
ERROR_DICT['07101'] = 'Position not found'
ERROR_DICT['07301'] = 'Order not found'
ERROR_DICT['07501'] = 'Error in sl or tp value, not real values' 
ERROR_DICT['07502'] = 'Position not found'
ERROR_DICT['07506'] = 'Wrong TP value' 
ERROR_DICT['07507'] = 'Wrong SL value'
ERROR_DICT['07601'] = 'Error in sl or tp value, not real values'
ERROR_DICT['07602'] = 'Order not found'
ERROR_DICT['07606'] = 'Wrong TP value' 
ERROR_DICT['07607'] = 'Wrong SL value'
ERROR_DICT['07701'] = 'Error in sl or tp value, not real values'
ERROR_DICT['07702'] = 'Position not found'
ERROR_DICT['07801'] = 'Error in sl or tp value, not real values'
ERROR_DICT['07802'] = 'Order not found'  
ERROR_DICT['50001'] = 'Error in comma/dot function' 
ERROR_DICT['50101'] = 'Instrument not defined'
ERROR_DICT['50102'] = 'Undefined error'  

class Pytrader_BT_API:

    def __init__(self):
        self.socket_error: int = 0
        self.socket_error_message: str = ''
        self.order_return_message: str = ''
        self.order_error: int = 0
        self.connected: bool = False
        self.timeout: bool = False
        self.command_OK: bool = False
        self.command_return_error: str = ''
        self.debug: bool = False
        self.version: str = '1.00'
        self.max_bars: int = 25000
        self.max_ticks: int = 5000
        self.timeout_value: int = 120
        self.instrument_conversion_list: dict = {}
        self.instrument_name_broker: str = ''
        self.instrument_name_universal: str = ''
        self.date_from: datetime = '2000/01/01, 00:00:00'
        self.date_to: datetime = datetime.now()
        self.invert_array: bool = False
        self.data_directory: str = None

        self.error_dict: dict = {}
        self.license: str = 'Demo'

    def Disconnect(self):
        """Closes the socket connection to a MT4 or MT5 EA bot.

        Args:
            None
        Returns:
            bool: True or False
        """

        self.sock.close()
        return True

    def Connect(self,
                server: str = '',
                port: int = 8888,
                instrument_lookup: dict = []) -> bool:
        """
        Connects to BT.

        Args:
            server: Server IP address, like -> '127.0.0.1', '192.168.5.1'
            port: port number
            instrument_lookup: dictionairy with general instrument names and broker intrument names
        Returns:
            bool: True or False
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        self.port = port
        self.server = server
        self.instrument_conversion_list = instrument_lookup

        if (len(self.instrument_conversion_list) == 0):
            print('Broker Instrument list not available or empty')
            self.socket_error_message = 'Broker Instrument list not available'
            return False

        try:
            self.sock.connect((self.server, self.port))
            try:
                data_received = self.sock.recv(1000000).decode()
                self.connected = True
                self.socket_error = 0
                self.socket_error_message = ''
                print(data_received)
                return True
            except socket.error as msg:
                self.socket_error = 100
                self.socket_error_message = 'Could not connect to server.'
                self.connected = False
                return False
        except socket.error as msg:
            print(
                "Couldnt connect with the socket-server: %self.sock\n terminating program" %
                msg)
            self.connected = False
            self.socket_error = 101
            self.socket_error_message = 'Could not connect to server.'
            return False
 
    def Check_connection(self) -> bool:

        """
        Checks if connection with MT terminal/Ea bot is still active.
        Args:
            None
        Returns:
            bool: True or False
        """
        self.command = 'F000#0#'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False
        
        if self.debug:
            print(dataString)

        x = dataString.split('#')

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
        else:
            self.timeout = False
            self.command_OK = True
            return False
    
    def Set_timeout(self,
                    timeout_in_seconds: int = 60
                    ):
        """
        Set time out value for socket communication with BT.

        Args:
            timeout_in_seconds: the time out value
        Returns:
            True
        """
        self.timeout_value = timeout_in_seconds
        return True

    @property
    def IsConnected(self) -> bool:
        """
        Returns connection status.
        Returns:
            bool: True or False
        """
        return self.connected

    def Set_comma_or_dot(self,
                            mode: str = 'comma') -> bool:
        """
            Sets if the BT must see real values as comma  or dot string
            This is country/culture/region dependend
        Args:
            mode: comma or dot
        Returns:
            bool: True or False
        """
        self.command = 'F500#1#' + str(mode) + "#"
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F500':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        return True

    def Check_license(self, 
                        server: str = '127.0.0.1',
                        port: int = 5555) -> bool:

        """
        Check for license.

        Args:
            server: License Server IP address, like -> '127.0.0.1', '192.168.5.1'
            port: port number, default 5555
        Returns:
            bool: True or False
        """
        self.license = 'Demo'
        self.command = 'F001#2#' + str(server) + "#" + str(port) + '#'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F001':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False        

        self.license = str(x[3])
        return True

    def Set_data_directory(self, 
                            data_directory: str = None) -> bool:

        """
        Set data directory/folder.

        Args:
            data_directory: data directory where BT can find M1 data files
        Returns:
            bool: True or False
        """
        self.data_directory = data_directory
        if (self.data_directory != None):
            self.command = 'F006#1#' + str(self.data_directory) + '#'
            self.command_return_error = ''
            ok, dataString = self.send_command(self.command)
            if not ok:
                self.command_OK = False
                return False

            if self.debug:
                print(dataString)

            x = dataString.split('#')
            if x[0] != 'F006':
                self.command_return_error = ERROR_DICT[str(x[3])]
                self.command_OK = False
                return False
            else:
                return True 

    def Set_bar_date_asc_dec(self,
                                asc_dec: bool = False) -> bool:
        """
        Sets first row of array as first bar or as last bar
        Args:
            asc_dec:    True = row[0] is oldest bar
                        False = row[0] is latest bar
        Returns:
            bool: True or False
        """ 
        self.invert_array = asc_dec
        return True

    def Get_broker_server_time(self) -> datetime:
        """
        Retrieves broker server time.
        Args:
            None
        Returns:
            datetime: Boker time, this is the time of the current M1 bar
        """
        self.command_return_error = ''
        self.command = 'F005#0#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F005':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        y = x[0].split('-')
        d = datetime(int(y[0]), int(y[1]), int(y[2]),
                     int(y[3]), int(y[4]), int(y[5]))
        return d

    def Get_dynamic_account_info(self) -> dict:
            """
            Retrieves dynamic account information.
            Returns: Dictionary with:
                Account balance,
                Account equity,
                Account profit
            """
            self.command_return_error = ''
            ok, dataString = self.send_command('F002#0#')
            if (ok == False):
                self.command_OK = False
                return None

            if self.debug:
                print(dataString)

            x = dataString.split('#')
            if x[0] != 'F002':
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None

            returnDict = {}
            del x[0:2]
            x.pop(-1)

            returnDict['balance'] = float(x[0])
            returnDict['equity'] = float(x[1])
            returnDict['profit'] = float(x[2])

            self.command_OK = True
            return returnDict

    def Set_instrument_list(self,
                        instrument_list: list = ['EURUSD']) -> bool:
        """
        Sets the instruments for the BT

        Args:
            instrument_list: list with instruments
        Returns:
            bool: True or False
        Remark: Now the M1 data file contents are imported in the BT for the specified instruments
        """
        self.command_return_error = ''
        self.command = 'F013#'
        if (len(instrument_list) == 0):
            self.command_return_error = 'empty list'
            return False

        self.command = self.command + str(len(instrument_list)) + '#'

        for element in instrument_list:
            self.command = self.command + element + '#'
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F013':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False   

        self.timeout = True
        self.command_OK = True
        return True

    def Set_timeframes(self,
                    timeframe_list: list = ['M1', 'H1']) -> bool:
        """
        Set the timeframes for the BT to be used

        Args:
            timeframe_list: List with timeframes
        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F019#'
        if (len(timeframe_list) == 0):
            self.command_return_error = 'empty list'
            return False
        
        self.command = self.command + str(len(timeframe_list)) + '#'
        for element in timeframe_list:
            self.command = self.command + element + '#'
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F019':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False        
        
        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
   
    def Set_instrument_parameters(self,
                        instrument: str = 'EURUSD',
                        digits: int = 5,
                        max_lotsize: float = 200.0,
                        min_lotsize: float = 0.01,
                        lot_stepsize: float = 0.01,
                        point: float = 0.00001,
                        tick_size: float = 0.00001,
                        tick_value: float = 1.0,
                        swap_long: float = 0.00,
                        swap_short: float = 0.00) -> bool:
        """
        Set the parameters for an instrument

        Args:
            server: instrument
            digits: number of digits
            max_lotsize: maximum lotsize value
            min_lotsize: minimum lotsize value
            lot_stepsize: minimum lot stepsize increment
            point: poit value
            tick_size: tick size or point value
            tick_value: tick value
            swap_long; swap long/buy value
            swap_short: swap short/sell value
        Returns:
            bool: True or False
        """
        self.command_return_error = ''

        self.command = 'F011#10#' + str(instrument) + '#' + str(digits) + '#' + str(max_lotsize) + '#' + str(min_lotsize) + \
                            "#" + str(lot_stepsize) + "#" + str(point) + "#" + str(tick_size) + "#" + str(tick_value) +  \
                            '#' + str(swap_long) + '#' + str(swap_short) + '#'
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False
        
        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F011':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True

    def Get_instrument_info(self,
                            instrument: str = 'EURUSD') -> dict:
        """
        Retrieves instrument information.

        Args:
            instrument: instrument name
        Returns: Dictionary with:
            instrument,
            digits,
            max_lotsize,
            min_lotsize,
            lot_step,
            point,
            tick_size,
            tick_value
            swap_long
            swap_short
        """

        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none' or self.instrument == None):
            self.command_return_error = 'Instrument not in broker list'
            self.command_OK = False
            return None


        self.command = 'F003#1#' + self.instrument + '#'

        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F003':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        returnDict = {}
        del x[0:2]
        x.pop(-1)

        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['digits'] = int(x[0])
        returnDict['max_lotsize'] = float(x[1])
        returnDict['min_lotsize'] = float(x[2])
        returnDict['lot_step'] = float(x[3])
        returnDict['point'] = float(x[4])
        returnDict['tick_size'] = float(x[5])
        returnDict['tick_value'] = float(x[6])
        returnDict['swap_long'] = float(x[7])
        returnDict['swap_short'] = float(x[8])

        self.command_OK = True
        return returnDict

    def Reset_Backtester_pointers(self) -> bool:
        
        """
        All pointers in the BT will be resetted
        But no new instrument list and no new time frame list can be set
        """
        self.command = 'F009#0#'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
        else:
            self.timeout = False
            self.command_OK = True
            return False
    
    def Reset_Backtester(self) -> bool:
        """
        Reset of backtester.
        After this reset new instrument list can be set
        """
        self.command = 'F008#0#'
        self.command_return_error = ''
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
        else:
            self.timeout = False
            self.command_OK = True
            return False

    def Set_account_characteristics(self,
                        balance: float = 10000.0,
                        max_pendings: int = 50,
                        margin_call: int = 50) -> bool:
        """
        Set account parameters

        Args:
            balance: Start amount of balance, like initial deposit
            max_pendings: maximum number op pending orders
            margin_call: to be defined, at the moment not used
        Returns:
            bool: True or False
        """
        
        self.balance = balance
        self.max_pendings = max_pendings
        self.margin_call = margin_call

        self.command_return_error = ''

        self.command = 'F010#3#' + str(self.balance) + '#' + str(self.max_pendings) + '#' + str(self.margin_call) + '#'
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')

        if x[0] != 'F010':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True

    def Set_spread_and_commission_in_pips(self,
                        instrument: str = 'EURUSD',
                        low_spread_in_pips: float = 1.0,
                        high_spread_in_pips: float = 1.2,
                        commission_in_pips: float = 1.10) -> bool:
        self.low_spread_in_pips = low_spread_in_pips
        self.high_spread_in_pips = high_spread_in_pips
        self.commission_in_pips = commission_in_pips

        """
        Set spread range and commission

        Args:
            instrument: instrument name
            low_spread_in_pips: minimum spread
            high_spread_in_pips: maximum spread
            commission_in_pips: commission for opening and closing a trade
        Returns:
            bool: True or False
        Remark:
            At opening or closing a trade the spread used will have a value between minimum and maximum spread values (random)
        """
        self.command_return_error = ''

        self.command = 'F015#4#' + str(instrument) + "#" + str(self.low_spread_in_pips) + '#' + str(self.high_spread_in_pips) + '#' + str(self.commission_in_pips) + '#'
        ok, dataString = self.send_command(self.command)

        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F015':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
        else:
            self.timeout = False
            self.command_OK = True
            return False

    def Set_index_for_start(self,
                    index: int = 0) -> bool:
        """
        Set the start index for star using the BT

        Args:
            index: moves the pointers in the Bt to this value

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F016#1#' + str(index) + '#'

        ok, dataString = self.send_command(self.command)
        
        if (ok == False):
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F016':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True 
    
    def Go_x_increments_forwards(self,
                    increments: int = 0) -> bool:
        """
        Moves the index/pointers in the BT forwards

        Args:
            increments: pointer for M1 data/bars will be incremented by x
                        all other pointers depends on the time frame
        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F017#1#' + str(increments) + '#'

        ok, dataString = self.send_command(self.command)
        
        if (ok == False):
            self.command_OK = False
            return False
        
        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F017':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return False

        if x[2] == 'OK':
            self.timeout = True
            self.command_OK = True
            return True
    
    def Get_actual_bar_info(self,
                            instrument: str = 'EURUSD',
                            timeframe: int = 16408) -> dict:
        """
        Retrieves instrument last actual data.
        Args:
            instrument: instrument name
            timeframe: time frame like H1, H4
        Returns: Dictionary with:
            instrument name,
            date,
            open,
            high,
            low,
            close,
            volume
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.command = 'F041#2#' + self.get_broker_instrument_name(
            self.instrument_name_universal) + '#' + str(timeframe) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F041':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        returnDict = {}
        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['date'] = int(x[0])
        returnDict['open'] = float(x[1])
        returnDict['high'] = float(x[2])
        returnDict['low'] = float(x[3])
        returnDict['close'] = float(x[4])
        returnDict['volume'] = float(x[5])

        self.command_OK = True
        return returnDict
    
    def Get_last_x_bars_from_now(self,
                                 instrument: str = 'EURUSD',
                                 timeframe: int = 16408,
                                 nbrofbars: int = 1000) -> np.array:
        """
        Retrieves last x bars .

        Args:
            instrument: name of instrument like EURUSD
            timeframe: timeframe like 'H4'
            nbrofbars: Number of bars to retrieve
        Returns: numpy array with:
            date,
            open,
            high,
            low,
            close,
            volume
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.numberofbars = nbrofbars

        dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
                       ('low', np.float64), ('close', np.float64), ('volume', np.int32)])
        rates = np.empty(self.numberofbars, dtype=dt)

        if (self.numberofbars > self.max_bars):
            iloop = self.numberofbars / self.max_bars
            iloop = math.floor(iloop)
            itail = int(self.numberofbars - iloop * self.max_bars)

            for index in range(0, iloop):
                self.command = 'F042#5#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + \
                        str(timeframe) + '#' + str(index * self.max_bars) + '#' + str(self.max_bars) + '#' + str(nbrofbars) + '#'
                ok, dataString = self.send_command(self.command)
                
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F042':
                    self.command_return_error = ERROR_DICT[str(x[3])]
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    rates[value + index * self.max_bars][0] = int(y[0])
                    rates[value + index * self.max_bars][1] = float(y[1])
                    rates[value + index * self.max_bars][2] = float(y[2])
                    rates[value + index * self.max_bars][3] = float(y[3])
                    rates[value + index * self.max_bars][4] = float(y[4])
                    rates[value + index * self.max_bars][5] = float(y[5])

                if (len(x) < self.max_bars):
                    rates = np.sort(rates)
                    self.command_OK = True
                    if (self.invert_array == True):
                        rates = np.sort(rates)
                    return rates

            if (itail == 0):
                rates = np.sort(rates)
                self.command_OK = True
                if (self.invert_array == True):
                    rates = np.sort(rates)
                return rates

            if (itail > 0):
                self.command = 'F042#5#' + self.get_broker_instrument_name(
                    self.instrument_name_universal) + '#' + str(timeframe) + '#' + str(
                    iloop * self.max_bars) + '#' + str(itail) + '#' + str(nbrofbars) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F042':
                    self.command_return_error = ERROR_DICT[str(x[3])]
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    rates[value + iloop * self.max_bars][0] = int(y[0])
                    rates[value + iloop * self.max_bars][1] = float(y[1])
                    rates[value + iloop * self.max_bars][2] = float(y[2])
                    rates[value + iloop * self.max_bars][3] = float(y[3])
                    rates[value + iloop * self.max_bars][4] = float(y[4])
                    rates[value + iloop * self.max_bars][5] = float(y[5])

                self.command_OK = True
                rates = np.sort(rates)
                if (self.invert_array == True):
                    rates = np.sort(rates)
                return rates
        else:
            self.command = 'F042#4#' + str(self.get_broker_instrument_name(self.instrument_name_universal)) + '#' + \
                    str(timeframe) + '#' + str(0) + '#' + str(self.numberofbars) + '#' + str(nbrofbars) + '#'
            #print(self.command)
            ok, dataString = self.send_command(self.command)
            if not ok:
                self.command_OK = False
                print('not ok')
                return None
            if self.debug:
                print(dataString)
                print('')
                print(len(dataString))

            x = dataString.split('#')
            if str(x[0]) != 'F042':
                self.command_return_error = ERROR_DICT[str(x[3])]
                self.command_OK = False
                return None

            del x[0:2]
            x.pop(-1)

            for value in range(0, len(x)):
                y = x[value].split('$')

                rates[value][0] = int(y[0])
                rates[value][1] = float(y[1])
                rates[value][2] = float(y[2])
                rates[value][3] = float(y[3])
                rates[value][4] = float(y[4])
                rates[value][5] = float(y[5])

        self.command_OK = True
        if (self.invert_array == True):
            rates = np.sort(rates)
        return rates

    def Get_last_x_renko_bars_from_now(self,
                                 instrument: str = 'EURUSD',
                                 nbrofbars: int = 1000) -> np.array:
        """retrieves last x bars from a MT4 or MT5 EA bot.

        Args:
            instrument: name of instrument like EURUSD
            nbrofbars: Number of bars to retrieve
        Returns: numpy array with:
            date,
            open,
            high,
            low,
            close,
            volume
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.numberofbars = nbrofbars

        dt = np.dtype([('date', np.int64), ('open', np.float64), ('high', np.float64),
                       ('low', np.float64), ('close', np.float64), ('volume', np.int32)])
        rates = np.empty(self.numberofbars, dtype=dt)

        if (self.numberofbars > self.max_bars):
            iloop = self.numberofbars / self.max_bars
            iloop = math.floor(iloop)
            itail = int(self.numberofbars - iloop * self.max_bars)
            #print('iloop: ' + str(iloop))
            #print('itail: ' + str(itail))

            for index in range(0, iloop):
                self.command = 'F142#5#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + \
                        str(index * self.max_bars) + '#' + str(self.max_bars) + '#' + str(nbrofbars) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F042':
                    self.command_return_error = str(x[2])
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    rates[value + index * self.max_bars][0] = int(y[0])
                    rates[value + index * self.max_bars][1] = float(y[1])
                    rates[value + index * self.max_bars][2] = float(y[2])
                    rates[value + index * self.max_bars][3] = float(y[3])
                    rates[value + index * self.max_bars][4] = float(y[4])
                    rates[value + index * self.max_bars][5] = float(y[5])

                if (len(x) < self.max_bars):
                    rates = np.sort(rates)
                    self.command_OK = True
                    if (self.invert_array == True):
                        rates = np.sort(rates)
                    return rates

            if (itail == 0):
                rates = np.sort(rates)
                self.command_OK = True
                if (self.invert_array == True):
                    rates = np.sort(rates)
                return rates

            if (itail > 0):
                self.command = 'F142#5#' + self.get_broker_instrument_name(
                    self.instrument_name_universal) + '#' + str(iloop * self.max_bars) + \
                    '#' + str(itail) + '#' + str(nbrofbars) + '#'
                ok, dataString = self.send_command(self.command)
                if not ok:
                    self.command_OK = False
                    return None
                if self.debug:
                    print(dataString)
                    print('')
                    print(len(dataString))

                x = dataString.split('#')
                if str(x[0]) != 'F042':
                    self.command_return_error = str(x[2])
                    self.command_OK = False
                    return None

                del x[0:2]
                x.pop(-1)

                for value in range(0, len(x)):
                    y = x[value].split('$')

                    rates[value + iloop * self.max_bars][0] = int(y[0])
                    rates[value + iloop * self.max_bars][1] = float(y[1])
                    rates[value + iloop * self.max_bars][2] = float(y[2])
                    rates[value + iloop * self.max_bars][3] = float(y[3])
                    rates[value + iloop * self.max_bars][4] = float(y[4])
                    rates[value + iloop * self.max_bars][5] = float(y[5])

                self.command_OK = True
                rates = np.sort(rates)
                if (self.invert_array == True):
                    rates = np.sort(rates)
                return rates
        else:
            self.command = 'F142#4#' + str(self.get_broker_instrument_name(self.instrument_name_universal)) + '#' + \
                    str(0) + '#' + str(self.numberofbars) + '#' + str(nbrofbars) + '#'
            #print(self.command)
            ok, dataString = self.send_command(self.command)
            if not ok:
                self.command_OK = False
                print('not ok')
                return None
            if self.debug:
                print(dataString)
                print('')
                print(len(dataString))

            x = dataString.split('#')
            if str(x[0]) != 'F142':
                self.command_return_error = str(x[2])
                self.command_OK = False
                return None

            del x[0:2]
            x.pop(-1)

            for value in range(0, len(x)):
                y = x[value].split('$')

                rates[value][0] = int(y[0])
                rates[value][1] = float(y[1])
                rates[value][2] = float(y[2])
                rates[value][3] = float(y[3])
                rates[value][4] = float(y[4])
                rates[value][5] = float(y[5])

        self.command_OK = True
        if (self.invert_array == True):
            rates = np.sort(rates)
        return rates

    def Get_last_tick_info(self,
                           instrument: str = 'EURUSD') -> dict:
        """
        Retrieves instrument last tick data.
        Backtester bid and ask are same. 
        All data are the last M1 bar

        Args:
            instrument: instrument name
        Returns: Dictionary with:
            instrument name,
            date,
            ask,
            bid,
            last,
            volume,
            spread
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        if (self.instrument == 'none'):
            self.command_return_error = 'Instrument not in list'
            self.command_OK = False
            return None
        ok, dataString = self.send_command('F020#1#' + self.instrument + '#')

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if x[0] != 'F020':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        returnDict = {}
        del x[0:2]
        x.pop(-1)

        returnDict['instrument'] = str(self.instrument_name_universal)
        returnDict['date'] = int(x[0])
        returnDict['ask'] = float(x[1])
        returnDict['bid'] = float(x[2])
        returnDict['last'] = float(x[3])
        returnDict['volume'] = int(x[4])
        returnDict['spread'] = float(x[5])

        self.command_OK = True
        return returnDict

    def Get_specific_bar(self,
                                instrument_list: list = ['EURUSD', 'GBPUSD'],
                                specific_bar_index: int = 1,
                                timeframe: int = 16408) -> dict:
        """
        Retrieves instrument data(d, o, h, l, c, v) of one bar(index) for the instruments in the list.
        Args:
            instrument: instrument name
            specific_bar_index: the specific bar (0 = actual bar)
            timeframe: time frame like H1, H4
        Returns: Dictionary with:       {instrument:{instrument data}}
            instrument name,
            [date,
            open,
            high,
            low,
            close,
            volume]
        """
        self.command_return_error = ''
        # compose MT5 command string
        self.command = 'F045#3#'
        for index in range (0, len(instrument_list), 1):
            _instr = self.get_broker_instrument_name(instrument_list[index].upper())
            self.command = self.command + _instr + '$'
        
        self.command = self.command + '#' + str(specific_bar_index) + '#' + str(timeframe) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F045':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None

        del x[0:2]
        x.pop(-1)
        result = {}
        
        for value in range(0, len(x)):
            y = x[value].split('$')
            symbol_result = {}
            symbol = str(y[0])
            symbol_result['date'] = int(y[1])
            symbol_result['open'] = float(y[2])
            symbol_result['high'] = float(y[3])
            symbol_result['low'] = float(y[4])
            symbol_result['close'] = float(y[5])
            symbol_result['volume'] = float(y[6])
            result[symbol] = symbol_result
        
        return result
    
    def Save_renko_bars_to_file(self,
                                    instrument: str = 'EURUSD',
                                    filename: str = 'temp.csv') -> bool:
        self.command_return_error = ''
        # compose MT5 command string
        self.instrument_name_universal = instrument.upper()
        self.command = 'F150#2#'
        self.command = self.command + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + str(filename) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F150':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return False
        
        return True

    def Save_bars_to_file(self,
                            instrument: str = 'EURUSD',
                            timeframe: int = 16408,
                            filename: str = 'temp.csv') -> bool:

        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        # compose MT5 command string
        self.command = 'F154#3#'
        self.command = self.command + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + str(timeframe) + '#' + str(filename) + '#'
        ok, dataString = self.send_command(self.command)

        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F150':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return False
        
        return True

    def Get_all_orders(self) -> pd.DataFrame:
        """
        retrieves all pending orders.
        Args:

        Returns:
            data array(panda) with all order information:
            ticket,
            instrument,
            order_type,
            magic number,
            volume/lotsize,
            open price,
            stopp_loss,
            take_profit,
            comment
        """
        self.command = 'F060#0#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        orders = self.create_empty_DataFrame(self.columnsOpenOrders, 'id')
        x = dataString.split('#')
     
        '''
        if str(x[0]) != 'F060':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None 
        '''

        del x[0:2]
        x.pop(-1)

        for value in range(0, len(x)):
            y = x[value].split('$')

            rowOrders = pd.Series({
                    'ticket': int( y[0]), 'instrument': self.get_universal_instrument_name(str(y[1])), 'order_type': str(y[2]), 'magic_number': int(y[3]), 
                    'volume': float( y[4]), 'open_price': float( y[5]), 'open_time': int(y[6]), 'stop_loss': float( y[7]), 'take_profit': float( y[8]), 'comment': str(y[9])})
            orders = orders.append(rowOrders, ignore_index=True)

        self.command_OK = True
        return orders

    def Get_all_open_positions(self) -> pd.DataFrame:
        """
        retrieves all open positions.
        Args:

        Returns:
            data array(panda) with all position information:
            ticket,
            instrument,
            position_type,
            magic_number,
            volume/lotsize,
            open_price,
            open_time,
            stopp_loss,
            take_profit,
            comment,
            profit,
            swap,
            commission
            dd_min
            dd_plus
        """
        self.command_return_error = ''
        self.command = 'F061#0#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        positions = self.create_empty_DataFrame(
            self.columnsOpenPositions, 'id')
        x = dataString.split('#')

        '''
        if (str(x[0]) != 'F061'):
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None
        '''

        del x[0:2]
        x.pop(-1)

        for value in range(0, len(x)):
            y = x[value].split('$')

            rowPositions = pd.Series(
                {
                    'ticket': int( y[0]), 'instrument': self.get_universal_instrument_name( (y[1])), 'position_type': str( y[2]), 
                    'magic_number': int(y[3]), 'volume': float( y[4]), 'open_price': float( y[5]), 'open_time': int(y[6]),
                     'stop_loss': float( y[7]), 'take_profit': float( y[8]), 'comment': str( y[9]), 'profit': float( y[10]), 
                     'swap': float( y[11]), 'commission': float( y[12]), 'dd_min': float(y[13]), 'dd_plus': float(y[14])})
            positions = positions.append(rowPositions, ignore_index=True)

        self.command_OK = True
        return positions

    def Get_all_closed_positions(self
                                 ):
        """
        retrieves all closed positions/orders.
        Args:
            None
        Returns:
            data array(panda) with all position information:
            position ticket,
            instrument,
            order_ticket,
            position_type,
            magic number,
            volume/lotsize,
            open price,
            open time,
            close_price,
            close_time,
            comment,
            profit,
            swap,
            commission,
            open_log,
            close_log,
            dd_min,
            dd_plus
        """
        self.command_return_error = ''

        self.command = 'F062#0#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        closed_positions = self.create_empty_DataFrame(
            self.columnsClosedPositions, 'id')
        x = dataString.split('#')

        '''
        if str(x[0]) != 'F062':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None
        '''

        del x[0:2]
        x.pop(-1)
        for value in range(0, len(x)):
            y = x[value].split('$')
            rowClosedPositions = pd.Series(
                {
                    'position_ticket': int(y[0]), 'instrument': self.get_universal_instrument_name(str( y[1])), 'order_ticket': int( y[2]), 
                    'position_type': str( y[3]), 'magic_number': int( y[4]), 'volume': float( y[5]), 'open_price': float( y[6]), 
                    'open_time': int( y[7]), 'close_price': float(y[8]), 'close_time': int( y[9]), 'sl': float(y[10]), 'tp': float(y[11]), 'comment': str( y[12]), 
                    'profit': float( y[13]), 'swap': float( y[14]), 'commission': float( y[15]), 'open_log': str(y[16]), 'close_log': str(y[17]),
                    'dd_min': float(y[18]), 'dd_plus': float(y[19])})
            closed_positions = closed_positions.append(rowClosedPositions, ignore_index=True)

        return closed_positions

    def Get_last_x_closed_positions(self, 
                        amount: int = 3
                                 ):
        """
        retrieves last x closed positions/orders.
        Args:
            None
        Returns:
            data array(panda) with all position information:
            position ticket,
            instrument,
            order_ticket,
            position_type,
            magic number,
            volume/lotsize,
            open price,
            open time,
            close_price,
            close_time,
            comment,
            profit,
            swap,
            commission,
            position open comment,
            position close comment
            dd_min
            dd_plus
        """
        self.command_return_error = ''

        self.command = 'F063#1#' + str(amount) + '#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)

        closed_positions = self.create_empty_DataFrame(
            self.columnsClosedPositions, 'id')
        x = dataString.split('#')
        if str(x[0]) != 'F063':
            self.command_return_error = str(x[2])
            self.command_OK = False
            return None
        
        if (int(x[1]) == 0):
            return closed_positions
        
        del x[0:2]
        x.pop(-1)
        for value in range(0, len(x)):
            y = x[value].split('$')
            rowClosedPositions = pd.Series(
                {
                    'position_ticket': int(y[0]), 'instrument': self.get_universal_instrument_name(str( y[1])), 'order_ticket': int( y[2]), 
                    'position_type': str( y[3]), 'magic_number': int( y[4]), 'volume': float( y[5]), 'open_price': float( y[6]), 
                    'open_time': int( y[7]), 'close_price': float(y[8]), 'close_time': int( y[9]), 'sl': float(y[10]), 'tp': float(y[11]), 'comment': str( y[12]), 
                    'profit': float( y[13]), 'swap': float( y[14]), 'commission': float( y[15]), 'open_log': str(y[16]), 'close_log': str(y[17]),
                    'dd_min': float(y[18]), 'dd_plus': float(y[19])})
            closed_positions = closed_positions.append(
                rowClosedPositions, ignore_index=True)

        return closed_positions

    def Open_order(self,
                   instrument: str = '',
                   ordertype: str = 'buy',
                   volume: float = 0.01,
                   openprice: float = 0.0,
                   slippage: int = 5,
                   magicnumber: int = 0,
                   stoploss: float = 0.0,
                   takeprofit: float = 0.0,
                   comment: str = '',
                   open_log: str = ''
                   ) -> int:
        """
        Open an order.
        Args:
            instrument: instrument
            ordertype: type of order, buy, sell, buy stop, sell stop, buy limit, sell limit
            volume: order volume/lot size
            open price: open price for order, 0.0 for market orders
            slippage: allowed slippage
            magicnumber: magic number for this order
            stoploss: order stop loss price, actual price, so not relative to open price
            takeprofit: order take profit, actual price, so not relative to open price
            comment: order comment
            open_log: additional comment for opening the order
        Returns:
            int: ticket number. If -1, open order failed
        """

        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        # check the command for '#' , '$', '!' character
        # these are not allowed, used as delimiters
        comment.replace('#', '')
        comment.replace('$', '')
        comment.replace('!', '')
        self.command = 'F070#10#' + self.get_broker_instrument_name(self.instrument_name_universal) + '#' + ordertype + '#' + str(volume) + '#' + \
            str(openprice) + '#' + str(slippage) + '#' + str(magicnumber) + '#' + str(stoploss) + '#' + str(takeprofit) + '#' + str(comment) + '#' + str(open_log) + "#"
        #print(self.command)
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return int(-1)

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F070':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = int(x[3])
            return int(-1)

        self.command_OK = True
        self.order_return_message = str(x[2])
        return int(x[3])

    def Close_position_by_ticket(self,
                                 ticket: int = 0,
                                 close_log: str = '') -> bool:
        """
        Close a position.
        Args:
            ticket: ticket of position to close
            close_log: reason for closing position

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F071#2#' + str(ticket) + '#' + str(close_log) + '#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        '''
        if str(x[0]) != 'F071':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            self.order_error = str(x[3])
            return False
        '''
        if str(x[2]) == 'OK':
            self.command_OK = True
            self.order_return_message = ''
            return True
        elif str(x[2]) == 'NOK':
            self.command_OK = True
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False
        
        return False 

    def Delete_order_by_ticket(self,
                               ticket: int = 0) -> bool:
        """
        Delete an order.
        Args:
            ticket: ticket of order(pending) to delete

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F073#1#' + str(ticket) + '#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        
        if str(x[2]) == 'OK':
            self.command_OK = True
            self.order_return_message = ''
            return True
        elif str(x[2]) == 'NOK':
            self.command_OK = True
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False
        return False   

    def Set_sl_and_tp_for_position(self,
                                   ticket: int = 0,
                                   stoploss: float = 0.0,
                                   takeprofit: float = 0.0) -> bool:
        """
        Change stop loss and take profit for a position.
        Args:
            ticket: ticket of position to change
            stoploss; new stop loss value, must be actual price value
            takeprofit: new take profit value, must be actual price value

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F075#3#' + \
            str(ticket) + '#' + str(stoploss) + '#' + str(takeprofit) + '#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F075':
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False

        self.command_OK = True
        return True

    def Set_sl_and_tp_for_order(self,
                                ticket: int = 0,
                                stoploss: float = 0.0,
                                takeprofit: float = 0.0) -> bool:
        """
        Change stop loss and take profit for an order.
        Args:
            ticket: ticket of order to change
            stoploss; new stop loss value, must be actual price value
            takeprofit: new take profit value, must be actual price value

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F076#3#' + \
            str(ticket) + '#' + str(stoploss) + '#' + str(takeprofit) + '#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F076':
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False

        self.command_OK = True
        return True

    def Reset_sl_and_tp_for_position(self,
                                ticket: int = 0) -> bool:
        """
        Reset stop loss and take profit for a position.
        Args:
            ticket: ticket of position to change

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F077#1#' + str(ticket) + '#' 
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F077':
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False

        self.command_OK = True
        return True

    def Reset_sl_and_tp_for_order(self,
                                ticket: int = 0) -> bool:
        """
        Reset stop loss and take profit for an order.
        Args:
            ticket: ticket of order to change


        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F078#1#' + str(ticket) + '#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F078':
            self.command_OK = False
            self.order_return_message = ERROR_DICT[str(x[3])]
            return False

        self.command_OK = True
        return True

    def Reset_order_lists(self) -> bool:
        
        """
        Reset orders lists for speed, only effective for big history of trades

        Returns:
            bool: True or False
        """
        self.command_return_error = ''
        self.command = 'F080#1#'
        ok, dataString = self.send_command(self.command)
        
        if not ok:
            self.command_OK = False
            return False

        if self.debug:
            print(dataString)

        x = dataString.split('#')
        if str(x[0]) != 'F080':
            self.command_return_error = str(x[2])
            self.command_OK = False
            self.order_return_message = str(x[2])
            return False

        return True

    def Get_datafactory_info(self,
                                instrument: str = "EURUSD") -> dict:

        """
        Retrieve data factory info

        Args:
            instrument: instrument name
        Returns: Dictionary with
            instrument
            number_of_bars (M1)
            start_date
            end_date
        """
        self.command_return_error = ''
        self.instrument_name_universal = instrument.upper()
        self.instrument = self.get_broker_instrument_name(self.instrument_name_universal)
        self.command = "F501#1#" + self.instrument + "#"

        ok, dataString = self.send_command(self.command)
        if not ok:
            self.command_OK = False
            return None

        if self.debug:
            print(dataString)
        
        returnDict = {}
        x = dataString.split('#')
        if x[0] != 'F501':
            self.command_return_error = ERROR_DICT[str(x[3])]
            self.command_OK = False
            return None
        
        del x[0:2]
        x.pop(-1)
        returnDict['instrument'] = str(x[0])
        returnDict['number_of_bars'] = int(x[1])
        returnDict['start_date'] =  datetime.fromtimestamp(int(x[2]))
        returnDict['end_date'] =  datetime.fromtimestamp(int(x[3]))

        return returnDict

    def send_command(self,
                     command):
        self.command = command + "!"
        self.timeout = False
        #self.sock.send(bytes(self.command, "utf-8"))
        if (self.connected == False):
            return False, None
        
        try:
            data_received = ''
            self.sock.send(bytes(self.command, "utf-8"))
            while True:
                data_received = data_received + self.sock.recv(500000).decode()
                if data_received.endswith('!'):
                    break
            return True, data_received
        except socket.timeout as msg:
            self.timeout = True
            print(msg)
            return False, None
         
    def get_timeframe_value(self,
                            timeframe: str = 'D1') -> int:

        self.tf = 16408  # mt5.TIMEFRAME_D1
        timeframe.upper()
        if timeframe == 'MN1':
            self.tf = 49153  # mt5.TIMEFRAME_MN1
        if timeframe == 'W1':
            self.tf = 32769  # mt5.TIMEFRAME_W1
        if timeframe == 'D1':
            self.tf = 16408  # mt5.TIMEFRAME_D1
        if timeframe == 'H12':
            self.tf = 16396  # mt5.TIMEFRAME_H12
        if timeframe == 'H8':
            self.tf = 16392  # mt5.TIMEFRAME_H8
        if timeframe == 'H6':
            self.tf = 16390  # mt5.TIMEFRAME_H6
        if timeframe == 'H4':
            self.tf = 16388  # mt5.TIMEFRAME_H4
        if timeframe == 'H3':
            self.tf = 16387  # mt5.TIMEFRAME_H3
        if timeframe == 'H2':
            self.tf = 16386  # mt5.TIMEFRAME_H2
        if timeframe == 'H1':
            self.tf = 16385  # mt5.TIMEFRAME_H1
        if timeframe == 'M30':
            self.tf = 30  # mt5.TIMEFRAME_M30
        if timeframe == 'M20':
            self.tf = 20  # mt5.TIMEFRAME_M20
        if timeframe == 'M15':
            self.tf = 15  # mt5.TIMEFRAME_M15
        if timeframe == 'M10':
            self.tf = 10  # mt5.TIMEFRAME_M10
        if timeframe == 'M5':
            self.tf = 5  # mt5.TIMEFRAME_M5
        if timeframe == 'M1':
            self.tf = 1  # mt5.TIMEFRAME_M1

        return self.tf

    def get_broker_instrument_name(self,
                                   instrumentname: str = '') -> str:
        self.intrumentname = instrumentname
        try:
            # str result =
            # (string)self.instrument_conversion_list.get(str(instrumentname))
            return self.instrument_conversion_list.get(str(instrumentname))
        except BaseException:
            return 'none'

    def get_universal_instrument_name(self,
                                      instrumentname: str = '') -> str:
        self.instrumentname = instrumentname
        try:
            for item in self.instrument_conversion_list:
                key = str(item)
                value = self.instrument_conversion_list.get(item)
                if (value == instrumentname):
                    return str(key)
        except BaseException:
            return 'none'
        return 'none'

    def create_empty_DataFrame(self,
                               columns, index_col) -> pd.DataFrame:
        index_type = next((t for name, t in columns if name == index_col))
        df = pd.DataFrame({name: pd.Series(dtype=t) for name,
                           t in columns if name != index_col},
                          index=pd.Index([],
                                         dtype=index_type))
        cols = [name for name, _ in columns]
        cols.remove(index_col)
        return df[cols]

    columnsOpenOrders = [
        ('id', int),
        ('ticket', int),
        ('instrument', str),
        ('order_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('stop_loss', float),
        ('take_profit', float),
        ('comment', str)]

    columnsOpenPositions = [
        ('id', int),
        ('ticket', int),
        ('instrument', str),
        ('position_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('stop_loss', float),
        ('take_profit', float),
        ('comment', str),
        ('profit', float),
        ('swap', float),
        ('commission', float),
        ('dd_min', float),
        ('dd_plus', float)]

    columnsClosedPositions = [
        ('id', int),
        ('position_ticket', int),
        ('instrument', str),
        ('order_ticket', int),
        ('position_type', str),
        ('magic_number', int),
        ('volume', float),
        ('open_price', float),
        ('open_time', int),
        ('close_price', float),
        ('close_time', int),
        ('sl', float),
        ('tp', float),
        ('comment', str),
        ('profit', float),
        ('swap', float),
        ('commission', float),
        ('open_log', str),
        ('close_log', str),
        ('dd_min', float),
        ('dd_plus', float)]

