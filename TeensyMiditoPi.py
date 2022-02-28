#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial
import sys
import mido, time


if __name__ == '__main__':
    
    #print('Running. Press CTRL-C to exit.')
    #with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
    #if arduino.isOpen():
            #print("{} connected!".format(arduino.port))
    try:
        ser = serial.Serial("/dev/ttyACM0", 9600,timeout=0, parity=serial.PARITY_NONE, 
                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    except:
        sys.exit("Error connecting device")        
    #ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)