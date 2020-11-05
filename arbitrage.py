#!/usr/bin/env python3

import serial
import io
import threading

class RangeError:
    """Parameter out of range"""
    pass

class DeviceError:
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
        elif "AFG-2105" in self.info[0]:
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
            raise DeviceError
            
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
            return lines
        else:
            return ""

class AFGbase():
    def __init__(self,dev):
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
        return self.msg('SOURCE'+str(chan)+'APPLY?')
    
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
        return self.msg('SOURCE'+str(chan)+':SQUARE:DCYCLE '+str(offset))
    
    def get_square_dutycycle(self, chan=1):
        """Returns currently set square function duty cycle"""
        return self.msg('SOURCE'+str(chan)+':SQUARE:DCYCLE?')
    
    # RAMP symmetry commands
    #####################
    def set_ramp_symmetry(self, sym=50, chan=1):
        """Instructs device to change symmetry of ramp function on channel 'chan'
        sym can be a number (in percent) or 'MIN' or 'MAX' """
        return self.msg('SOURCE'+str(chan)+':RAMP:SYMM '+str(offset))
    
    def get_square_duty(self, chan=1):
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
            raise RangeError
    
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
            raise RangeError
    
    def set_volt_units_vpp(self, chan=1):
        """Set voltage units to vpp"""
        return self.set_output_volt_units(unit="VPP", chan=chan)
    
    def set_volt_units_vrms(self, chan=1):
        """Set voltage units to vrms"""
        return self.set_output_volt_units(unit="VRMS", chan=chan)
    
    def set_volt_units_dbm(self, chan=1):
        """Set voltage units to vdbm"""
        return self.set_output_volt_units(unit="DBM", chan=chan)
    
    def get_volt_units(self, chan=1):
        """Returns current output voltage units of channel chan"""
        return self.msg('SOURCE'+str(chan)+':VOLT:UNIT?')
    
    
    
class AFG2005(AFGbase):
    def info(self):
        return("AFG2005")

class AFG2105(AFGbase):
    def info(self):
        return("AFG2105")

class AFG2012(AFGbase):
    def info(self):
        return("AFG2012")

class AFG2112(AFGbase):
    def info(self):
        return("AFG2112")

class AFG2025(AFGbase):
    def info(self):
        return("AFG2025")

class AFG2125(AFGbase):
    def info(self):
        return("AFG2125")

