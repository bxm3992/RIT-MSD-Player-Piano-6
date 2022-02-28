#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

#print('Running. Press CTRL-C to exit.')
    #with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
    #if arduino.isOpen():
            #print("{} connected!".format(arduino.port))

import serial
import sys
import mido, time
import serial.tools.list_ports as port_list

if __name__ == '__main__':
    
    ports = list(port_list.comports())
    for p in ports: print (p)
        
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    data_length=4
    while True:
        if ser.in_waiting > 0:
            data = ser.read(size=data_length)
            for i in range(data_length):
                print(data[i]) 
            #ser.flush()