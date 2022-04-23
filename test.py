"""
MIDI Play
Originated: 22363
    Author: Blaise Meilunas
------------------
Play Doctor Who midifile - note: you need the relative or absolute filepath name to the midifile
python3 test.py play ./midifiles/DoctorWho.mid

Play Pirates at a specific tempo @ 160
python3 test.py play ./midifiles/DoctorWho.mid 160

Print the tempo of Sweden
python3 test.py tempo ./midifiles/DoctorWho.mid

Reset all keys
python3 test.py reset
-------------------

Notes for usage:
To stop the play mid-playback: Ctrl-C
******************************
IMPORTANT: AFTER STOPPING MID-PLAY -> RUN RESET -> python3 play_midi.py reset 
    Solenoids emit a mechanical whine if still attempting to actuate - reset the solenoids to prevent damage 
"""
import mido
import sys
import os
import json
import time
import threading
from math import floor


import board
import busio
import digitalio
import adafruit_tlc5947
import RPi.GPIO as GPIO

#global flag for testing thread & keystroke number
nflag= False
bflag = False
dflag = False
dflag2 = False
flag=True
correct_keys=[8,9,10,11,4,5,6,7,0,1,2,3,15,14,13,13,19,19,17,16,23,22,22,20]
keyNum = 0

# Key Offset refers to the note difference between MIDI Start(C0) and Piano Start(A0)
KEY_OFFSET = 9

# The global PWM minimum for default usage if piano is not calibrated - cannot exceed 4096
PWM_MIN = 2048

# Calibration file name and location - CSV
calFile = 'key_calibrations.txt'


def reset_key():
    SCK = board.SCK
    MOSI = board.MOSI
    LATCH = digitalio.DigitalInOut(board.D5)

    # Initialize SPI bus.
    spi = busio.SPI(clock=SCK, MOSI=MOSI)

    # Initialize TLC5947
    tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,
                                       num_drivers=4)
    for x in range(88):
        tlc5947[x] = 0
    tlc5947.write()

    print("RESET")


def gen_calibration_file():
    """
    Generates a calibration file with assumed PWM minimums give by the global
    :return:
    """
    file = open(calFile, 'w')
    for num in range(88):
        file.write(str(num)+","+str(PWM_MIN)+"\n")
    file.close()


def read_calibration_file():
    """
    Returns a dict of minimum note values (PWM) and arranges them based on their note location
    :return: noteMinList - list of notes and their minimum PWM activation strengths
    """
    noteMinDict = dict()
    file = open(calFile, 'r')
    for line in file.readlines():
        stripLine = line.rstrip()
        if line != "":
            noteMinDict[int(stripLine.split(",")[0])] = int(stripLine.split(",")[1])
    file.close()
    return noteMinDict


def getTempo(song_path):
    """
    Method to ge the original tempo of a song from and return it
    :param song_path: Song to get the original set tempo from
    :return: server searches STDOUT pipe for tempo response - CAREFUL WITH PRINT STATEMENTS
    """
    if not os.path.exists(song_path):
        print("Song provided does not exist")
        sys.exit("Song provided does not exist")  # Redundant Check - song wouldn't be selectable if it doesn't exist
    mid = mido.MidiFile(song_path)

    tempo = 0

    for msg in mid:
        if msg.is_meta and msg.type == 'set_tempo':
            tempo = int(msg.tempo)
            break
    print(int(mido.tempo2bpm(tempo)))


