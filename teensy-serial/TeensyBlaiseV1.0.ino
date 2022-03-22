#define HWSERIAL1 Serial1
int ledPin = 13;
int ledState=LOW;
bool currentKeyPress = false;
float startTime=0;
float endTime=0;
float timeTravel = 0; 
float distance = 0.0139954; //.551 inches to meters
float velocity = 0;

void setup() {
    HWSERIAL1.begin(9600);
    Serial.begin(9600);
    pinMode(ledPin,OUTPUT);
}

void loop() {
  

//while a keypress is currently happening
while(currentKeyPress){
  int val = analogRead(0);
  //Serial.println("Keypress has happened");
  if(val > 700){ //key has been unpressed, therefore a keypress has occured
    endTime = millis(); //get time was unpressed
    digitalWrite(ledPin,ledState=LOW);
    timeTravel = endTime - startTime; //calc total time spent to press
    Serial.println("Key 0 has been pressed");
    Serial.print("It took this many ms to be pressed: ");
    Serial.println(timeTravel);
    Serial.print("The velocity must be: ");
    velocity=distance/(timeTravel*.001);
    Serial.println(velocity);
    currentKeyPress = false;
    startTime=0;endTime=0;timeTravel=0;velocity=0; //reset all values
  }
  delay(50);
}
//while a keypress is not happening
while(!currentKeyPress){
  int val = analogRead(0);
  //Serial.println("Keypress has not happened");
  //Serial.println(val);
  if(val < 500){ //key has been pressed, therefore a keypress has started
    startTime = millis(); //get time that press started
    digitalWrite(ledPin,ledState=HIGH);
    currentKeyPress = true;
  }
  delay(50);
}
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)
}
