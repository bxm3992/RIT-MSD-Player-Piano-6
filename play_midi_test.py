"""
MIDI Play
Originated: 19363
    Author: Curtis Geiger
Adapted: 21363
    Author: Steven Petrick
            Josiah Martuscello

MIDI interpetation and play functionality
Meant to be threaded via server JavaScript to perform MIDI play
------------------
Example Usages:
Play Doctor Who midifile - note: you need the relative or absolute filepath name to the midifile
python3 play_midi.py play ./midifiles/DoctorWho.mid

Play Pirates at a specific tempo @ 160
python3 play_midi.py play ./midifiles/DoctorWho.mid 160

Print the tempo of Sweden
python3 play_midi.py tempo ./midifiles/DoctorWho.mid

Reset all keys
python3 play_midi.py reset
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
flag=False
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

    #set all keys to 0
    for x in range(88):  # Go through all 88 keys   
        tlc5947[x] = 0
        continue

    #call to the function that does the testing for threading
    print('starting threads...')
    input_thread=threading.Thread(target=get_input)
    testing_thread=threading.Thread(target=testing)

    testing_thread.start()
    input_thread.start()
    
    while(not(flag)):
        continue

    print("Finished playing....")     
    reset_key()

def testing():
    global flag
    global keyNum

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
    keyNum=0
    while(flag != True):
        # send array to PWM IC, set current key to 'actve'
        temp_PWMvalue = 4090
        tlc5947[keyNum]= temp_PWMvalue
        tlc5947.write()
        print("value written. key is currently: ",keyNum) #uncomment write when ready
        #removed sustain pedal functionality
        time.sleep(5)
        if flag ==True:
            print('The loop will now close.')

#wait for constant input
#if input is enter, break test
#if input anything else, increment the key
def get_input():
    global flag
    global keyNum
    while(1):    
        keystroke = input('input i to increment, c to close testing program \n')
        #freezes thread until keypress
        print('you pressed:', keystroke)
        if keystroke == 'c':
            flag=True
            break
        elif keystroke == 'i':
            #check if over 88 keys
            if (keyNum >= 88):
                keyNum = 0
            elif (keyNum < 88):    
                keyNum= keyNum+1
        else:
            continue

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
