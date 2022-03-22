
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

    Serial.println("<Arduino is ready>");
    delay(5000);
    digitalWrite(ledPin, LOW);
}

//===============

void loop() {
    Serial.println("<Hello from Arduino!>\n");
    delay(1000);
}
