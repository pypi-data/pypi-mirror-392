import numpy as np
import numpy.typing as npt
import time

from importlib.util import find_spec
from numpy.linalg import inv

from .baseshield import BaseDummyShield

# check if scipy package is installed
_SCIPY_INSTALLED = (find_spec("scipy") is not None)

if _SCIPY_INSTALLED:
    # This stops the interpreter from crashing on Ctrl-C (due to Scipy)
    import os
    os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

    from scipy.linalg import expm


class StateSpaceShield(BaseDummyShield):
    """This class can be used to simulate a general state-space model and control it using a :py:class:`automationshield.ShieldController` instance. \
        The state-space system must be a SISO system.

    Create a class that inherits from :py:class:`~automationshield.StateSpaceShield` and override the following methods:

    * :py:meth:`~automationshield.StateSpaceShield.calculate_a`, :py:meth:`~automationshield.StateSpaceShield.calculate_b`, \
        :py:meth:`~automationshield.StateSpaceShield.calculate_c`, :py:meth:`~automationshield.StateSpaceShield.calculate_d`: \
        These methods should return state-space matrices A, B, C and D, respectively. They take the current state vector as input, \
        which makes it possible to update the matrices depending on the current state of the system. This way, a non-linear system can be simulated accurately.
    * Optional: :py:meth:`~automationshield.StateSpaceShield.get_equilibrium_point`: Override this method when you're including non-linear behaviour. \
        This method should return the equilibrium state and required input to maintain this state.
    """
    EXACT = "exact"
    """Set discretisation to this constant for exact discretisation."""
    EULER = "euler"
    """Set discretisation to this constant for Euler discretisation."""
    TUSTIN = "tustin"
    """Set discretisation to this constant for Tustin discretisation."""

    def __init__(self, n_states: int, discretisation: str=None):
        """
        :param n_states: Number of states of the system.
        :param discretisation: Type of discretisation to use. Must be one of :py:const:`~automationshield.StateSpaceShield.EXACT`, \
            :py:const:`~automationshield.StateSpaceShield.EULER` or :py:const:`~automationshield.StateSpaceShield.TUSTIN`; defaults to :py:const:`~automationshield.StateSpaceShield.TUSTIN`.
        """
        super().__init__()

        self._discretisation = None
        if discretisation is None:
            self.discretisation = self.TUSTIN
        else:
            self.discretisation = discretisation

        self._identity = np.eye(n_states)

        self.x: npt.NDArray[np.float64] = np.zeros((n_states, 1))
        """State vector of shape (n_states, 1)."""
        self.u: npt.NDArray[np.float64] = np.zeros((1, 1))
        """Input vector of shape (1, 1)."""

        self.t0: float = time.perf_counter()
        """Time of last step. Used to calculate real time step sizes."""

    @property
    def discretisation(self) -> str:
        """Get or set discretisation method used. Must be one of :py:const:`~automationshield.StateSpaceShield.EXACT`, \
            :py:const:`~automationshield.StateSpaceShield.EULER` or :py:const:`~automationshield.StateSpaceShield.TUSTIN`. \
            In order to use :py:const:`~automationshield.StateSpaceShield.EXACT`, Scipy must be installed.

        :raises RunTimeError: When trying to set :py:const:`~automationshield.StateSpaceShield.EXACT` without Scipy installed.
        """
        return self._discretisation

    @discretisation.setter
    def discretisation(self, value: str):
        if value not in [self.EXACT, self.EULER, self.TUSTIN]:
            raise ValueError("Invalid discretisation method provided.")

        if value == self.EXACT and (not _SCIPY_INSTALLED):
            raise RuntimeError("Scipy must be installed to use exact discretisation but module not found.")

        self._discretisation = value

    def calculate_a(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate A matrix. This method must be implemented on a subclass.

        :param state: Current state of the system.
        :raises NotImplementedError: When method is not overridden on the subclass.
        :return: Numpy array. Must be a 2D array of shape (n_states, n_states).
        """
        raise NotImplementedError

    def calculate_b(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate B matrix. This method must be implemented on a subclass.

        :param state: Current state of the system.
        :raises NotImplementedError: When method is not overridden on the subclass.
        :return: Numpy array. Must be a 2D array of shape (n_states, 1).
        """
        raise NotImplementedError

    def calculate_c(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate C matrix. This method must be implemented on a subclass.

        :param state: Current state of the system.
        :raises NotImplementedError: When method is not overridden on the subclass.
        :return: Numpy array. Must be a 2D array of shape (1, n_states).
        """
        raise NotImplementedError

    def calculate_d(self, state: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate A matrix. This method must be implemented on a subclass.

        :param state: Current state of the system.
        :raises NotImplementedError: When method is not overridden on the subclass.
        :return: Numpy array. Must be a 2D array of shape (1, 1).
        """
        raise NotImplementedError

    def get_equilibrium_point(self, state: npt.NDArray[np.float64]) -> tuple[npt.NDArray[np.float64], float]:
        """Return equilibrium input and state for the current state. Used for linearising at the current state. \
            By default, the equilibrium state and input are returned as (0, 0), in which case this method has no effect.

        :param state: Current state.
        :return: Equilibrium state and input, respectively.
        """
        return 0, 0

    def discretise(self, a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], dt: float) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Calculate discrete-time matrices :math:`A_D` and :math:`B_D` from their continuous-time counterpart obtained from \
            :py:meth:`~StateSpaceShield.calculate_a` and :py:meth:`~StateSpaceShield.calculate_b`, respectively, using the discretisation method set.

        :param a: Matrix :math:`A`.
        :param b: Matrix :math:`B`.
        :param dt: Time step.
        :return: Discrete-time matrices :math:`A_D` and :math:`B_D`.
        """
        match self.discretisation:
            case self.TUSTIN:
                return self.discrete_tustin(a, b, dt)
            case self.EXACT:
                return self.discrete_exact(a, b, dt)
            case self.EULER:
                return self.discrete_euler(a, b, dt)

    def discrete_exact(self, a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], dt: float) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Calculate discrete-time matrices :math:`A_D` and :math:`B_D` from their continuous-time counterpart obtained from \
            :py:meth:`~StateSpaceShield.calculate_a` and :py:meth:`~StateSpaceShield.calculate_b`, respectively, using the exact discretisation method.

        .. math::
            A_D &= e^{A \\cdot dt} \\\\
            B_D &= A^{-1} \\cdot \\left(A_D - I \\right) \\cdot B

        :param a: Matrix :math:`A`.
        :param b: Matrix :math:`B`.
        :param dt: Time step.
        :return: Discrete-time matrices :math:`A_D` and :math:`B_D`.
        """
        a_d = expm(a*dt)
        return a_d, self._calculate_b_d(a, b, a_d)

    def discrete_tustin(self, a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], dt: float) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Calculate discrete-time matrices :math:`A_D` and :math:`B_D` from their continuous-time counterpart obtained from \
            :py:meth:`~StateSpaceShield.calculate_a` and :py:meth:`~StateSpaceShield.calculate_b`, respectively, using the Tustin discretisation method.

        .. math::
            A_D &= \\left(I + \\frac{A \\cdot dt}{2} \\right) \\cdot \\left( I - \\frac{A \\cdot dt}{2} \\right)^{-1} \\\\
            B_D &= A^{-1} \\cdot \\left(A_D - I \\right) \\cdot B

        :param a: Matrix :math:`A`.
        :param b: Matrix :math:`B`.
        :param dt: Time step.
        :return: Discrete-time matrices :math:`A_D` and :math:`B_D`.
        """
        a_d = (self._identity + .5*a*dt) @ inv(self._identity - .5*a*dt)
        return a_d, self._calculate_b_d(a, b, a_d)

    def discrete_euler(self, a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], dt: float) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Calculate discrete-time matrices :math:`A_D` and :math:`B_D` from their continuous-time counterpart obtained from \
            :py:meth:`~StateSpaceShield.calculate_a` and :py:meth:`~StateSpaceShield.calculate_b`, respectively, using the forward Euler discretisation method.

        .. math::
            A_D &= I + A \\cdot dt \\\\
            B_D &= B \\cdot dt

        :param a: Matrix :math:`A`.
        :param b: Matrix :math:`B`.
        :param dt: Time step.
        :return: Discrete-time matrices :math:`A_D` and :math:`B_D`.
        """
        a_d = self._identity + a*dt
        return a_d, b*dt

    def _calculate_b_d(self, a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], a_d: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Calculate discrete-time matrix :math:`B_D`.

        .. math::
            B_D &= A^{-1} \\cdot \\left(A_D - I \\right) \\cdot B

        :param a: Matrix :math:`A`.
        :param b: Matrix :math:`B`.
        :param a_d: Discrete-time matrix :math:`A_D`.
        :return: Discrete-time matrix :math:`B_D`.
        """
        return inv(a) @ (a_d - self._identity) @ b

    def condition_input(self, input: float) -> float:
        """Condition the input before applying it to the system. Override this method in your subclass to customise how the input is conditioned. \
            By default, the input is returned unchanged.

        :param input: Input value.
        :return: Conditioned input value.
        """
        return input

    def read(self) -> tuple[int, float]:
        """The :py:meth:`automationshield.shields.BaseShield.read` method is overridden to replicate the behaviour from a physical shield. \
            This method calculates the output of the system and returns it. The output corresponding to the potentiometer value \
            of a physical shield is set to 0.

        .. math::
            y = C \\cdot x + D \\cdot u

        :return: Output of the system.
        """
        sensor = self.calculate_c(self.x) @ self.x + self.calculate_d(self.x) @ self.u

        return 0, sensor[0, 0]

    def write(self, flag: int, input: float) -> float:
        """The :py:meth:`automationshield.shields.BaseShield.read` method is overridden to replicate the behaviour from a physical shield. \
            This method does the following:

        * Update the time step;
        * Calculate the equilibrium point input :math:`u_e` and state :math:`x_e`;
        * Calculate the discrete-time system and input matrices :math:`A_D` and :math:`B_D`;
        * Update the state vector using the equation below.

        .. math::
            x_{k+1} = x_e + A_D \\cdot \\left( x_k - x_{e,k} \\right) + B_D \\cdot \\left( u_k - u_{e,k} \\right)

        Finally, the input is update with the conditioned input value. Conditioning is performed through :py:meth:`StateSpaceShield.condition_input`.

        :param flag: Run flag for a physical shield. Ignored.
        :param input: Input value.
        :return: Conditioned input value.
        """
        t1 = time.perf_counter()
        dt = t1 - self.t0
        self.t0 = t1

        xe, ue = self.get_equilibrium_point(self.x)

        a = self.calculate_a(self.x)
        b = self.calculate_b(self.x)
        a_d, b_d = self.discretise(a, b, dt)

        self.x = xe + a_d @ (self.x - xe) + b_d @ (self.u - ue)

        self.u[0, 0] = self.condition_input(input)

        return self.u[0, 0]
