import can
from .helper import byte_arr_to_hex, hex_to_decimal, hex_to_byte_arr, byte_arr_to_dec

class ECU:
    ''' virtual class ECU which everything should inherit from  '''
    _ecu_id = 0
    _state = "error-active" # state of the ECU, is either error-active, error passive or bus off.
    # Transmit Error Counter when > 128 and < 255 passive error. When 
    # the counter is less then 128 then the state should be active error and
    #finally buss off when it is 255. transmit error gives 8 points.
    _TEC = 0

    def __init__(self):
        _state = "error-active"

    def get_id(self):
        return self._ecu_id
    
    def get_state(self):
        return self._state

    def get_tec(self):
        return self._TEC

class Engine(ECU):
    ''' Engine class is a subclass of ECU, here it is hard-coded to the values
    of a Acura ILX 2016. The information about it was extract from the opendbc
    github project. The "engine" ECU should be speed and not rpm, eg: output is
    in km/h'''
    def  __init__(self, ecu_id=344):
        super().__init__()
        self._current_speed = 0 # speed vals are in km/h
        self._initial_speed = 0
        self._ecu_id = ecu_id
    
    # generates a message to be sent over the can bus
    def gen_message(self, dec):
        '''Generates a message to be send over the can bus, takes in the data in 
        the form of a list for now it takes the id of the engine which is hard
        coded. Takes in a decimal representing km/h.'''
        return can.Message(arbitration_id=836, data=self._speed_data(dec))
        
    def _extract_speed(self, can_message):
        ''' Takes a can message and returns the hex of the speed '''
        print(hex_to_decimal(byte_arr_to_hex(can_message.data)))

    def get_speed(self):
        return int(self._current_speed)

    def _speed_data(self, dec):
        ''' takes a decimal that represents the speed and sends the data to a 
        can bus after converting the decimal to a hexadecimal and loading the 
        array. To be used in a can frame. Takes in a decimal rep km/h. * 100 
        because the dbc file specifies 0.01 as the scale. '''
        return hex_to_byte_arr(hex(int(dec*100)))

    def set_speed(self, dec):
        ''' takes a decimal and sets the speed value to it. '''
        self._current_speed = dec
    
    def recv_can(self, msg):
        print("recv got ", msg)
        self._current_speed = int(byte_arr_to_hex(msg),16) * 0.01

class Fake(Engine):
    ''' For now hard code the perpetrator to the engine since it is the only
    ECU. The name fake is there to imply that the ECU is not part of the "real"
    list of ECUs within a car. '''
    def __init__(self, ecu_id = 430):
        super().__init__()
        self._attack_mode = "" # represent different attacking modes here. For now the 
                               # supported modes are "DOS" and "BUS-OFF".
        _current_speed = None

