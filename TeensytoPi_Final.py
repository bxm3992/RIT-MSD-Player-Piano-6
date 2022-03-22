#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial
import sys
import mido, time, threading
import serial.tools.list_ports as port_list
import os
import threading

if __name__ == '__main__':
    
    ports = list(port_list.comports())
    for p in ports: print (p)
    
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        data_length=4 #one byte is 8 bits, use arduino to determine how many bytes being sent
        while True:
            if ser.in_waiting > 0:
                command_note_velocity_time = ser.read_until(size=data_length)
                ser.flush()
    except KeyboardInterrupt:
            print("Closing program.\n")

''' 
This is the function that creates the midi file
Originated: 22363
    Original Author: Austin Nguyen
    Author: Blaise Meilunas 
'''    
def createMIDI():
    flag = False
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    #https://www.programiz.com/python-programming/datetime/current-datetime
    #when creating use date and time
    #need to add means to change the name
    userInput = input("Press q to stop recording: ")
    while(not(flag)):
        if userInput == "q":
            flag = True
            enterName = input("Enter filename for MIDI file: ")
            mid.save(enterName + ".mid")
        bitsToRead = ser.inWaiting()
        arrayBits = ser.read(bitsToRead)
        # Not sure if bytearray was used to send array over serial
        # arrayData = bytearray(bitsToRead)
        # for elem in arrayData:
            # Skip the first element since it's the delta time
            # continue
            # track.append(Message('note_on', note=int(elem), 0, arrayData[0])) # Specify velocity
        track.append(Message('note_on', note=64, velocity=127, time=32))
        
