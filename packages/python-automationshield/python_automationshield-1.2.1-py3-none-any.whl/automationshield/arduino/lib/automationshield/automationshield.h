#ifndef AUTOMATIONSHIELD
#define AUTOMATIONSHIELD

#include <Wire.h>
#include <Arduino.h>

class AutomationShield{
    public:
        AutomationShield(byte id1, byte id2, int inSize, int outSize, uint8_t potPin, uint8_t sensorPin, uint8_t actuatorPin);

        virtual void setup(void);
        void loop(void);

    protected:
        static const int TEST = 0;
        static const int RUN = 1;
        static const int STOP = 2;

        const int potPin;
        const int sensorPin;
        const int actuatorPin;

        const byte MCP4725 = (0x60);

        const int inSize;
        const int outSize;

        byte* inBuffer;
        byte* outBuffer;

        const int version = 1;
        byte shield_id[2];

        virtual void receive(int &flag, int &actuator);
        void send(void);
        virtual int sensorRead(void);
        int referenceRead(void);
        virtual void actuatorWrite(int DAClevel);
        void setOutBuffer(int &pot, int &sensor);
};

#endif
