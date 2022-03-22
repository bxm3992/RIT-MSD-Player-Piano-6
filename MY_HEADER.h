#ifndef MY_HEADER   /* Include guard */
#define MY_HEADER

//defined structure that holds all the info the serial data requires for the thread
typedef struct midiData {
        int midi_command;
        int midi_note;
        int midi_velocity;
        int midi_time;
} midiData;

// Create a Linked_List
typedef struct Linked_List {
        struct midiData data;
        struct Linked_List *next;
} Linked_List;

#endif // MY_HEADER