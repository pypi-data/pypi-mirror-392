#ifndef AEROSHIELD
#define AEROSHIELD

#include <automationshield.h>
#include <AS5600.h>

class AeroShield : public AutomationShield {
    public:
        AeroShield(): AutomationShield((byte)0x41, (byte)0x45, 2, 3, A3, (uint8_t)0, (uint8_t)5) {};
        void setup(void);

    private:
        AS5600 angleSensor;

        int sensorRead(void);
        void receive(int &flag, int &actuator);
        void actuatorWrite(int actuator);
};

#endif