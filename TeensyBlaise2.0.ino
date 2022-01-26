//Blaise Teensy Threading Code
//last update: 1/25/22

#include <TeensyThreads.h>
#define HWSERIAL1 Serial1
int ledPin = 13;
int ledState=LOW;
bool currentKeyPress = false;

void thread_func_currKeyPress(){
  //while a keypress is currently happening
  while(currentKeyPress){
    int val = analogRead(0);
    Serial.println("Keypress has happened");
    if(val > 700){
      digitalWrite(ledPin,ledState=LOW);
      Serial.println("Key 0 has been pressed");
      currentKeyPress = false;
    }
    delay(50);
  }
}

void thread_func_waitingKeyPress(){
  //while a keypress is not happening
  while(!currentKeyPress){
    int val = analogRead(0);
    Serial.println("Keypress has not happened");
    //Serial.println(val);
    if(val < 500){
      digitalWrite(ledPin,ledState=HIGH);
      currentKeyPress = true;
    }
  delay(50);
  }
}

void setup() {
    HWSERIAL1.begin(9600);
    Serial.begin(9600);
    pinMode(ledPin,OUTPUT);
    threads.addThread(thread_func_currKeyPress,1);
    threads.addThread(thread_func_waitingKeyPress,1);
}


void loop() {
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)


}