def actuateSustainPedal(dir):
    """
    Thread trigger function for the sustain pedal - clockwise is UP, counter-clockwise is DOWN
    :param dir: direction to actuate the pedal - INT - 1 for UP, 0 for DOWN
    :return: None
    """

    PWMPIN = 12
    GPIO.setwarnings(False)			            #disable warnings
    # GPIO.setmode(GPIO.BOARD)		            #set pin numbering system
    GPIO.setup(PWMPIN,GPIO.OUT)
    pi_pwm = GPIO.PWM(PWMPIN,10000)		        #create PWM instance with frequency
    pi_pwm.start(0)

    HBRIDGE_A = digitalio.DigitalInOut(board.D6) # may need to be a different IO port
    HBRIDGE_B = digitalio.DigitalInOut(board.D7) # may need to be a different IO port
    HBRIDGE_A.direction = digitalio.Direction.OUTPUT
    HBRIDGE_B.direction = digitalio.Direction.OUTPUT


    if dir == 1:
        HBRIDGE_A.value = True
        HBRIDGE_B.value = False
        time.sleep(1)  # Time for sustain pedal to actuate - UP
        HBRIDGE_A.value = False
        HBRIDGE_B.value = False
    else:
        HBRIDGE_A.value = False
        HBRIDGE_B.value = True
        time.sleep(2)  # Time for sustain pedal to actuate - DOWN
        HBRIDGE_A.value = False
        HBRIDGE_B.value = False

        print("PEDAL ACTUATED")

