#include <floatshield.h>

void FloatShield::setup() {
    AutomationShield::setup();

    actuatorWrite(0);

    analogReference(EXTERNAL);

    distanceSensor.init();
    distanceSensor.setMeasurementTimingBudget(20000);
    distanceSensor.startContinuous();
}

int FloatShield::sensorRead() {
    return distanceSensor.readRangeContinuousMillimeters();
}