import numpy as np
import numpy.typing as npt

from .baseshield import BaseShield
from .statespaceshield import StateSpaceShield


class AeroShield(BaseShield):
    """Class for Aeroshield device. Inherits from BaseShield.

    The Aeroshield is a pendulum control experiment. The actuator is a propeller at the end of the pendulum. The position of the pendulum is measured by an angle sensor.

    Interface:
        * Actuator input should be provided in percent by default.
        * Potentiometer is provided in percent by default.
        * Sensor values are converted to degrees by default.
    """
    script = "aeroshield"
    shield_id = "AE"

    actuator_bits: int = 8
    potentiometer_bits: int = 10
    sensor_bits: int = 12

    class PlotInfo(BaseShield.PlotInfo):
        sensor_unit = r"$\degree$"
        sensor_type = "Angle"
        sensor_min = 0
        sensor_max = 180

    def convert_sensor_reading(self, raw: int) -> float:
        """Convert raw angle to degrees.

        .. math::
            \\alpha_{deg} = \\alpha_{raw} \\cdot \\frac{360}{2^{n}}

        where :math:`n` equals :py:const:`AeroShield.sensor_bits`.

        :param raw: 12-bit value of angle sensor.
        :return: Angle value scaled to degrees.
        """
        return raw * 360 / (2**self.sensor_bits)

    def calibrate_sensor_reading(self, raw_angle: int) -> int:
        """Calibrate the sensor reading with the zero reference. Subtract zero reference from the measurement \
            and ensure result is between :math:`-90 \\degree` and :math:`270 \\degree` and not off by a multiple of :math:`360 \\degree`.

        :param raw_angle: Raw 12-bit angle value.
        :return: Calibrated angle.
        """

        angle = raw_angle - self.zero_reference
        # make sure angle is positive in testing range
        if angle < -1024:
            angle += 4096

        return angle


class AeroShieldMimic(StateSpaceShield, AeroShield):
    """State-space model of the AeroShield. Simulates the behaviour of an Aeroshield device through its range of angles. \
        The system is identified through the following set of differential equations

    .. math::
        \\ddot{\\theta} &= \\frac{k \\cdot F}{m \\cdot r} - \\frac{g}{r} \\sin{\\theta} - \\frac{b \\cdot \\dot{\\theta}}{m \\cdot r} \\\\
        \\dot{\\theta} &= \\dot{\\theta} \\\\
        \\dot{F}_k &= d \\cdot \\left(u_{k-1} - F_{k-1}\\right)

    Here, :math:`k \\cdot F` is the fan thrust, with :math:`k` a constant and :math:`F` an approximation of the fan speed. The fan speed is modelled as a delay \
        between the requested input and the effective fan speed. The value of :math:`d` was obtained through frequency analysis.

    The system of equations is converted to a state-space system to work with the :py:class:`~automationshield.StateSpaceShield`. Inputs and outputs are identical to the physical shield, the state vector is

    .. math::
        x = \\begin{bmatrix} \\dot{\\theta} \\\\ \\theta \\\\ F \\end{bmatrix}

    For the matrices, refer to the methods in which they are defined.

    The state-space system is linearised each control loop at its current position, such that the behaviour more closely resembles real life. For this, a second-degree polynomial \
        that models the required input to hold the pendulum at a given angle was obtained experimentally. This polynomial is given in :py:attr:`AeroShieldMimic.equilibrium`.
    """

    b = 0.0007
    """Friction coefficient."""
    m = 0.006
    """Pendulum mass."""
    g = 9.81
    """Gravitational acceleration."""
    r = 0.125
    """Pendulum length."""
    k = 0.00165
    """Fan thrust multiplier."""
    d = 12
    """Fan speed delay constant."""

    equilibrium: np.poly1d = np.poly1d([11.946862470797765, 29.288529089840527, 1.0401199115394326])
    """Second-degree polynomial returning the required steady-state input as a function of the sine of the pendulum angle. \
        The figure shows the input required to keep the pendulum at a given angle, i.e. compensate for its own weight.

    .. plot::

        >>> plt.style.use('dark_background')
        >>> theta = np.linspace(0, 180, 500)
        >>> equilibrium = np.poly1d([11.946862470797765, 29.288529089840527, 1.0401199115394326])
        >>> plt.plot(theta, equilibrium(np.sin(np.radians(theta))))
        >>> plt.grid(True)
        >>> plt.xticks([0, 30, 60, 90, 120, 150, 180])
        >>> plt.title("Required input for force equilibrium as function of pendulum angle")
        >>> plt.xlabel(r"Pendulum Angle ($\\degree$)")
        >>> plt.ylabel("Equilibrium Input (%)")
    """

    def __init__(self, discretisation: str=None):
        """
        :param discretisation: Discretisation method to use, defaults to the default of :py:class:`~automationshield.StateSpaceShield`.
        """
        super().__init__(n_states=3, discretisation=discretisation)

    def calculate_a(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate matrix A:

        .. math::
            A = \\begin{bmatrix}
            -\\frac{b}{m \\cdot r} & - \\frac{g}{r} \\cos{\\theta} & \\frac{k}{m \\cdot r} \\\\
            1 & 0 & 0 \\\\
            0 & 0 & -12 \\\\
            \\end{bmatrix}

        where :math:`\\theta` is a state variable.
        """
        return np.array(
            [[-self.b/(self.m*self.r), -self.g/self.r * np.cos(state[1, 0]), self.k/(self.m*self.r)],
             [1                      , 0                                   , 0                     ],
             [0                      , 0                                   , -self.d               ]]
        )

    def calculate_b(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate matrix B:

        .. math::
            B = \\begin{bmatrix} 0 \\\\ 0 \\\\ 12 \\end{bmatrix}
        """
        return np.array(
            [[0],
             [0],
             [self.d]]
        )

    def calculate_c(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate matrix C:

        .. math::
            C = \\begin{bmatrix} 0 & 1 & 0 \\end{bmatrix}
        """
        return np.array([[0, 1, 0]])

    def calculate_d(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate matrix D:

        .. math::
            D = \\begin{bmatrix} 0 \\end{bmatrix}
        """
        return np.array([[0]])

    def get_equilibrium_point(self, state: npt.NDArray[np.float64]) -> tuple[npt.NDArray[np.float64], float]:
        """Calculate equilibrium input and state at the current pendulum angle :math:`\\theta`. The equilibrium state is defined as

        .. math::
            x_{e, k} = \\begin{bmatrix} \\dot{\\theta}_{e, k} \\\\ \\theta_{e, k} \\\\ F_{e, k} \\end{bmatrix} = \\begin{bmatrix} 0 \\\\ \\theta_k \\\\ u_{e,k} \\end{bmatrix}
        """
        ue = self.equilibrium(np.sin(state[1, 0]))
        xe = np.array([
            [0],
            self.x[1],
            [ue]
        ])

        return xe, ue

    def read(self) -> tuple[int, float]:
        """Convert the output to degrees. This method calls :py:meth:`automationshield.StateSpaceShield.read` and converts the output to degrees before returning it.

        :return: Output in degrees.
        """
        pot, out = super().read()
        return pot, np.degrees(out)

    def condition_input(self, input):
        return self.saturate_percent(input)