def playMidi(song_path, bpm=0):
    """
    The main MIDI playback function
    :param song_path: song in which to extract metadata from
    :param bpm: OVERWRITE tempo, 0 otherwise to set to tempo found in metadata
    :return:
    """
    global keyNum

    if not os.path.exists(song_path):
        sys.exit("Song Provided does not exist")  # Redundant Check - song wouldn't be selectable if it doesn't exist
    mid = mido.MidiFile(song_path)

    notesDict = {'songName': 'testname', 'bpm': 999, 'notes': []}
    length = 0
    notesArray = [[]]
    tickLength = 0
    VOLUME = 100
    MIN = 800

   
    SCK = board.SCK
    MOSI = board.MOSI
    LATCH = digitalio.DigitalInOut(board.D5)
    
    HBRIDGE_A = digitalio.DigitalInOut(board.D6) # may need to be a different IO port
    HBRIDGE_B = digitalio.DigitalInOut(board.D7) # may need to be a different IO port


    # Initialize SPI bus.
    spi = busio.SPI(clock=SCK, MOSI=MOSI)

    # Initialize TLC5947
    tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,
                                       num_drivers=4)
    for x in range(88):
        tlc5947[x] = 0
    tlc5947.write()

    if bpm != 0:  # If there is a bpm provided, convert to mido tempo
       tempo = mido.bpm2tempo(bpm)

    for msg in mid:
        if msg.is_meta and msg.type == 'set_tempo':
            if bpm == 0:  # If there is an overwriting tempo given to the function, ignore metadata
                tempo = int(msg.tempo)
            length = int(floor(mido.second2tick(mid.length,
                                                mid.ticks_per_beat,
                                                tempo)))
            tickLength = mido.tick2second(1, mid.ticks_per_beat, tempo)
            #break
        # print(msg)

    #print('Tick length: ' + str(tickLength))
    currentTick = 0
    notesArray[0] = [0 for x in range(90)]
    lineIncrement = 0
    
    # Create notesArray (list of lists) out of midi messages
    # ------------------------------------------------------
    # Basic visual depiction of notesArray:
    #                                        time --->
    # lineIncrement:(index)  |       0       1      2       3    ...
    #    pedalState:(bool)   |    [ [0       0      1       1
    #    delayAfter:(sec)    |       0       0.1    0.3     0.4
    #            /G:(vel)    |       000     000    000     000
    #           / F:  |      |       000     000    000     000
    #          /  E:  |      |       000     127    127     127
    #     notes   D:  |      |       000     000    000     000 
    #          \  C:  v      |       000     000    000     127  
    #           \ B:         |       000     127    127     000
    #            \A:         |       000]    000]   000]    000]  ... ]
    print("Parsing MIDI file....")
    for msg in mid:
        # places velocity values in notesArray based on when notes occur simultaneously, and keeps track of delay between events. 
        if msg.type is 'note_on' or msg.type is 'note_off':
            delayAfter = int(floor(mido.second2tick(msg.time, mid.ticks_per_beat, tempo)))
            if delayAfter == 0: #simultaneous notes
                if msg.note < 89:
                    notesArray[lineIncrement][msg.note - 12] = msg.velocity  # should this 12 be set to KEY_OFFSET?
            else:
                notesArray[lineIncrement][88] = delayAfter
                notesArray.append([0 for x in range(90)])
                for y in range(88):
                    notesArray[lineIncrement+1][y] = notesArray[lineIncrement][y]
                #notesArray.append(notesArray[lineIncrement])
                lineIncrement += 1
                # notesArray[lineIncrement][88] = 0
                if msg.note < 89:
                    notesArray[lineIncrement][msg.note - 12] = msg.velocity
                    
                # notesArray.append([0 for x in range(90)])
                # for y in range(88):
                #     notesArray[lineIncrement+1][y] = notesArray[lineIncrement][y]
                # lineIncrement += 1
                
        # Saves state of pedal when sent a 'control_change' message for sustain pedal (CC #64)
        elif msg.type is 'control_change' and msg.control == 64:
            delayAfter = int(floor(mido.second2tick(msg.time, mid.ticks_per_beat, tempo)))
            if msg.value > 63:
                # in MIDI protocol 0-63=off, 64-127=on
                pedalState = 1
            else:
                pedalState = 0
        
            notesArray[lineIncrement][-1] = pedalState  # write pedalState as final value in each noteArray column.

    # Velocity to PWM
    # 1-126 -> MIN PWM (2048) - 4096 | Assuming linear scale
    #           notePWM    = (((noteVel - velMin) * (PWMMax - PWMMin)) / (velMax - velMin)) + PWMMin
    # In usage: tlc5947[x] = (((line[x] - velMin) * (PWMMax - PWMMin)) / (velMax - velMin)) + PWMMin
    velMin = 1
    velMax = 127
    PWMMax = 4095
    # PWMMin is global and subject to vary depending on the note - often replaced by # in calibration file

    # Read calibration file else generate a calibration file and try again
    notesMinDict = None
    try:
        notesMinDict = read_calibration_file()
    except:
        gen_calibration_file()
        notesMinDict = read_calibration_file()
    if notesMinDict is None:
        sys.exit("Failed to read/generate calibration file. Please check file generation and reading functions.")

    print('Playing....')
    startTime = time.time()
    tlc5947.write()
    # COUNT-IN WAIT IS PERFORMED HERE - DONE TEMPORARILY VIA FILE POLLING
    # TODO: Replace by Django Webframework

    time.sleep(3)
    #test outline:
    #   set first bit of array to 4090
    #   send array (plays key)
    #   poll for input (wait 10 seconds)
    #   loop else  
    #       go to next bit
    #   if input is exit, break out overall loop

    temp_keyNum = int(input('input the starting keynum value (between 0 and 87) \n'))
    if temp_keyNum < 88 and temp_keyNum >= 0:
        keyNum = temp_keyNum
    else:
        keyNum = 0
    
    

    #set all keys to 0
    for x in range(88):  # Go through all 88 keys   
        tlc5947[x] = 0
        continue

    #call to the function that does the testing for threading
    print('starting threads...')
    master_thread=threading.Thread(target=master_program)
    
    input_thread=threading.Thread(target=get_input)
    testing_thread=threading.Thread(target=testing)
    
    new_testing_thread=threading.Thread(target=new_testing)
    blaise_testing_thread=threading.Thread(target=blaise_testing)
    
    master_thread.start()
    testing_thread.start()
    input_thread.start()
    new_testing_thread.start()
    blaise_testing_thread.start()
    
    while((flag)):
        continue
    print("One moment.")
    time.sleep(5)
    print("Finished playing....")     
    reset_key()

