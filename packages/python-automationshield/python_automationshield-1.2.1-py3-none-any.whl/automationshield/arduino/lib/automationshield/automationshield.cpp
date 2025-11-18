#include <automationshield.h>

AutomationShield::AutomationShield(
    byte id1, byte id2, int inSize, int outSize, uint8_t potPin, uint8_t sensorPin, uint8_t actuatorPin
    ):
    shield_id({id1, id2}),
    inSize(inSize),
    outSize(outSize),
    inBuffer(new byte[inSize]),
    outBuffer(new byte[outSize]),
    potPin(potPin),
    sensorPin(sensorPin),
    actuatorPin(actuatorPin)
{}


void AutomationShield::setup() {
    Serial.begin(115200);
    Wire.begin();
}

void AutomationShield::receive(int &flag, int &actuator) {
    Serial.readBytes(inBuffer, inSize);
    flag = inBuffer[0];
    actuator = (inBuffer[1] << 8) + inBuffer[2];
}

void AutomationShield::send() {
    Serial.write(outBuffer, outSize);
}

int AutomationShield::sensorRead() {
    return analogRead(sensorPin);
}

int AutomationShield::referenceRead() {
    return analogRead(potPin);
}

void AutomationShield::actuatorWrite(int DAClevel) {
    Wire.beginTransmission(MCP4725); 					//addressing
    Wire.write(0x40); 						    		// write dac(DAC and EEPROM is 0x60)
    uint8_t firstbyte=(DAClevel>>4);					//(0,0,0,0,0,0,0,0,D11,D10,D9,D8,D7,D6,D5,D4) of which only the 8 LSB's survive
    DAClevel = DAClevel << 12;  						//(D3,D2,D1,D0,0,0,0,0,0,0,0,0,0,0,0,0)
    uint8_t secndbyte=(DAClevel>>8);					//(0,0,0,0,0,0,0,0,D3,D2,D1,D0,0,0,0,0) of which only the 8 LSB's survive.
    Wire.write(firstbyte);                              //first 8 MSB's
    Wire.write(secndbyte);                              //last 4 LSB's
    Wire.endTransmission();
}

void AutomationShield::setOutBuffer(int &v1, int &v2) {
    outBuffer[0] = ((v1 >> 4) & 0xF0) + (v2 >> 8);
    outBuffer[1] = v1 & 0xFF;
    outBuffer[2] = v2 & 0xFF;
}

void AutomationShield::loop() {
    if (Serial.available() > 0){

        static int flag;
        static int actuator;
        static int sensor;
        static int pot;

        receive(flag, actuator);

        switch(flag) {
            case TEST: {
                outBuffer[0] = version;
                outBuffer[1] = shield_id[0];
                outBuffer[2] = shield_id[1];
                break;
            }
            case RUN: {
                actuatorWrite(actuator);
                sensor = sensorRead();
                pot = referenceRead();
                setOutBuffer(pot, sensor);
                break;
            }
            case STOP: {
                actuatorWrite(0);
                break;
            }
        }
        send();
    }
}
