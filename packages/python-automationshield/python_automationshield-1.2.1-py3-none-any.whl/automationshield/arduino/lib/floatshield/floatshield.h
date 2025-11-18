#ifndef FLOATSHIELD
#define FLOATSHIELD

#include <automationshield.h>
#include <VL53L0X.h>

class FloatShield : public AutomationShield {
    public:
        FloatShield(): AutomationShield((byte)0x46, (byte)0x4c, 3, 3, A0, (uint8_t)0, (uint8_t)0) {};
        void setup(void);

    private:
        VL53L0X distanceSensor;

        int sensorRead(void);
};

#endif
