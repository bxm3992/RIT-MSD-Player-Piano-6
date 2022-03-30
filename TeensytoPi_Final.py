#!/usr/bin/env python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial
import sys
import mido, time, threading
import numpy as np
from datetime import datetime
import serial.tools.list_ports as port_list
import os

flag = False
keynote_array=[]
midiLL= LinkedList()

''' 
PSUEDOCODE:
Main function 
create the note array for the midi data
creates two threads
    Thread one is reading the serial input of the pi and storing the info in the array using a function, or sending data to struct if flag = 1
    Thread two is waiting for the flag to be set to start creating a MIDI file using the serial info
 '''

def getSerialData():
'''
This is a threading function to get the serial data from the Pi.
'''
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        data_length=4 #one byte is 8 bits, use arduino to determine how many bytes being sent
        while True:
            if ser.in_waiting > 0:
                command_note_velocity_time = ser.read_until(size=data_length)
                for x in range(1,4):
                    keynote_array[command_note_velocity_time[1],x] = command_note_velocity_time[x]
                if(flag):
                    midiLL.AtEnd(command_note_velocity_time)
                ser.flush()
                
    except KeyboardInterrupt:
            print("Closing program.\n")

''' 
This is the function that creates the midi file based on a flag.
Originated: 22363
    Original Author: Austin Nguyen
    Author: Blaise Meilunas 
'''    
def createMIDI():
    while(1):
        if(flag):
            mid = MidiFile()
            track = MidiTrack()
            mid.tracks.append(track)
            #https://www.programiz.com/python-programming/datetime/current-datetime
            #when creating use date and time
            #need to add means to change the name
            while(flag):
            #add to the midi file until flag is toggled off then save and close
                #check for data
                if(midiLL.head.data != None):
                    temp_data=midiLL.head.data
                    temp_command=''
                    #get note command else throw error cuz impossible
                    if (temp_data[0] == 144):
                        temp_command='note_on'
                    elif(temp_data[0] == 128):
                        temp_command='note_off'
                    else:
                        raise ValueError
                    #add data to midi and remove data from LList
                    track.append((Message(temp_command, note=temp_data[1],velocity=temp_data[2],time=temp_data[3])))
                    RemoveNode(midiLL,temp_data)
            curr_time = datetime.now()
            temp_name = time.strftime("%d/%m/%Y %H:%M:%S")
            mid.save(temp_name+'.mid')
        

  
    
if __name__ == '__main__':
    
    serial_thread=Thread(target=getSerialData)
    serial_thread.start()
    
    #internal array is size 4, contains: command|note|velocity|time
    np.full((88,4),0) #keynote_array=np.array([0,0,0,0],[0,0,0,0])
    
    midifile_thread=Thread(target=createMIDI)
    midifile_thread.start()
    


class Node:
   def __init__(self, data=None):
      self.data = data
      self.next = None
class LinkedList:
   def __init__(self):
      self.head = None

#functions to add at end and beginning
   def Atbegining(self, data_in):
      NewNode = Node(data_in)
      NewNode.next = self.head
      self.head = NewNode
    # Function to add newnode
   def AtEnd(self, newdata):
      NewNode = Node(newdata)
      if self.headval is None:
         self.headval = NewNode
         return
      laste = self.headval
      while(laste.nextval):
         laste = laste.nextval
      laste.nextval=NewNode
      
# Function to remove node
   def RemoveNode(self, Removekey):
      HeadVal = self.head
         
      if (HeadVal is not None):
         if (HeadVal.data == Removekey):
            self.head = HeadVal.next
            HeadVal = None
            return
      while (HeadVal is not None):
         if HeadVal.data == Removekey:
            break
         prev = HeadVal
         HeadVal = HeadVal.next

      if (HeadVal == None):
         return

      prev.next = HeadVal.next
         HeadVal = None
         
#function to print
   def LListprint(self):
      printval = self.head
      while (printval):
         print(printval.data),
         printval = printval.next    
