import ctypes
import numpy as np
import numpy.typing as npt
import time

from multiprocess import Process, RawValue
from multiprocess.shared_memory import SharedMemory
from typing import Callable, Optional, Sequence

from .reference import Reference, ConstantReference, PresetReference

from ..exception import AutomationShieldException
from ..shields.baseshield import BaseShield
from ..plotting import LivePlotter


class ShieldController:
    """The ShieldController class implements a controller interface for the various shield classes. This class should be subclassed to create custom controllers.\
        In a subclass, overwrite the :py:meth:`ShieldController.controller` method to implement your controller. Optionally, overwrite the :py:meth:`ShieldController.variables` method \
        to initialise instance variables that should persist beyond the scope of the controller method.

    Example:

    >>> class MyController(ShieldController):
    ...     def controller(self, t: float, dt: float, ref: float, pot: float, sensor: float) -> float:
    ...         return ref
    """
    def __init__(self, shield:BaseShield) -> None:
        """
        :param shield: shield class instance.
        :type shield: ~automationshield.shields.BaseShield
        """
        self.shield = shield

        # t1 - tstart, ref, pot, sensor, actuator
        self.n_base_vars = 5
        # store additional variables to save when running an experiment
        self.tracked_variables: dict[str, int] = dict()

        # initiate controller variables
        self.variables()

        self.cntr = 0

    def variables(self) -> None:
        """Define variables to be used by the controller or saved during the experiment."""
        pass

    def add_tracked_variable(self, name: str, size: int=1) -> dict[str, int]:
        """Add a variable to the list of variables whose value should be tracked during the experiment and returned afterwards.
        Variables should be instance variables of the class, otherwise they won't be accessible!

        :param name: Name of the variable, without 'self.'
        :type name: str
        :param size: Size of the variable, e.g. 3 for a three-dimensional position vector. Defaults to 1, i.e. single values.
        :type size: int
        :return: A copy of the current map of tracked variables and their respective size.
        :rtype: dict[str, int]
        """
        self.tracked_variables[name] = size

        return self.tracked_variables.copy()

    def reference_callback(self, cntr: int, t: float, pot: float) -> int | float:
        """Calculate reference value. If used, this method is called every cycle to calculate a new reference. After implementing this method on a subclass of :py:class:`ShieldController`, \
            you can use it during an experiment as follows:

        >>> my_controller = MyController(shield=shield)
        >>> my_controller.run(freq=freq, cycles=cycles, ref=my_controller.reference_callback)

        This implementation allows for multiple callback functions to be defined on the controller class or outside of it. It is not mandatory to override this specific method.

        :param cntr: Number of the current cycle.
        :type cntr: int
        :param t: Time since start of experiment in seconds.
        :type t: float
        :param pot: Potentiometer value in percent.
        :type pot: float
        :return: Reference value.
        :rtype: float
        """

        return 0

    def controller(self, t: float, dt: float, ref: int | float, pot: float, sensor: float) -> int | float:
        """Implement the controller here. You can subclass ShieldController and overwrite the controller.

        :param t: Time since start of run in seconds.
        :type t: float
        :param dt: Length of current time step in seconds.
        :type dt: float
        :param ref: Reference value for the current step.
        :type ref: float
        :param pot: Potentiometer value in percent.
        :type pot: float
        :param sensor: Sensor value, calibrated if applicable.
        :type sensor: float
        :return: input value for actuator. the motor value will be saturated afterwards.
        :rtype: float
        """

        return 0  # actuator value

    def run(self, freq: int | float, cycles: Optional[int]=None, ref: Optional[int | float | Sequence[int | float] | Callable[[int, float, float], int | float] | Reference]=None, live_plotter: Optional[LivePlotter]=None) -> npt.NDArray[np.float64]:
        """Run the controller on a shield device.

        You can stop the experiment at any time by pressing Ctrl-C. The experiment will exit gracefully and return the gathered data up to the point of the interrupt.

        :param freq: Desired frequency of the loop.
        :type freq: int
        :param cycles: Number of cycles to run the experiment. If ref is an array, cycles is optional and the length of the reference is used as the number of cycles. Defaults to None.
        :type cycles: int
        :param ref: The reference to follow. It can be an array, a single value (i.e. constant reference) or a function or class to be called in each cycle. \
            If it's an array, it should have a length equal to freq * cycles. See the documentation for :py:meth:`ShieldController.reference_callback` on how to define a callback function. \
            A class should expose a :py:meth:`__call__` method, whose signature must match that of a callback function, like in ~automationshield.controller.Reference. \
            The class doesn't need to inherit from ~automationshield.controller.reference. Defaults to None, in which case the reference is set to 0.
        :type ref: float | int | Sequence[float | int] | Callable[[int, float, float], float], Type[~automationshield.controller.Reference], optional
        :param live_plotter: Optional :py:class:`~automationshield.plotting.LivePlotter` instance to use for displaying a live plot, defaults to None.
        :type live_plotter: ~automationshield.plotting.LivePlotter, optional
        :return: Experiment data. The columns of the array are time, reference, potentiometer, sensor, actuator, and any additional variables in the order they were added.
        :rtype: npt.NDArray[np.float64]
        """

        # if cycles is given, use that. Otherwise, check if ref has a length.
        if cycles is None:
            if hasattr(ref, "__len__"):
                cycles = len(ref)
            else:
                raise AutomationShieldException("Cycles must be given or ref should be sequence")

        if callable(ref):
            pass
        elif ref is None:
            ref = ConstantReference(0)
        elif isinstance(ref, (int, float)):
            ref = ConstantReference(ref)
        elif hasattr(ref, "__getitem__"):
            ref = PresetReference(ref)
        else:
            raise TypeError(f"Reference of type '{type(ref)}' is not suitable.")

        shape = (cycles, self.n_base_vars + sum(self.tracked_variables.values()))

        shm = SharedMemory(create=True, size=int(np.dtype(np.float64).itemsize * np.prod(shape)))
        hist = np.ndarray(shape=shape, dtype=np.float64, buffer=shm.buf)
        hist *= 0
        hist[:, 0] = np.arange(0, cycles/freq, 1/freq)

        cntr: ctypes.c_ulong = RawValue(ctypes.c_uint32)

        process = Process(target=self._run, args=(freq, cycles, ref, cntr, shm.name, hist.shape, hist.dtype))
        process.start()

        try:
            if live_plotter:
                live_plotter.set_plot_limits_time(cycles / freq, freq)
                live_plotter.plot(hist, cntr)

            # this cannot go in a finally block, since this is the blocking call if there is no live_plotter
            process.join()

        except KeyboardInterrupt:
            print("Received Ctrl-C, stopping experiment...")

            if live_plotter:
                live_plotter.close()

            process.join()

        hist = hist.copy()
        shm.close()
        shm.unlink()

        return hist[:cntr.value]

    def _run(self, freq: int | float, cycles: int, ref: Reference, cntr: ctypes.c_ulong, memname: str, shape: tuple[int, int], dtype: np.dtype):
        shm = SharedMemory(name=memname)
        hist = np.ndarray(shape=shape, dtype=dtype, buffer=shm.buf)

        period = 1/freq

        with self.shield as shield:
            # need an initial write so there's something to read when we get there.
            shield.write(shield.RUN, 0)

            tstart = time.perf_counter()
            t0 = t1 = tstart

            done = False
            while not done:
                try:
                    pot, sensor = shield.read()

                    dt = t1 - t0
                    t0 = t1
                    ti = t1 - tstart

                    ref_i = ref(cntr.value, ti, pot)

                    raw_actuator = self.controller(ti, dt, ref_i, pot, sensor)
                    actuator = shield.write(shield.RUN, raw_actuator)

                    self._update_hist(hist, cntr, ti, ref_i, pot, sensor, actuator)

                    print(f"\r{cntr.value}", end="")

                    cntr.value += 1
                    if cntr.value == cycles:
                        done = True

                    while (t1 - t0) < period:
                        t1 = time.perf_counter()

                except KeyboardInterrupt:
                    done = True

            print()
            shm.close()

    def _update_hist(self, hist: npt.NDArray[np.float64], cntr: int, t: float, ref: int | float, pot:float, sensor: float, actuator: int | float):
        """Update hist array with variables of the current iteration (cntr). If variables were added to `extra_hist_vars`, add them to the hist as well."""
        hist[cntr, 0:self.n_base_vars] = t, ref, pot, sensor, actuator
        total_vars = self.n_base_vars

        for name, size in self.tracked_variables.items():
            hist[cntr, total_vars:total_vars+size] = getattr(self, name)

            total_vars += size
