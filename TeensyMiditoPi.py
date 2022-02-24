#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial
import mido, time


if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/ttyACM0", 31250, timeout=1) as arduino:
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            arduino.flush()
            # Infinite loop
            while (1):
            # If there is data available
                if(arduino.in_waiting > 0):
                    line = arduino.readline().decode('utf-8').rstrip()
                    # Print the data received from the Arduino
                    print(line)