################----------------------------##################
#---------------############################------------------#
################----------------------------##################
def testing():
    while(1):
        global dflag
        global dflag2
        global keyNum
        while(dflag):
            
            #this is the correct key array because the mapping is wrong for some reason, last 3 zeros are 86,46,51 indexes
            correct_keys=[8,9,10,11,4,5,6,7,0,1,2,3,15,14,13,13,19,19,17,16,23,22,22,20]

            SCK = board.SCK
            MOSI = board.MOSI
            LATCH = digitalio.DigitalInOut(board.D5)

             # Initialize SPI bus.
            spi = busio.SPI(clock=SCK, MOSI=MOSI)
            
            tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,
                                               num_drivers=4)
            for x in range(88):
                tlc5947[x] = 0
            tlc5947.write()
            while(dflag2 != True):
                # send array to PWM IC, set current key to 'actve'
                temp_PWMvalue = 4090
                true_key=correct_keys[keyNum]
                tlc5947[true_key]= temp_PWMvalue
                tlc5947.write()
                print("value written. key is currently: ",keyNum) #uncomment write when ready
                print("the solenoid is activated.")
                #unwrite it 
                time.sleep(2)
                tlc5947[keyNum]= 0
                tlc5947.write()
                print("the solenoid is now off.")
                #removed sustain pedal functionality
                time.sleep(5)
                if dflag2 ==True:
                    print('The loop will now close.')
                    dflag=False
                    break
            if not dflag:
                break

#wait for constant input
#if input is c, close program
#if input anything else, increment the key
def get_input():
    while(1):
        key_limit = 24
        global dflag2
        global keyNum
        while(dflag):   
            keystroke = input('input i to increment, c to close testing program \n')
            #freezes thread until keypress
            print('you pressed:', keystroke)
            if keystroke == 'c':
                dflag2=True
                print("Preparing to close.")
                time.sleep(5)
                break
            elif keystroke == 'i':
                #check if over 88 keys (now keylimit)
                if (keyNum >= key_limit):
                    keyNum = 0
                elif (keyNum < key_limit):    
                    keyNum= keyNum+1
            else:
                continue

def new_testing():
    while(1):
        global nflag
        #this is the correct key array because the mapping is wrong for some reason, last 3 zeros are 86,46,51 indexes
        global correct_keys
        SCK = board.SCK
        MOSI = board.MOSI
        LATCH = digitalio.DigitalInOut(board.D5)

        # Initialize SPI bus.
        spi = busio.SPI(clock=SCK, MOSI=MOSI)
        tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,num_drivers=4)
        if nflag:
            for x in range(88):
                tlc5947[x] = 0
            tlc5947.write()
        while(nflag):    
            play_key=input('input key to play from 0 to 23 \n')
            #freezes thread until keypress
            print('Playing key ', play_key)
            # send array to PWM IC, set current key to 'actve'
            temp_PWMvalue = 4090
            int(play_key) #convert to num
            true_key=correct_keys[play_key]
            tlc5947[true_key]= temp_PWMvalue
            tlc5947.write()
            #unwrite it 
            time.sleep(1)
            tlc5947[true_key]= 0
            tlc5947.write()
            #the note was written, time to write another
        
