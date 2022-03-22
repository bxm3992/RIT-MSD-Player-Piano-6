//Blaise Teensy Threading Code
//last update: 1/25/22

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <TeensyThreads.h>
#include "MY_HEADER.h" 
#define HWSERIAL1 Serial1
int ledPin = 13;
int ledState=LOW;

//timing/velocity variables
double distance = 0.0139954; //.551 inches to meters
double current_time = 0.0;

double startTime_array[88]={0};
double endTime_array[88]={0};
double timeTravel_array[88]={0};
double velocity_array[88]={0};


//key variables
bool currentKeyPress_array[88] = {false};
volatile int global_val_array[88]= {0};

//Midi variables
int velocity = 100;//velocity of MIDI notes, must be between 0 and 127
int noteON = 144;//144 = 10010000 in binary, note on command
int noteOFF = 128;//128 = 10000000 in binary, note off command
int temp_time = 0;

//threading variables
int getValueThread;
int getkeyWatchThread_array[88];
int getsendSerialDataThread;

//linked list variables
struct Linked_List* serial_data_LL = NULL;
int linked_list_size = 0; //this is the size of the linked list too

//below is main code functions
//========================================================================
//========================================================================

//constantly reads value from input to teensy -- *consider making 4 threads for each 22 keys (optimize reading per board)*
void thread_func_getValues(){
  while(1){
  current_time=millis();
  for (int x=0; x<88; ++x){ //between 0 and 87 cuz 88 values
    volatile int temp_val = analogRead(x);
    global_val_array[x]=temp_val;
  }
    //delay(25); //likely dont need delay
  }
}

//constantly checks two functions for each key and will send trigger data to stack
void thread_func_keyWatch(int key){
  while(1){
  //current time get??
    if(currentKeyPress_array[key]){
      func_currKeyPress(key);
    }
    else{
      func_waitingKeyPress(key);
    }
    delay(10); 
  }
}

//constantly checks the LL if theres an element (new note) added to the back and will
//then remove an element from the front which also sends the data of the note over serial
void thread_func_sendSerialData(){
  while(1){
    //check if element in the linked list
    if(linked_list_size>0){
      deleteLinked_List(&serial_data_LL);
    }
    delay(25);
  }
}

//function to print the velocity
void print_velocity(int time_travel_temp,int key_num_temp){
      Serial.print("Key ");
      Serial.print(key_num_temp);
      Serial.println(" has been pressed");
      Serial.print("It took this many ms to be pressed: ");
      Serial.println(timeTravel_array[key_num_temp],4);
      Serial.print("The velocity must be: ");
      velocity=(distance)/(timeTravel_array[key_num_temp]*.001); //double the distance 
      Serial.println(velocity,4);
}

void func_currKeyPress(int key){
  //while a keypress is currently happening
  while(1){
      if(global_val_array[key] > 700 && currentKeyPress_array[key]){
        endTime_array[key] = millis();
        
        timeTravel_array[key] = endTime_array[key] - startTime_array[key]; 
    velocity_array[key]=(distance)/(timeTravel_array[key]*.001);
        
    //send info
    struct midiData temp_data;
    temp_data.midi_command=noteOFF;
    temp_data.midi_note=key;
    temp_data.midi_velocity=velocity_array[key];
    temp_data.midi_time=endTime_array[key];
    
    insertAfter(serial_data_LL, temp_data);
        
        currentKeyPress_array[key] = false;
      }
      delay(25);
    }
}

void func_waitingKeyPress(int key){
  //while a keypress is not happening
  while(1){
      if(global_val_array[key] < 620 && !currentKeyPress_array[key]){
        startTime_array[key] = millis();
    
    //send info
    struct midiData temp_data;
    temp_data.midi_command=noteON;
    temp_data.midi_note=key;
    //this needs to be addressed below
    temp_data.midi_velocity= distance /((startTime_array[key] - current_time)*.001);
    temp_data.midi_time=startTime_array[key];
    
    insertAfter(serial_data_LL, temp_data);
    
        currentKeyPress_array[key] = true;
      }
      delay(25);
  }
}

//send MIDI message
void my_MIDImessage(int command, int MIDInote, int MIDIvelocity, int temp_time) {
  Serial.write(command);//send note on or note off command 
  Serial.write(MIDInote);//send pitch data
  Serial.write(MIDIvelocity);//send velocity data
  Serial.write(temp_time); //send temporary time
}

