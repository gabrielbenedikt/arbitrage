#!/usr/bin/env python3

import serial
import io
import threading

class RangeException(BaseException):
    """Parameter out of range"""
    pass

class DeviceException(BaseException):
    """Unsupported device"""
    pass

class Arbitrage():
    def __init__(self,dev):
        self.readresponse=True
        self.opencon(dev)
        self.info = self.msg('*idn?')
        self.closecon()
        if "AFG-2005" in self.info:
            self.device=AFG2005(dev)
        elif "AFG-2105" in self.info:
            self.device=AFG2105(dev)
        elif "AFG-2012" in self.info:
            self.device=AFG2012(dev)
        elif "AFG-2112" in self.info:
            self.device=AFG2112(dev)
        elif "AFG-2025" in self.info:
            self.device=AFG2025(dev)
        elif "AFG-2125" in self.info:
            self.device=AFG2125(dev)
        else:
            raise DeviceException
            
    def opencon(self,dev):
        self.ser = serial.Serial(port=dev,
                                 baudrate=9600,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=0.1)
        
        self.buf = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 33554432), newline='\r', line_buffering = True)
    
    def closecon(self):
        self.ser.close()

    def msg(self, msg):
        self.buf.write(msg+'\n')
        if self.readresponse:
            lines=self.buf.readlines()
            if len(lines)>0:
                return lines[0].strip()
            else:
                return lines
        else:
            return ['']

