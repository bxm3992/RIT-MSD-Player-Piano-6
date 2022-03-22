
byte ledPin = 13;   // the onboard LED

//===============

void setup() {
    Serial.begin(115200);

    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
    digitalWrite(ledPin, HIGH);

    //Serial.println("<Arduino is ready>");
    delay(5000);
    digitalWrite(ledPin, LOW);
}

//===============
byte arraySent[4] = {49,50,51,52};
char i = 48;

void loop() {
    int bytesSent = Serial.write(arraySent,sizeof(arraySent));
    delay(1000);
    arraySent[3]=i;
    i++;
    //Serial.println(bytesSent);
    //Serial.print("Sent: ");
    //Serial.println(bytesSent);
}
