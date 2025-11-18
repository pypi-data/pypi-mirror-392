from .baseshield import BaseShield


class FloatShield(BaseShield):
    """Class for Floatshield device. Inherits from BaseShield.

    The Floatshield features a ball in a vertical tube. A fan (the actuator) is installed at the bottom, which can blow the ball up in the tube. \
        The position of the ball in the tube is measured by a distance sensor at the top of the tube, using infrared laser.

    Interface:
        * Actuator input should be provided in percent by default.
        * Potentiometer is provided in percent by default.
        * Sensor values are provided in millimetres from the bottom of the tube.
    """
    script = "floatshield"
    shield_id = "FL"

    actuator_bits = 12
    potentiometer_bits = 10
    sensor_bits = 12

    class PlotInfo(BaseShield.PlotInfo):
        sensor_unit = "mm"
        sensor_type = "Height"
        sensor_min = 0
        sensor_max = 320

    def calibrate_sensor_reading(self, sensor: int) -> int:
        """Calibrate sensor reading. 0 is taken as the ball being at the bottom of the tube.

        :param sensor: Raw sensor value.
        :return: Calibrate sensor value.
        """
        return - super().calibrate_sensor_reading(sensor)
