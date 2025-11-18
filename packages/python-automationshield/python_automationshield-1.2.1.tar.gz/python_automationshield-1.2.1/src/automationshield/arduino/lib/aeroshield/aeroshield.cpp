# include <aeroshield.h>

void AeroShield::setup() {
    AutomationShield::setup();
    angleSensor.begin(0);
}

void AeroShield::receive(int &flag, int &actuator) {
    Serial.readBytes(inBuffer, inSize);
    flag = inBuffer[0];
    actuator = inBuffer[1];
}

int AeroShield::sensorRead() {
    return angleSensor.rawAngle();
}

void AeroShield::actuatorWrite(int actuator) {
    analogWrite(actuatorPin, actuator);
}