void setup() {
  //open serial
    Serial1.begin(115200);

  //distinguishable flashing of LED for prep. on-off-on, stay during delay then off
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
    digitalWrite(ledPin, HIGH);

    //Serial.println("<Arduino is ready>");
    delay(8000);
    digitalWrite(ledPin, LOW);
  
  //initialize threads: get data / serial connection / key watching threads
    getValueThread= threads.addThread(thread_func_getValues,1);
  getsendSerialDataThread= threads.addThread(thread_func_sendSerialData,1);
  for (int x=0; x<88; ++x){ //between 0 and 87 cuz 88 values
    getkeyWatchThread_array[x] = threads.addThread(thread_func_keyWatch,x);
  }
  current_time=millis();
  
  //struct midiData temp_data;
  //temp_data.midi_command=noteON;
  //temp_data.midi_note=0;
  //temp_data.midi_velocity=0;
  //temp_data.midi_time=0;
  //insertAtBeginning(serial_data_LL, temp_data);
  
}


void loop() {
//base value is 790 (could be alterd by resistor, no magnet)
//lowest value is ~280 (closest magnet)
  
  while(1){
  //thread  
  }
  
}

//below is functions for linked-list usage
//========================================================================
//========================================================================

//defined structure that holds all the info the serial data requires for the thread

//typedef struct midiData {
//        int midi_command;
//        int midi_note;
//        int midi_velocity;
//        int midi_time;
//} midiData;
//
//// Create a Linked_List
//typedef struct Linked_List {
//        struct midiData data;
//        struct Linked_List *next;
//} Linked_List;


// Insert at the beginning
void insertAtBeginning(struct Linked_List** head_ref,struct midiData new_data) {
  // Allocate memory to a Linked_List
  struct Linked_List* new_Linked_List = (struct Linked_List*)malloc(sizeof(struct Linked_List));

  // insert the data
  new_Linked_List->data = new_data;

  new_Linked_List->next = (*head_ref);

  // Move head to new Linked_List
  (*head_ref) = new_Linked_List;
  
  //increase key size
  linked_list_size++;
}

// Insert a Linked_List after a Linked_List
void insertAfter(struct Linked_List* prev_Linked_List,struct midiData new_data) {
  if (prev_Linked_List == NULL) {
  struct Linked_List* new_Linked_List = (struct Linked_List*)malloc(sizeof(struct Linked_List));
  new_Linked_List->data = new_data;
  new_Linked_List->next = NULL;
  prev_Linked_List = new_Linked_List; //set null list to new real list?
  return;
  }

  struct Linked_List* new_Linked_List = (struct Linked_List*)malloc(sizeof(struct Linked_List));
  new_Linked_List->data = new_data;
  new_Linked_List->next = prev_Linked_List->next;
  prev_Linked_List->next = new_Linked_List;
  
  //increase key size
  linked_list_size++;
}

// Insert the the end
void insertAtEnd(struct Linked_List** head_ref,struct midiData new_data) {
  struct Linked_List* new_Linked_List = (struct Linked_List*)malloc(sizeof(struct Linked_List));
  struct Linked_List* last = *head_ref; /* used in step 5*/

  new_Linked_List->data = new_data;
  new_Linked_List->next = NULL;

  if (*head_ref == NULL) {
  *head_ref = new_Linked_List;
  return;
  }

  while (last->next != NULL) last = last->next;

  last->next = new_Linked_List;
  
  //increase key size
  linked_list_size++;
  
  return;
}

// Delete a Linked_List
void deleteLinked_List(struct Linked_List** head_ref) {
  struct Linked_List *temp = *head_ref, *prev;
  
  //make current pointer the next LL element, send serial data, free old element space, decrease counter
  if (temp != NULL) {
    *head_ref = temp->next;
    midiData temp_data = temp->data;
    my_MIDImessage(temp_data.midi_command,temp_data.midi_note,temp_data.midi_velocity,temp_data.midi_time);
    free(temp);
    linked_list_size--;
    return;
  }
  else{
    return;
  }
}

// Search a Linked_List
int searchLinked_List(struct Linked_List** head_ref,struct midiData key) {
  struct Linked_List* current = *head_ref;

  while (current != NULL) {
  if (compare_midiData(current->data,key)) return 1;
  current = current->next;
  }
  return 0;
}

bool compare_midiData(struct midiData data1, struct midiData data2){
  return true;
}
