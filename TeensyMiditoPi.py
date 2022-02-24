#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial
import mido, time


if __name__ == '__main__':
    
    #print('Running. Press CTRL-C to exit.')
    #with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
    #if arduino.isOpen():
            #print("{} connected!".format(arduino.port))
            
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(0.1) #wait for serial to open
        ser.flush()
        # Infinite loop
        while (1):
            # If there is data available
                if(ser.in_waiting > 0):
                    line = ser.readline().decode('utf-8').rstrip()
                    # Print the data received from the Arduino
                    print(line)