#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial,time
import mido


if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                while True:
                    
                    time.sleep(0.1) #wait for arduino to answer
                    while arduino.inWaiting()==0: pass
                    if  arduino.inWaiting()>0: 
                        answer=arduino.read(4)
                        print(answer[0],",",answer[1],",",answer[2],",",answer[3])
                        arduino.flushInput() #remove data after reading

                    # cmd=input("Enter command : ")
                    # arduino.write(cmd.encode())
                    # #time.sleep(0.1) #wait for arduino to answer
                    # while arduino.inWaiting()==0: pass
                    # if  arduino.inWaiting()>0: 
                    #     answer=arduino.readline()
                    #     print(answer)
                    #     arduino.flushInput() #remove data after reading
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")