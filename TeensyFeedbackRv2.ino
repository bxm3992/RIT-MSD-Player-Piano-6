const int NUM_PINS = 32;
//int pin_nums[NUM_PINS] = {0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 39, 38, 37, 36, 35};
int pin_nums[NUM_PINS] = {28, 27, 25, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 35, 36, 37, 38, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 33, 33, 33, 33, 33};
long keys = 0x00000000;
long test1, test2, test3, test4,  test5, test6, test7, test8= 0x00;
int sec = 0x00;
int third = 0x00;
int fourth = 0x00;
int first = 0x00;

#define HWSERIAL1 Serial1

void setup() {
  // put your setup code here, to run once:
  for (int i = 0; i < NUM_PINS; i++){
    pinMode(pin_nums[i], INPUT);
  }

    HWSERIAL1.begin(9600);
}




void loop() {
  // put your main code here, to run repeatedly:
  int bcnt = 7;
  int Bcnt = 0;
  
  for (int i=0; i < NUM_PINS; i++){
    if (Bcnt == 0){
      bitWrite(first, bcnt, digitalRead(pin_nums[i]));
      bcnt--;
    }else if (Bcnt == 1){
      bitWrite(sec, bcnt, digitalRead(pin_nums[i]));
      bcnt--;
    }else if (Bcnt == 2){
      bitWrite(third, bcnt, digitalRead(pin_nums[i]));
      bcnt--;
    }else{
      bitWrite(fourth, bcnt, digitalRead(pin_nums[i]));
      bcnt--;
    }

    if (bcnt == -1){
      bcnt = 7;
      Bcnt++;
    }
  }

  Serial.print(first, HEX);
  HWSERIAL1.write(first);
  Serial.print(sec, HEX);
  HWSERIAL1.write(sec);
  Serial.print(third, HEX);
  HWSERIAL1.write(third);
  Serial.print(fourth, HEX);
  HWSERIAL1.write(fourth);

  
  
  keys = 0x00000000;
  delay(10);
}