def blaise_testing():
    while(1):
        global bflag
        #this is the correct key array because the mapping is wrong for some reason, last 3 zeros are 86,46,51 indexes
        global correct_keys
        SCK = board.SCK
        MOSI = board.MOSI
        LATCH = digitalio.DigitalInOut(board.D5)

        # Initialize SPI bus.
        spi = busio.SPI(clock=SCK, MOSI=MOSI)
        tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,num_drivers=4)
        if bflag:
            for x in range(88):
                tlc5947[x] = 0
            tlc5947.write()
        if bflag:
            #CE then ADFD
            temp_play_single_key(21,.25)    
            temp_play_single_key(19,.45)       
            
            temp_turnon_single_key(0)       
            temp_turnon_single_key(3)
            temp_turnon_single_key(5)
            temp_turnon_single_key(20)
            time.sleep(1.5)
            temp_turnoff_single_key(0)
            temp_turnoff_single_key(3)
            temp_turnoff_single_key(5)
            temp_turnoff_single_key(20)
            #end ADFD
            
            #DE
            temp_play_single_key(20,.25)
            temp_play_single_key(21,.45)
            
            #ACE DCCAC
            temp_turnon_single_key(0)
            temp_turnon_single_key(2)
            temp_turnon_single_key(4)
            temp_play_single_key(20,.45)    #D
            
            temp_play_single_key(19,.25)    #C
            temp_play_single_key(19,.45)    #C
            temp_play_single_key(17,.25)    #A
            temp_play_single_key(19,.45)    #C
            temp_turnoff_single_key(0)
            temp_turnoff_single_key(2)
            temp_turnoff_single_key(4)
            temp_play_single_key(17,.45)    #A
            #end ACE
            
            #C then CEG GEDC GEDD with BDG
            temp_play_single_key(19,.25)
            
            temp_turnon_single_key(2)
            temp_turnon_single_key(4)
            temp_turnon_single_key(6)
            temp_play_single_key(23,.25)
            temp_play_single_key(21,.25)
            temp_play_single_key(20,.25)
            temp_play_single_key(19,.25)    #end of first GEDC
            temp_play_single_key(23,.25)
            temp_play_single_key(21,.25)
            temp_turnoff_single_key(2)
            temp_turnoff_single_key(4)
            temp_turnoff_single_key(6)
            
            temp_play_single_key(20,.25)    #D
            temp_turnon_single_key(1)
            temp_turnon_single_key(3)
            temp_turnon_single_key(6)
            temp_play_single_key(20,.35)    #D2
            temp_play_single_key(20,.55)    #D3
            temp_play_single_key(21,.25)    #E
            temp_turnoff_single_key(1)
            temp_turnoff_single_key(3)
            temp_turnoff_single_key(6)  
            #end of CEG and BDG
            
            #C then ADFD
            temp_play_single_key(19,.25)
            temp_turnon_single_key(0)
            temp_turnon_single_key(3)
            temp_turnon_single_key(5)
            temp_turnon_single_key(20)
            time.sleep(1)
            temp_turnoff_single_key(0)
            temp_turnoff_single_key(3)
            temp_turnoff_single_key(5)
            temp_turnoff_single_key(20)
            
            temp_play_single_key(20,.25)
            temp_play_single_key(21,.25)
            temp_play_single_key(20,.25)
            
            #DE
            temp_play_single_key(20,.25)
            temp_play_single_key(21,.45)
            
            #ACE DCCAC
            temp_turnon_single_key(0)
            temp_turnon_single_key(2)
            temp_turnon_single_key(4)
            temp_play_single_key(20,.45)
            
            temp_play_single_key(19,.25)
            temp_play_single_key(19,.45)
            temp_play_single_key(17,.25)
            temp_play_single_key(19,.45)
            temp_turnoff_single_key(0)
            temp_turnoff_single_key(2)
            temp_turnoff_single_key(4)
            temp_play_single_key(17,.45)
            #end ACE
            
            temp_play_single_key(19,.25)
            
            temp_turnon_single_key(2)
            temp_turnon_single_key(4)
            temp_turnon_single_key(6)
            temp_play_single_key(23,.25)
            temp_play_single_key(21,.25)
            temp_play_single_key(20,.25)
            temp_play_single_key(19,.25)
            temp_play_single_key(23,.25)
            temp_play_single_key(21,.25)
            temp_turnoff_single_key(2)
            temp_turnoff_single_key(4)
            temp_turnoff_single_key(6)
            
            temp_play_single_key(20,.25)
            temp_turnon_single_key(1)
            temp_turnon_single_key(3)
            temp_turnon_single_key(6)
            temp_play_single_key(20,.35)
            temp_turnon_single_key(20)
            time.sleep(.7)
            temp_turnoff_single_key(1)
            temp_turnoff_single_key(3)
            temp_turnoff_single_key(6)
            time.sleep(.4)
            temp_turnoff_single_key(20)
            
            #begin ADFD
            temp_turnon_single_key(0)
            temp_turnon_single_key(3)
            temp_turnon_single_key(5)
            temp_play_single_key(20,.35)
            temp_play_single_key(20,.35)
            temp_play_single_key(19,.25)
            temp_play_single_key(20,.25)
            temp_play_single_key(21,.25)
            temp_turnoff_single_key(0)
            temp_turnoff_single_key(3)
            temp_turnoff_single_key(5)
            temp_play_single_key(20,.25)
            temp_play_single_key(17,.25)
            #end of ADFD
            
            temp_play_single_key(19,.35)
            #new ACE
            temp_turnon_single_key(0)
            temp_turnon_single_key(2)
            temp_turnon_single_key(4)
            temp_play_single_key(20,.15)
            time.sleep(.15)
            temp_play_single_key(20,.15)
            time.sleep(.15)
            temp_play_single_key(20,.15)
            time.sleep(.15)
            temp_play_single_key(20,.15)
            temp_play_single_key(19,.15)
            temp_play_single_key(20,.15)
            temp_play_single_key(21,.15)
            temp_turnoff_single_key(0)
            temp_turnoff_single_key(2)
            temp_turnoff_single_key(4)
            temp_play_single_key(20,.15)
            temp_play_single_key(17,.25)
            #end of ACE
            
            #C then CEG GEDC GEDD with BDG
            temp_play_single_key(19,.25)
            
            temp_turnon_single_key(2)
            temp_turnon_single_key(4)
            temp_turnon_single_key(6)
            temp_play_single_key(23,.25)
            temp_play_single_key(21,.25)
            temp_play_single_key(20,.25)
            temp_play_single_key(19,.25)    #end of first GEDC
            temp_play_single_key(23,.25)
            temp_play_single_key(21,.25)
            temp_turnoff_single_key(2)
            temp_turnoff_single_key(4)
            temp_turnoff_single_key(6)
            temp_play_single_key(20,.15)
            temp_play_single_key(19,.15)
            
            #CE then ADFD
            temp_play_single_key(21,.25)    
            temp_play_single_key(19,.45)       
            
            temp_turnon_single_key(1)       
            temp_turnon_single_key(3)
            temp_turnon_single_key(6)
            temp_turnon_single_key(20)
            time.sleep(1.5)
            temp_turnon_single_key(1)       
            temp_turnon_single_key(3)
            temp_turnon_single_key(6)
            temp_turnoff_single_key(20)
            
        bflag=False


