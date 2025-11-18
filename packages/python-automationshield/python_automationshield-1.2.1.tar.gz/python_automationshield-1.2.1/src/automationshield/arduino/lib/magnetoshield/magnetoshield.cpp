#include <magnetoshield.h>

void MagnetoShield::setup() {
    AutomationShield::setup();

    analogReference(EXTERNAL);
}