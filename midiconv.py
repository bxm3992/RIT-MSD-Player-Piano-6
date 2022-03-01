"""
Takes a MIDI file and converts it into a text file, which will then insert the velocity measurements into the MIDI file.
"""
#import play_midi_conv as pm
import sys
import os
import time
import threading
import serial as s
from mido import Message, MidiFile, MidiTrack

########### BELOW IS USED FOR MANUAL MIDI PROCESSING USING MF2TXP.EXE PROGRAM ############
##########################################################################################
def editMidi(note):
    midiFile = input("Insert midi name (don't include file extension): ")
    absPath = os.path.abspath("midifiles/mf2tXP.exe")
    midiPath = os.path.abspath("midifiles/" + midiFile)
    os.system(absPath + ' ' + midiPath + ".mid" + ' ' + midiPath + ".txt")

    # Now edit the MIDI text file to have the proper velocity measurements
    i = 0
    midiTxt = os.path.abspath("midifiles/" + midiFile + ".txt")
    # testFile = open("midifiles/test.txt", 'w')
    # Skip the first 12 lines within a MIDI file since they're not tampered with
    midiRead = open(midiTxt, 'r')
    lines = midiRead.readlines()
    strLst = []
    newstrLst = []
    for line in lines:
        if i < 12:
            i += 1
            newstrLst.append(line.split(" "))
            continue
        strLst.append(line)
    length = 1
    for string in strLst:
        if length == len(strLst)-1:
            break
        # Separate the string
        newStr = string.split(" ")
        # Check/ignore the cases within the midi file that don't include the playing of piano keys
        if newStr[0] == "0" or newStr[0] == "1" or newStr[0] == "TrkEnd\n" or newStr[0] == "MTrk\n":
            newstrLst.append(newStr)
            continue
        if len(newStr) > 1 and newStr[1] == "Meta":
            newstrLst.append(newStr)
            continue
        # Change the velocity value
        # TODO stop point: EDIT SPECIFIC PIANO KEY/NOTE With DIFFERENT VELOCITY VALUES
        # vel = changekeyVel(note)
        # newStr[4] = "v=" + str(vel) + "\n"
        newStr[4] = "v=0\n"
        # Put the edited string into a new list
        newstrLst.append(newStr)
        length += 1
    midiRead.close()

    # Write back to the midifile with the edited velocity values
    miditestTxt = os.path.abspath("midifiles/" + midiFile + "_Test" + ".txt")
    midiWrite = open(miditestTxt, 'w')
    for lst in newstrLst:
        toStr = listToString(lst)
        editedLine = "".join(toStr).lstrip()
        midiWrite.write(editedLine)
    midiWrite.close()


def listToString(s): 
    str1 = "" 
    for ele in s: 
        str1 += ' ' + ele 
    return str1


def changekeyVel(note):
    pass


def waitforkeyPress(key):
    # Velocity value ranges from 0-127
    vel = 0
    recordedVel = 0
    # If the value of keypress != 0, then it's still being pressed
    while (key != 0): ## May have to change while loop condition, not sure if this is the proper way to detect keypress
        # Record the time the key is being pressed for
        start = time.time()
    end = time.time()
    elapsedTime = (end - start) * 1000 # in milliseconds
    # Any keypress longer than 300 ms is considered quiet
    if (elapsedTime > 300):
        vel = 0
    # Else, convert the velocity of data 
    vel = elapsedTime * recordedVel
    # Put it into MIDI velocity parameter
    return vel
##########################################################################################


###################### BELOW IS USED FOR SERIAL MIDI PROCESSING ##########################
##########################################################################################

#TODO: Make MIDI file from tracks that is sent over serial
# Try to edit velocity values from tracks being sent

def createMIDI():
    flag = False
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    ser = serial.Serial('', ) # Need to specify port and baud rate
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
        

##########################################################################################


# Main function to process/run made functions
def main():
    #editMidi()
    createMIDI()


if __name__ == "__main__":
    main()
