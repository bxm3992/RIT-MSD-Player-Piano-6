#include <MIDI.h>
#include "USBHost_t36.h"

const int channel = 1;
byte ledPin = 13;   // the onboard LED

//===============


void setup() {
    Serial1.begin(115200);

    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
    digitalWrite(ledPin, HIGH);

    //Serial.println("<Arduino is ready>");
    delay(8000);
    digitalWrite(ledPin, LOW);
}

//===============
int velocity = 100;//velocity of MIDI notes, must be between 0 and 127
int noteON = 144;//144 = 10010000 in binary, note on command
int noteOFF = 128;//128 = 10000000 in binary, note off command
int temp_time = 0;

void loop() {
  for (int note=1;note<89;note++) {//from note 50 (D3) to note 69 (A4)
    my_MIDImessage(noteON, note, velocity,temp_time);//turn note on
    delay(500);//hold note for 300ms
    temp_time=temp_time+5;
    my_MIDImessage(noteOFF, note, velocity,temp_time);//turn note off
    delay(2000);//wait 200ms until triggering next note
    temp_time=temp_time+20;
  }
}
//send MIDI message
void my_MIDImessage(int command, int MIDInote, int MIDIvelocity, int temp_time) {
  Serial.write(command);//send note on or note off command 
  Serial.write(MIDInote);//send pitch data
  Serial.write(MIDIvelocity);//send velocity data
  Serial.write(temp_time); //send temporary time
}
