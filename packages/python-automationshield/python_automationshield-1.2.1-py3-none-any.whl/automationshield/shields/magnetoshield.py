import time

from math import log

from .baseshield import BaseShield


class MagnetoShield(BaseShield):
    """Class for Magnetoshield device. Inherits from BaseShield.

    The Magnetoshield device is a control experiment using magnetic levitation. The actuator is an electromagnet over which the voltage can be controlled. \
        The electromagnet attracts a permanent magnet placed below the electromagnet. The position of the permanent magnet is estimated using a Hall effect sensor.

    Interface:
        * Actuator input should be provided in percent by default.
        * Potentiometer is provided in percent by default.
        * Sensor values are provided in Gauss by default. This class provides an additional method :py:meth:`MagnetoShield.magnet_position`, which calculates the distance of the permanent magnet from the electromagnet.

    This class does not use the :py:attr:`BaseShield.zero_reference` attribute.
    """
    script = "magnetoshield"
    shield_id = "MG"

    actuator_bits = 12
    potentiometer_bits = 10
    sensor_bits = 10

    class PlotInfo(BaseShield.PlotInfo):
        sensor_unit = "mm"
        sensor_type = "Height"
        sensor_min = 12
        sensor_max = 17

    emagnet_height: int = 20
    """Height of the electromagnet above ground in mm."""
    magnet_low: int = 3
    """Top of the magnet from ground - distance from Hall element in mm when the magnet is at the bottom of the tube."""
    magnet_high: int = 8
    """Top of the magnet from ground - distance from Hall element in mm when the magnet is at the top of the tube."""

    default_p1: float = 3.233100
    """Default value for calculating the magnet position. See :py:meth:`MagnetoShield.magnet_position`."""
    default_p2: float = 0.220571
    """Default value for calculating the magnet position. See :py:meth:`MagnetoShield.magnet_position`."""

    def __init__(self, port: str | None = None) -> None:
        super().__init__(port)

        self._p1 = None
        self._p2 = None

    def convert_sensor_reading(self, sensor: int) -> float:
        """Converts the n-bit sensor reading of the Hall effect sensor to Gauss. \
            The constants in this method are for release 4 of the MagnetoShield. Conversion is done using

        .. math::
            B = \\left(2.5 - s \\cdot \\frac{3.3}{2^{10} - 1}\\right) \\cdot 800

        The sensor value :math:`s` is scaled with the ratio of the ADC reference voltage (:math:`3.3` (:math:`V`)) over the AD converter resolution (:math:`10` bits, i.e. :math:`1023`). \
            The :math:`2.5` (:math:`V`) bias for zero magnetic flux is subtracted and the result is scaled with the sensitivity of the Hall effect sensor (:math:`1.25 \\frac{mV}{G} = 800 \\frac{G}{V}`)

        :param sensor: Raw sensor value.
        :return: Sensor value in Gauss.
        """
        return (2.5 - sensor*(3.3/(2**self.potentiometer_bits - 1)))*800

    def calibrate_sensor_reading(self, sensor: int) -> int:
        """Return sensor value as is. No calibration is performed.

        :param sensor: Raw sensor value.
        :return: Raw sensor value.
        """
        return sensor

    @property
    def p1(self) -> float:
        """Return :math:`p_1` constant calculated during calibration. If not available, return :py:attr:`~MagnetoShield.default_p1`.

        :return: :math:`p_1` constant.
        """
        if self._p1:
            return self._p1

        return self.default_p1

    @p1.setter
    def p1(self, value: float):
        self._p1 = value

    @property
    def p2(self) -> float:
        """Return :math`p_2` constant calculated during calibration. If not available, return :py:attr:`~MagnetoShield.default_p2`.

        :return: :math:`p_2` constant.
        """
        if self._p2:
            return self._p2

        return self.default_p2

    @p2.setter
    def p2(self, value: float):
        self._p2 = value

    def calibrate(self):
        """Perform sensor calibration for conversion from Gauss to magnet distance from electromagnet. \
            The sensor values are read in the lowest and highest magnet position, :math:`s_{0}` and :math:`s_{1}` respectively. \
            The constants :math:`p_1` and :math:`p2` are calculated as follows:

        .. math::
            p_2 &= \\frac{ \\log{ \\left( z_{e} - z_{0} \\right) } - \\log{ \\left( z_{e} - z_{1} \\right) } } { \\log{ s_{0} } - \\log{ s_{1} } } \\\\
            p_1 &= \\frac{ z_{e} - z_{1} } { \\left( s_{1} \\right)^{p_2} }

        :math:`z_{e}`, :math:`z_{0}` and :math:`z_{1}` correspond to :py:attr:`~MagnetoShield.emagnet_height`, :py:attr:`~MagnetoShield.magnet_low` and :py:attr:`~MagnetoShield.magnet_high`, respectively.
        """
        self.write(self.RUN, 0)
        time.sleep(.5)
        self.read()
        low = 0
        for _ in range(100):
            self.write(self.RUN, 100)
            _, val = self.read()
            if val > low:
                low = val

        self.write(self.RUN, 100)
        time.sleep(.5)
        self.read()
        high = 1e3
        for _ in range(100):
            self.write(self.RUN, 100)
            _, val = self.read()
            if val < high:
                high = val

        self.write(self.STOP, 0)
        time.sleep(.5)

        self.p2 = log((self.emagnet_height - self.magnet_low) / (self.emagnet_height - self.magnet_high)) / log(low/high)
        self.p1 = (self.emagnet_height - self.magnet_high) / (high ** self.p2)

    def magnet_position(self, sensor: float) -> float:
        """Calculate magnet distance from electromagnet using

        .. math::
            y = p_1 \cdot B^{p_2}

        where :math:`B` is the magnetic flux density in Gauss. :math:`p_1` and :math:`p_2` are constants which are calculated in :py:meth:`~MagnetoShield.calibrate`.

        The distance can vary between approximately :math:`12 mm` and :math:`17 mm`.

        :param sensor: Sensor value in Gauss.
        :return: Magnet distance from electromagnet.
        """
        return self.p1 * sensor ** self.p2
