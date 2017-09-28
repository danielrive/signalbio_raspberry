
#include <SoftwareSerial.h>

SoftwareSerial BTserial(10,9); // RX | TX  

void setup() {
Serial.begin(9600);
BTserial.begin(9600); 
}

void loop() {
BTserial.println(analogRead(A0));
BTserial.flush();  
}
 
