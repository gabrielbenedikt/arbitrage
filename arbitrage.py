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
        'func' can be SIN, SQUare, RAMP, NOISE, USER
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        return self.msg('SOURCE'+str(chan)+':APPLY:'+str(func)+' '+str(freq)+','+str(amp)+','+str(off))
    
    def apply_sine(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output sine function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        self.apply_func(chan=chan, func='SIN', freq=freq, amp=amp, off=off)
    
    def apply_square(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to outut square function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        self.apply_func(chan=chan, func='SQUARE', freq=freq, amp=amp, off=off)
        
    def apply_ramp(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output ramp function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        self.apply_func(chan=chan, func='RAMP', freq=freq, amp=amp, off=off)
    
    def apply_noise(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output noise at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        self.apply_func(chan=chan, func='NOISE', freq=freq, amp=amp, off=off)
        
    def apply_user(self,freq=100, amp=0.1, off=0, chan=1):
        """Instructs device to output stored user function at channel 'chan' with frequency 'freq', amplitude 'amp' and offset 'off'
        'freq' in Hz
        'amp' in V
        'offs' in V"""
        self.apply_func(chan=chan, func='USER', freq=freq, amp=amp, off=off)
        
    
    
    
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