def temp_play_single_key(keynum_temp,timeon):
    global correct_keys
    SCK = board.SCK
    MOSI = board.MOSI
    LATCH = digitalio.DigitalInOut(board.D5)

	# Initialize SPI bus.
    spi = busio.SPI(clock=SCK, MOSI=MOSI)
    tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,num_drivers=4)
    temp_PWMvalue = 4090
    true_key=correct_keys[keynum_temp]
    tlc5947[true_key]= temp_PWMvalue
    tlc5947.write()
	#unwrite it 
    time.sleep(timeon)
    tlc5947[true_key]= 0
    tlc5947.write()
    #key has been written and unwritten
    
def temp_turnon_single_key(keynum_temp):
    global correct_keys
    SCK = board.SCK
    MOSI = board.MOSI
    LATCH = digitalio.DigitalInOut(board.D5)

	# Initialize SPI bus.
    spi = busio.SPI(clock=SCK, MOSI=MOSI)
    tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,num_drivers=4)
    temp_PWMvalue = 4090
    true_key=correct_keys[keynum_temp]
    tlc5947[true_key]= temp_PWMvalue
    tlc5947.write()
    #key has been written

def temp_turnoff_single_key(keynum_temp):
    global correct_keys
    SCK = board.SCK
    MOSI = board.MOSI
    LATCH = digitalio.DigitalInOut(board.D5)

	# Initialize SPI bus.
    spi = busio.SPI(clock=SCK, MOSI=MOSI)
    tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, auto_write=False,num_drivers=4)
    true_key=correct_keys[keynum_temp]
    tlc5947[true_key]= 0
    tlc5947.write()
    #key has been unwritten
    
