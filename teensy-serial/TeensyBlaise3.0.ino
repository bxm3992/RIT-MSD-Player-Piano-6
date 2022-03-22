//Blaise Teensy Threading Code
//last update: 1/26/22
//https://stackoverflow.com/questions/47101062/python-serial-communication-arduino-teensy-to-raspberry-pi?noredirect=1&lq=1

#include <TeensyThreads.h>
#define HWSERIAL1 Serial1
int ledPin = 13;
int ledState=LOW;
bool currentKeyPress = false;

void thread_func_currKeyPress(){
  //while a keypress is currently happening
  while(currentKeyPress){
    int val = analogRead(0);
    int val2 = analogRead(1);
    //Serial.println("Keypress has happened");
    if(val > 700){
      digitalWrite(ledPin,ledState=LOW);
      Serial.println("Key 0 has been pressed");
      currentKeyPress = false;
    }
    if(val2 > 700){
      digitalWrite(ledPin,ledState=LOW);
      Serial.println("Key 1 has been pressed");
      currentKeyPress = false;
    }
    delay(50);
  }
}

void thread_func_waitingKeyPress(){
  //while a keypress is not happening
  while(!currentKeyPress){
    int val = analogRead(0);
    int val2 = analogRead(1);
    //Serial.println("Keypress has not happened");
    //Serial.println(val);
    if(val < 500){
      digitalWrite(ledPin,ledState=HIGH);
      currentKeyPress = true;
    }
    if(val2 < 500){
      digitalWrite(ledPin,ledState=HIGH);
      currentKeyPress = true;
    }
  delay(50);
  }
}

unsigned long s = 0;
void setup() {
    HWSERIAL1.begin(0);
    Serial.begin(0);
    pinMode(ledPin,OUTPUT);
    //threads.addThread(thread_func_currKeyPress,1);
    //threads.addThread(thread_func_waitingKeyPress,1);
}


void loop() {
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)
  if(Serial.available() > 0){
    while(Serial.available() > 0){//Buffer memory must always be clean !
        char read = Serial.read();
        delay(1);//wait until next_char
        }
    Serial.print("TEST : ");
    Serial.println(s, DEC);
    s++;
   }

}
