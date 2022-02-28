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
        
    time.sleep(2)
    #try:
    ser = serial.Serial(port="/dev/ttyACM0", baudrate=9600,timeout=0, parity=serial.PARITY_NONE, 
                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    #except:
        #sys.exit("Error connecting device")        
    time.sleep(2)
    ser.reset_input_buffer()
    time.sleep(.01)
    print("Starting program.")
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)