class AFGbase():
    def __init__(self,dev):
        self.frequencyrange=dict()
        self.frequencyrange["Triangle"]=(0.1,1*10**6)
        self.frequencyrange["Ramp"]=(0.1,1*10**6)
        self.opencon(dev)
        self.readresponse=True
        self.ser_read_thread=threading.Thread(target=self.ser_read_thread)
        self.ser_read_thread.start()
        
    def opencon(self,dev):
        self.ser = serial.Serial(port=dev,
                                 baudrate=9600,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=0.1)
        
        self.buf = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 33554432), newline='\r', line_buffering = True)
    
    def closecon(self):
        self.ser.close()
        
    def ignore_serial_read(self,ignore):
        self.readresponse= not ignore
    
    def ser_read_thread(self):
        while True:
            if not self.readresponse:
                line=self.buf.readline()

    def msg(self, msg):
        self.buf.write(msg+'\n')
        if self.readresponse:
            lines=self.buf.readlines()
            if len(lines)>0:
                return lines[0].strip()
            else:
                return lines
        else:
            return ['']


    ##############################
    #          COMMANDS          #
    ##############################


    # System commands
    ###################
    def identify(self):
        """Returns the function generator manufacturer, model number, serial number and firmware version number"""
        return self.msg('*idn?')
    
    def reset(self):
        """Reset the function generator to its factory default state"""
        return self.msg('*rst')
    
    def clear(self):
        """clears all the event registers, the error queue and cancels an *OPC command"""
        return self.msg('*rst')
    
    # Apply commands
    ###################
    def apply_func(self, func='SIN', freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output function 'func' at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'func' can be SIN, SQUARE, RAMP, NOISE, USER
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.msg('SOURCE'+str(chan)+':APPLY:'+str(func)+' '+str(freq)+','+str(amp)+','+str(off))
    
    def apply_sine(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output sine function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.apply_func(chan=chan, func='SIN', freq=freq, amp=amp, off=off)
    
    def apply_square(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to outut square function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.apply_func(chan=chan, func='SQUARE', freq=freq, amp=amp, off=off)
        
    def apply_ramp(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output ramp function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.apply_func(chan=chan, func='RAMP', freq=freq, amp=amp, off=off)
    
    def apply_noise(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output noise at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.apply_func(chan=chan, func='NOISE', freq=freq, amp=amp, off=off)
        
    def apply_user(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output stored user function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.apply_func(chan=chan, func='USER', freq=freq, amp=amp, off=off)
    
    def get_apply(self,chan=1):
        """return current function settings"""
        return self.msg('SOURCE'+str(chan)+':APPLY?')
    
    # Function commands
    #####################
    def set_func(self, func='SIN', chan=1):
        """Instructs device to change output function of channen 'chan'
        func can be SIN, SQUARE, RAMP, NOISE, USER"""
        return self.msg('SOURCE'+str(chan)+':FUNC '+str(func))
    
    def get_func(self, chan=1):
        """Returns currently set function"""
        return self.msg('SOURCE'+str(chan)+':FUNC?')
    
    # Frequency commands
    #####################
    def set_freq(self, freq=100, chan=1):
        """Instructs device to change output frequency of channel 'chan'
        frequ can be a number or 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':FREQ '+str(freq))
    
    def get_freq(self, chan=1):
        """Returns currently set frequency"""
        return self.msg('SOURCE'+str(chan)+':FREQ?')
    
    # Amplitude commands
    #####################
    def set_amp(self, amp=0.1, chan=1):
        """Instructs device to change output amplitude of channel 'chan'
        amp can be a number or 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':AMPL '+str(amp))
    
    def get_amp(self, chan=1):
        """Returns currently set amplitude"""
        return self.msg('SOURCE'+str(chan)+':AMPL?')
    
    # DC Offset commands
    #####################
    def set_offset(self, offset=0, chan=1):
        """Instructs device to change output dc offset of channel 'chan'
        offset can be a number or 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':DCO '+str(offset))
    
    def get_offset(self, chan=1):
        """Returns currently set dc offset"""
        return self.msg('SOURCE'+str(chan)+':DCO?')
    
    # SQUARE Duty cycle commands
    #####################
    def set_square_dutycycle(self, duty=50, chan=1):
        """Instructs device to change duty cycle of square function on channel 'chan'
        duty can be a number (in percent) or 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':SQUARE:DCYCLE '+str(duty))
    
    def get_square_dutycycle(self, chan=1):
        """Returns currently set square function duty cycle"""
        return self.msg('SOURCE'+str(chan)+':SQUARE:DCYCLE?')
    
    # RAMP symmetry commands
    #####################
    def set_ramp_symmetry(self, sym=50, chan=1):
        """Instructs device to change symmetry of ramp function on channel 'chan'
        sym can be a number (in percent) or 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':RAMP:SYMM '+str(sym))
    
    def get_ramp_symmetry(self, chan=1):
        """Returns currently set ramp symmetry"""
        return self.msg('SOURCE'+str(chan)+':RAMP:SYMM?')
    
    # output commands
    #####################
    def set_output_enabled(self, enable=False):
        """Turn on or off output"""
        return self.msg('OUTP '+str("ON" if enable else "OFF"))
    
    def get_output_enabled(self):
        """Returns if device output state"""
        return self.msg('OUTP?')
    
    # output load commands
    #####################
    def set_output_load(self, load="DEF"):
        """Set output load to 50ohm (DEF) or HighZ (INF)"""
        if load.upper() in ["DEF","INF"]:
            return self.msg('OUTP:LOAD '+str(load))
        else:
            raise RangeException
    
    def set_output_load_50ohm(self):
        """Set output load to 50ohm"""
        return self.set_output_load(load="DEF")
    
    def set_output_load_high(self):
        """Set output load to HighZohm"""
        return self.set_output_load(load="INF")
    
    def get_output_load(self):
        """Returns if device output load state"""
        return self.msg('OUTP:LOAD?')
    
    # volt units commands
    #####################
    def set_volt_units(self, unit="VPP", chan=1):
        """Set voltage units to Vpp, Vrms of dBm"""
        if unit.upper() in ["VPP","VRMS","DBM"]:
            return self.msg('SOURCE'+str(chan)+':VOLT:UNIT '+str(unit))
        else:
            raise RangeException
    
    def set_volt_units_vpp(self, chan=1):
        """Set voltage units to vpp"""
        return self.set_volt_units(unit="VPP", chan=chan)
    
    def set_volt_units_vrms(self, chan=1):
        """Set voltage units to vrms"""
        return self.set_volt_units(unit="VRMS", chan=chan)
    
    def set_volt_units_dbm(self, chan=1):
        """Set voltage units to vdbm"""
        return self.set_volt_units(unit="DBM", chan=chan)
    
    def get_volt_units(self, chan=1):
        """Returns current output voltage units of channel chan"""
        return self.msg('SOURCE'+str(chan)+':VOLT:UNIT?')
    
    # Save and recall commands
    #####################
    # save and recall commands
    #####################
    def save_state(self, reg=0):
        """Saves current device state to register reg 0-9,
        or saves arbitrary waveform to register reg 10-19"""
        if reg in range(0,20):
            return self.msg('*SAV '+str(reg))
        else:
            raise RangeException
    
    def recall_state(self, reg=0):
        """Loads current device state from register reg 0-9,
        or loads arbitrary waveform from register reg 10-19"""
        if reg in range(0,20):
            return self.msg('*RCL '+str(reg))
        else:
            raise RangeException
        
    # Arbitrary waveform commands
    #####################
    # AW data dac commands
    #####################
    def set_aw_dac(self, block="-511, -206, 0, 206, 511, 206, 0, -206"):
        """Loads 'block' into memory
        block can be:
        -list of values, comma separated. E.g. "-511, -206, 0, 206, 511, 206, 0, -206"
        -binary data: format #216 dat
        where dat is 16 bit binary data"""
        return self.msg('DATA:DAC VOLATILE, 0, '+str(block))


class AFG2000(AFGbase):
    def info(self):
        return("AFG20xx")

class AFG2100(AFGbase):
    def info(self):
        return("AFG21xx")
    
    # AM commands
    #####################
    # AM state commands
    #####################
    def set_am_state(self, enable=True, chan=1):
        """Enables of disables amplitude modulation"""
        return self.msg('SOURCE'+str(chan)+':AM:STATE '+str("ON" if enable else "OFF"))
    
    def get_am_state(self, chan=1):
        """Returns if amplitude modulation is enabled or not"""
        return self.msg('SOURCE'+str(chan)+':AM:STATE?')
    
    # AM source commands
    #####################
    def set_am_source(self, src="INT", chan=1):
        """Sets AM source to INTernal or EXTernal"""
        if src.upper() in ['INT','EXT']:
            return self.msg('SOURCE'+str(chan)+':AM:SOUR '+str(src))
        else:
            raise RangeException
    
    def get_am_state(self, chan=1):
        """Returns current AM source"""
        return self.msg('SOURCE'+str(chan)+':AM:SOUR?')
    
    # AM function commands
    #####################
    def set_am_function(self, func="SIN", chan=1):
        """Sets internal AM source function"""
        if src.upper() in ['SIN','SQUARE','RAMP']:
            return self.msg('SOURCE'+str(chan)+':AM:INT:FUNC '+str(func))
        else:
            raise RangeException
    
    def get_am_function(self, chan=1):
        """Returns current internal AM source function"""
        return self.msg('SOURCE'+str(chan)+':AM:INT:FUNC?')
    
    # AM frequency commands
    #####################
    def set_am_frequency(self, freq=100, chan=1):
        """Sets internal AM function frequenc. Can be number or MIN or MAX"""
        return self.msg('SOURCE'+str(chan)+':AM:INT:FREQ '+str(freq))
        
    def get_am_frequency(self, chan=1):
        """Returns current internal AM function frequency"""
        return self.msg('SOURCE'+str(chan)+':AM:INT:FREQ?')
    
    # AM depth commands
    #####################
    def set_am_depth(self, depth=100, chan=1):
        """Sets AM depth in percent (0-120). Can be number or MIN or MAX"""
        return self.msg('SOURCE'+str(chan)+':AM:DEPT '+str(depth))
        
    def get_am_depth(self, chan=1):
        """Returns current AM depth"""
        return self.msg('SOURCE'+str(chan)+':AM:DEPT?')
    
    # FM commands
    #####################
    # FM state commands
    #####################
    def set_fm_state(self, enable=True, chan=1):
        """Enables of disables frequency modulation"""
        return self.msg('SOURCE'+str(chan)+':FM:STATE '+str("ON" if enable else "OFF"))
    
    def get_fm_state(self, chan=1):
        """Returns if frequency modulation is enabled or not"""
        return self.msg('SOURCE'+str(chan)+':FM:STATE?')
    
    # FM source commands
    #####################
    def set_fm_source(self, src="INT", chan=1):
        """Sets FM source to INTernal or EXTernal"""
        if src.upper() in ['INT','EXT']:
            return self.msg('SOURCE'+str(chan)+':FM:SOUR '+str(src))
        else:
            raise RangeException
    
    def get_fm_state(self, chan=1):
        """Returns current FM source"""
        return self.msg('SOURCE'+str(chan)+':FM:SOUR?')
    
    # FM function commands
    #####################
    def set_fm_function(self, func="SIN", chan=1):
        """Sets internal FM source function"""
        if src.upper() in ['SIN','SQUARE','RAMP']:
            return self.msg('SOURCE'+str(chan)+':FM:INT:FUNC '+str(func))
        else:
            raise RangeException
    
    def get_fm_function(self, chan=1):
        """Returns current internal FM source function"""
        return self.msg('SOURCE'+str(chan)+':FM:INT:FUNC?')
    
    # FM frequency commands
    #####################
    def set_fm_frequency(self, freq=100, chan=1):
        """Sets internal FM function frequenc. Can be number or MIN or MAX"""
        return self.msg('SOURCE'+str(chan)+':FM:INT:FREQ '+str(freq))
        
    def get_fm_frequency(self, chan=1):
        """Returns current internal FM function frequency"""
        return self.msg('SOURCE'+str(chan)+':FM:INT:FREQ?')
    
    # FM deviation commands
    #####################
    def set_fm_deviation(self, deviation=100, chan=1):
        """Sets FM deviation in "peak deviation in Hz". Can be number or MIN or MAX"""
        return self.msg('SOURCE'+str(chan)+':FM:DEV '+str(deviation))
        
    def get_fm_deviation(self, chan=1):
        """Returns current FM deviation"""
        return self.msg('SOURCE'+str(chan)+':FM:DEV?')
    
    # FSK commands
    #####################
    # FSK state commands
    #####################
    def set_fsk_state(self, enable=True, chan=1):
        """Enables of disables frequency-shift keying modulation"""
        return self.msg('SOURCE'+str(chan)+':FSK:STATE '+str("ON" if enable else "OFF"))
    
    def get_fsk_state(self, chan=1):
        """Returns if frequency-shift keying modulation is enabled or not"""
        return self.msg('SOURCE'+str(chan)+':FSK:STATE?')
    
    # FSK source commands
    #####################
    def set_fsk_source(self, src="INT", chan=1):
        """Sets FSK source to INTernal or EXTernal"""
        if src.upper() in ['INT','EXT']:
            return self.msg('SOURCE'+str(chan)+':FSK:SOUR '+str(src))
        else:
            raise RangeException
    
    def get_fsk_state(self, chan=1):
        """Returns current FSK source"""
        return self.msg('SOURCE'+str(chan)+':FSK:SOUR?')
    
    # FSK frequency commands
    #####################
    def set_fsk_frequency(self, freq=100, chan=1):
        """Sets FSK function frequenc. Can be number or MIN or MAX"""
        return self.msg('SOURCE'+str(chan)+':FSK:FREQ '+str(freq))
        
    def get_fsk_frequency(self, chan=1):
        """Returns current internal FSK function frequency"""
        return self.msg('SOURCE'+str(chan)+':FSK:FREQ?')
    
    # FSK internal rate commands
    #####################
    def set_fsk_internal_rate(self, rate=100, chan=1):
        """Sets FSK rate for internal sources. Can be number or MIN or MAX"""
        return self.msg('SOURCE'+str(chan)+':FSK:INT:RATE '+str(rate))
        
    def get_fsk_internal_rate(self, chan=1):
        """Returns current FM depth"""
        return self.msg('SOURCE'+str(chan)+':FSK:INT:RATE?')
    
    # Frequency sweep commands
    #####################
    # FS state commands
    #####################
    def set_fs_state(self, enable=True, chan=1):
        """Enables of disables Frequency sweep"""
        return self.msg('SOURCE'+str(chan)+':SWE:STATE '+str("ON" if enable else "OFF"))
    
    def get_fs_state(self, chan=1):
        """Returns if Frequency sweep is enabled or not"""
        return self.msg('SOURCE'+str(chan)+':SWE:STATE?')
    
    # FS start commands
    #####################
    def set_fs_start(self, freq=1, chan=1):
        """Sets start frequency of FS. Can be number, 'MIN' or 'MAX'"""
        return self.msg('SOURCE'+str(chan)+':FREQ:STAR '+str(freq))
    
    def get_fs_start(self, chan=1):
        """Returns FS start frequency"""
        return self.msg('SOURCE'+str(chan)+':FREQ:STAR?')
    
    # FS stop commands
    #####################
    def set_fs_stop(self, freq=1, chan=1):
        """Sets stop frequency of FS. Can be number, 'MIN' or 'MAX'"""
        return self.msg('SOURCE'+str(chan)+':FREQ:STOP '+str(freq))
    
    def get_fs_stop(self, chan=1):
        """Returns FS stop frequency"""
        return self.msg('SOURCE'+str(chan)+':FREQ:STOP?')
    
    # FS spacing commands
    #####################
    def set_fs_spacing(self, rate=1, chan=1):
        """Sets FS sweep rate. Can be number (Hz), 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':SWE:RATE '+str(rate))
    
    def get_fs_spacing(self, chan=1):
        """Returns FS sweep rate"""
        return self.msg('SOURCE'+str(chan)+':SWE:RATE?')
    
    # FS source commands
    #####################
    def set_fs_source(self, src='IMM', chan=1):
        """Sets FS source to 'IMMediate' or 'EXTernal'"""
        if src.upper() in ['IMM','EXT']:
            return self.msg('SOURCE'+str(chan)+':SWE:SOUR '+str(src))
        else:
            raise RangeException
    
    def get_fs_source(self, chan=1):
        """Returns FS source"""
        return self.msg('SOURCE'+str(chan)+':SWE:SOUR?')
    
    # Frequency counter commands
    #####################
    # FC gate commands
    #####################
    def set_fc_gate(self, gate=0.1):
        """Sets frequency counter gate time"""
        return self.msg('COUN:GAT '+str(gate))
    
    def get_fc_gate(self):
        """Returns current frequency counter gate time"""
        return self.msg('COUN:GAT?')
    
    # FC state commands
    #####################
    def set_fc_state(self, enable=True):
        """Enables / disables frequency counter"""
        return self.msg('COUN:STAT '+str("ON" if enable else "OFF"))
    
    def get_fc_state(self):
        """Returns if frequency counter is enabled"""
        return self.msg('COUN:STAT?')
    
    # FC counts commands
    #####################
    def get_fc_value(self):
        """Returns counter frequency"""
        return self.msg('COUN:VAL?')

class AFG2005(AFG2000):
    def __init__(self,dev):
        super().__init__(dev)
        self.frequencyrange["Sine"]=(0.1,5*10**6)
        self.frequencyrange["Square"]=(0.1,5*10**6)
        
    def info(self):
        return("AFG2005")

class AFG2105(AFG2100):
    def __init__(self,dev):
        super().__init__(dev)
        self.frequencyrange["Sine"]=(0.1,5*10**6)
        self.frequencyrange["Square"]=(0.1,5*10**6)
        
    def info(self):
        return("AFG2105")

class AFG2012(AFG2000):
    def __init__(self,dev):
        super().__init__(dev)
        self.frequencyrange["Sine"]=(0.1,1*10**6)
        self.frequencyrange["Square"]=(0.1,12*10**6)
        
    def info(self):
        return("AFG2012")

class AFG2112(AFG2100):
    def __init__(self,dev):
        super().__init__(dev)
        self.frequencyrange["Sine"]=(0.1,12*10**6)
        self.frequencyrange["Square"]=(0.1,12*10**6)
        
    def info(self):
        return("AFG2112")

class AFG2025(AFG2000):
    def __init__(self,dev):
        super().__init__(dev)
        self.frequencyrange["Sine"]=(0.1,25*10**6)
        self.frequencyrange["Square"]=(0.1,25*10**6)
    
    def info(self):
        return("AFG2025")

class AFG2125(AFG2100):
    def __init__(self,dev):
        super().__init__(dev)
        self.frequencyrange["Sine"]=(0.1,25*10**6)
        self.frequencyrange["Square"]=(0.1,25*10**6)
    
    def info(self):
        return("AFG2125")

