
long test1, test2, test3, test4,  test5, test6, test7, test8= 0x00;
int sec = 0x00;
int third = 0x00;
int fourth = 0x00;
int first = 0x00;

#define HWSERIAL1 Serial1
#define HWSERIAL2 Serial2
#define HWSERIAL3 Serial3

void setup() {
    HWSERIAL1.begin(9600);
    HWSERIAL2.begin(9600);
    HWSERIAL3.begin(9600);
    Serial.begin(9600);
}




void loop() {
  
 HWSERIAL1.write(0x11);
 if (HWSERIAL1.available()){
 test1=HWSERIAL1.read();
 test2=HWSERIAL1.read();
 test3=HWSERIAL1.read();
 test4=HWSERIAL1.read();
 }

 HWSERIAL2.write(0x22);
 if (HWSERIAL2.available()){
 test5=HWSERIAL2.read();
 test6=HWSERIAL2.read();
 test7=HWSERIAL2.read();
 test8=HWSERIAL2.read();
 }

HWSERIAL3.write(0x33);
if (HWSERIAL3.available()){
 first=HWSERIAL3.read();
 sec=HWSERIAL3.read();
 third=HWSERIAL3.read();
 fourth=HWSERIAL3.read();}
  
  Serial.print(test1,HEX);
  Serial.print(test2,HEX);
  Serial.print(test3,HEX);
  Serial.print(test4,HEX);
  Serial.print(" ");
  Serial.print(test5,HEX);
  Serial.print(test6,HEX);
  Serial.print(test7,HEX);
  Serial.print(test8,HEX);
  Serial.print(" ");
  Serial.print(first,HEX);
  Serial.print(sec,HEX);
  Serial.print(third,HEX);
  Serial.print(fourth,HEX);
  Serial.println("\n");

  delay(10);
}
