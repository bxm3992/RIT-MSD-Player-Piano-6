//Blaise Teensy Threading Code
//last update: 1/25/22

#include <TeensyThreads.h>
#define HWSERIAL1 Serial1
int ledPin = 13;
int ledState=LOW;

//timing/velocity variables
double distance = 0.0139954; //.551 inches to meters
double startTime=0;
double startTime1=0;
double endTime=0;
double endTime1=0;
double timeTravel = 0;
double timeTravel1 = 0; 
double velocity = 0;
double velocity1 = 0;

//key variables
int keyArray[5] = {0,0,0,0,0};
bool currentKeyPress = false;
bool currentKeyPress1 = false;
volatile int global_val0=0;
volatile int global_val1=0;

//constantly reads value from input to teensy
void thread_func_getValues(){
  while(1){
    volatile int temp_val = analogRead(0);
    global_val0=temp_val;
    volatile int temp_val1 = analogRead(1);
    global_val1=temp_val1;
    delay(25);
  }
}

int temp_displayArray[5] = {0,1,2,3,4};
//constantly prints the array the represents the keys
void thread_displayThread(){
  while(1){
    //Serial.print("Value of Key0: ");
    //Serial.println(global_val0);
    //Serial.print("Value of Key1: ");
    //Serial.println(global_val1);
    
    printArray_five(temp_displayArray,0);
    printArray_five(keyArray,1);
    delay(100);
    
  }
}

//function to print the array output
void printArray_five(int temp_array[],int temp_end){
  Serial.print("[ ");
  Serial.print(temp_array[0]);
  Serial.print(", ");
  Serial.print(temp_array[1]);
  Serial.print(", ");
  Serial.print(temp_array[2]);
  Serial.print(", ");
  Serial.print(temp_array[3]);
  Serial.print(", ");
  Serial.print(temp_array[4]);
  Serial.println(" ]");
  
  if(temp_end == 1){
    Serial.println("-----------------");
  }
}

//function to print the velocity
void print_velocity(int time_travel_temp,int key_num_temp){
      Serial.print("Key ");
      Serial.print(key_num_temp);
      Serial.println(" has been pressed");
      Serial.print("It took this many ms to be pressed: ");
      Serial.println(timeTravel,4);
      Serial.print("The velocity must be: ");
      velocity=(distance)/(timeTravel*.001); //double the distance 
      Serial.println(velocity,4);
}

void thread_func_currKeyPress(){
  //while a keypress is currently happening
  while(1){
      //int val = analogRead(0);
      //Serial.println("Keypress has happened");
      if(global_val0 > 700 && currentKeyPress){
        endTime = millis();
        
        digitalWrite(ledPin,ledState=LOW);
        
        timeTravel = endTime - startTime;
        //print_velocity(timeTravel,0);
        keyArray[0]=1;
        
        currentKeyPress = false;
      }
      if(global_val1 > 630 && currentKeyPress1){
        endTime1 = millis();
        
        digitalWrite(ledPin,ledState=LOW);
        
        //timeTravel1 = endTime1 - startTime1;
        //print_velocity(timeTravel1,1);
        keyArray[1]=1;
        
        currentKeyPress1 = false;
      }
      delay(25);
    }
}

void thread_func_waitingKeyPress(){
  //while a keypress is not happening
  while(1){
      //int val = analogRead(0);
      //Serial.println("Keypress has not happened");
      //Serial.println(val);
      if(global_val0 < 620 && !currentKeyPress){
        startTime = millis();
        digitalWrite(ledPin,ledState=HIGH);
        currentKeyPress = true;
      }
      if(global_val1 < 520 && !currentKeyPress1){
        startTime1 = millis();
        digitalWrite(ledPin,ledState=HIGH);
        currentKeyPress1 = true;
      }
      //keys arent pressed so reset to 0
      memset(keyArray,0,sizeof(keyArray));
      delay(25);
  }
}

int currPressThread;
int waitPressThread;
int getValueThread;
int displayThread;

void setup() {
    HWSERIAL1.begin(9600);
    Serial.begin(9600);
    pinMode(ledPin,OUTPUT);
    currPressThread= threads.addThread(thread_func_currKeyPress,1);
    waitPressThread= threads.addThread(thread_func_waitingKeyPress,1);
    getValueThread= threads.addThread(thread_func_getValues,1);
    displayThread= threads.addThread(thread_displayThread,1);
}


void loop() {
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)
  while(1){
    //Serial.print("The currePressThread is: ");
    //Serial.println(threads.getState(currPressThread));
    //Serial.print("The waitPressThread is: ");
    //Serial.println(threads.getState(waitPressThread));
    //Serial.print("The getValueThread is: ");
    //Serial.println(threads.getState(getValueThread));
    //delay(1000);
  }
}
