//Blaise Teensy Velocity Code
//last update: 1/24/22
#define HWSERIAL1 Serial1

int ledPin = 13;
int ledState=LOW;
bool currentKeyPress = false;
double startTime=0;
double endTime=0;
double timeTravel = 0; 
double distance = 0.0139954; //.551 inches to meters
double velocity = 0;

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
  //Serial.println(val);
  if(val > 550){ //key has been unpressed, therefore a keypress has occured
    endTime = millis(); //get time was unpressed
    digitalWrite(ledPin,ledState=LOW);
    timeTravel = endTime - startTime; //calc total time spent to press
    Serial.println("Key 0 has been pressed");
    Serial.print("time start: ");
    Serial.println(startTime,4);
    Serial.print("time end: ");
    Serial.println(endTime,4);
    Serial.print("It took this many ms to be pressed: ");
    Serial.println(timeTravel,4);
    Serial.print("The velocity must be: ");
    velocity=(distance)/(timeTravel*.001); //double the distance 
    Serial.println(velocity,4);
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
  if(val < 550){ //key has been pressed, therefore a keypress has started
    startTime = millis(); //get time that press started
    if(val < 350){
      digitalWrite(ledPin,ledState=HIGH);
      currentKeyPress = true;
    }
  }
  delay(50);
}
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)
}