def master_program():
    global flag
    global nflag
    global bflag
    global dflag
    while(flag):
        mode_input=input('Type h for help. Input testing command: \n')
        if mode_input == 'h':
            print('Commands are: \nh: display commands\nc: close program\nd: default program\nn: new program\nb: blaise program\na: advanced list\n')
        elif mode_input == 'c':
            flag=False
            print('Closing program...')
            time.sleep(5)
            break
        elif mode_input == 'a':
            print('default program: original program that will let you choose starting key and will repeat key until you increment or close program \nnew program: when a number is entered from 0-23 the corresponding key will immediately play \nblaise program: a nice surprise will play :^)\n')
        elif mode_input == 'd':
            print('Starting default program...')
            dflag=True
            while(dflag):
                if not dflag:
                    print('returning to master...')
            time.sleep(7)
        elif mode_input == 'n':
            print('Starting new program...')
            nflag=True
            while(nflag):
                if not nflag:
                    print('returning to master...')
            time.sleep(7)
        elif mode_input == 'b':
            print('Starting blaise program...')
            bflag=True
            while(bflag):
                if not bflag:
                    print('returning to master...')
            time.sleep(7)
        else:
            print('Invalid command. Try typing h for help!')
            
           
       


def main():
    """
    Arguments expected: play, reset, tempo
    Respectively calls their function
    :return:
    """
    cmd=None
    numArg = len(sys.argv)
    if numArg >= 2:
        cmd = sys.argv[1]
        if cmd == 'reset':
            reset_key()
        elif cmd == 'sustain':
            print("Actuate")
            actuateSustainPedal(1)
            time.sleep(3)
            print("De-actuate")
            actuateSustainPedal(0)
        elif cmd == 'tempo' and numArg >= 3:
            songname = sys.argv[2]
            getTempo(songname)
        elif cmd == 'play' and numArg >= 3:
            songname = sys.argv[2]
            tempo = 0
            if numArg >= 4:
                tempo = int(sys.argv[3])
            reset_key()  # Redundant key reset
            playMidi(songname, tempo)
    else:
        sys.exit("Please insert command as argument. reset, play songname opt:tempo, tempo")


if __name__ == "__main__":
    main()



#reset_key()
#playMidi('bumble_bee.mid')
#playMidi('for_elise_by_beethoven.mid')
# playMidi('debussy_clair_de_lune.mid')
#playMidi('Maple_Leaf_Rag_MIDI.mid')
#playMidi('jules_mad_world.mid')
#playMidi('Pinkfong-Babyshark-Anonymous-20190203093900-nonstop2k.com.mid')
#playMidi('080-Finale.mid')
#playMidi('gwyn_by_nitro.mid')
#playMidi('Westworld_Theme.mid')
#playMidi('Smash_Mouth.mid')
#playMidi('vangelis_-_chariots_of_fire_ost_bryus_vsemogushchiy.mid')
#playMidi('GameofThrones.mid')
#playMidi('Welcome_to_Jurassic_World.mid')
#playMidi('Games_of_Thrones_piano_cover_by_Lisztlovers.MID')
#playMidi('Sonic.mid')
#playMidi('Moana.mid')
#playMidi('HesaPirate.mid')
#playMidi('ChamberOfSecrets-HedwigsTheme.mid')
#playMidi('DuelOfTheFates.mid')
#playMidi('Star-Wars-Imperial-March.mid')
#playMidi('PianoMan.mid')
#playMidi('the_entertainer.mid')
#playMidi('chopin_minute.mid')
