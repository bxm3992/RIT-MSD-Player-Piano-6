#define HWSERIAL1 Serial1
int ledPin = 13;
int ledState=LOW;
bool currentKeyPress = false;

void setup() {
    HWSERIAL1.begin(9600);
    Serial.begin(9600);
    pinMode(ledPin,OUTPUT);
}

void loop() {
  

int digval=0;
//while a keypress is currently happening
while(currentKeyPress){
  int val = analogRead(0);
  //Serial.println("Keypress has happened");
  if(val > 700){
    digitalWrite(ledPin,ledState=LOW);
    digval=0;
    Serial.println("Key 0 has been pressed");
    currentKeyPress = false;
  }
  delay(50);
}
//while a keypress is not happening
while(!currentKeyPress){
  int val = analogRead(0);
  //Serial.println("Keypress has not happened");
  //Serial.println(val);
  if(val < 500){
    digitalWrite(ledPin,ledState=HIGH);
    digval=1;
    currentKeyPress = true;
  }
  delay(50);
}
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)
}
