#ifndef MAGNETOSHIELD
#define MAGNETOSHIELD

#include <automationshield.h>

class MagnetoShield : public AutomationShield {
    public:
        MagnetoShield(): AutomationShield((byte)0x4d, (byte)0x47, 3, 3, A0, A3, (uint8_t)0) {};
        void setup(void);
};

#endif
