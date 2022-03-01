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
    
    print(mido.get_output_names())
    
    try:
        #inport = mido.open_input('/dev/ttyACM0')
        inport = mido.open_input('Midi Through:Midi Through Port-0 14:0')
        while True:
            for temp_msg in inport.iter_pending():
                print(temp_msg)
    except KeyboardInterrupt:
            print("Interrupted. Closing ports....")
            inport.close()
            print("Closed ports. Closing program.\n")
    
    
        
    # ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    # ser.reset_input_buffer()
    # data_length=4 #one byte is 8 bits, use arduino to determine how many bytes being sent
    # while True:
    #     if ser.in_waiting > 0:
    #         data = ser.read_until(size=data_length)
    #         temp_data = [data[0],data[1],data[2],data[3]]
    #         #print(data)
    #         for i in range(data_length):
    #             print(str(temp_data[i])+",") 
    #         print("\n")
    #         ser.flush()