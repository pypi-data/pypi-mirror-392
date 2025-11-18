import numpy as np
import numpy.typing as npt

from matplotlib import pyplot as plt
from typing import Optional, Any

from ..shields import BaseShield


class Plotter:
    """Create matplotlib figure. When an instance is created, an empty figure is built with empty :py:class:`plt.Line2D` elements. \
        When calling :py:meth:`Plotter.plot` with the results of an experiment (output of :py:meth:`automationshield.ShieldController.run`), the data is rendered. \
        The :py:class:`~matplotlib.figure.Figure` and :py:class:`~matplotlib.axes.Axes` instances are returned by :py:meth:`Plotter.plot`, allowing the user to modify the plots before showing them. \
        :py:func:`matplotlib.pyplot.show` must be called in the main script for the figure to be shown.

    The figure created by :py:class:`Plotter` contains two or three plots in rows:

    * An output plot. This plot shows the sensor values and, optionally, the reference values.
    * An input plot. This plot show the actuator values and, optionally, the potentiometer values.
    * An optional time step plot. This plot show the step size for each time step in the experiment.

    Example:

    >>> from matplotlib import pyplot as plt
    >>>
    >>> shield = AeroShield()
    >>> results = MyController(shield).run(freq=200, cycles=1000)
    >>> fig, ax = Plotter(shield=shield).plot(results)
    >>> plt.show()
    """

    _update_methods = {plt.Line2D: "set_data", plt.Text: "set_text"}

    def __init__(
        self,
        shield: Optional[BaseShield] = None,
        show_dt: bool = True,
        show_ref: bool = True,
        show_pot: bool = False,
    ) -> None:
        """
        :param shield: shield instance being used, defaults to None. If provided, the :py:class:`~automationshield.shields.BaseShield.PlotInfo` class attributes are used to add \
            units to the output plot.
        :type shield: ~automationshield.shields.BaseShield, optional
        :param show_dt: Whether to show a third plot with the time steps, defaults to True.
        :type show_dt: bool
        :param show_ref: Whether to plot the reference as given to the :py:meth:`~automationshield.ShieldController.run` method, defaults to True.
        :type show_ref: bool
        :param show_pot: Whether to plot the potentiometer value, defaults to False.
        :type show_pot: bool
        """
        self.shield = shield

        self.show_dt = show_dt
        self.show_ref = show_ref
        self.show_pot = show_pot

        fig, ax = self.setup_figure(shield)
        self.fig: plt.Figure = fig
        self.ax: np.ndarray[Any, np.dtype[plt.Axes]] = ax

        lines, other_artists = self.setup_artists(shield)
        self.lines: dict[str, plt.Artist] = lines
        self.other_artists: list[plt.Artist] = other_artists

    def setup_figure(
        self, shield: Optional[BaseShield] = None
    ) -> tuple[plt.Figure, list[plt.Axes]]:
        """Create an empty figure. Creates the plots, defines the layout and sets the titles and axis labels.

        :param shield: Shield instance whose data will be plotted, defaults to None. If provided, units are set on the output plot.
        :type shield: ~automationshield.shields.BaseShield, optional
        :return: Figure and list of axes.
        :rtype: tuple[matplotlib.figure.Figure, list[matplotlib.axes.Axes]]
        """
        fig, ax = plt.subplots(
            ncols=1, nrows=2 + (1 if self.show_dt else 0), sharex=True
        )
        self.fig = fig
        self.ax = ax

        # output
        sensor_unit_string = rf" ({shield.PlotInfo.sensor_unit})" if shield else ""
        self.ax[0].set_ylabel(
            rf"{shield.PlotInfo.sensor_type if shield else 'Value'}{sensor_unit_string}"
        )
        self.ax[0].set_title("Output")
        self.ax[0].grid(True)

        # input
        self.ax[1].set_title("Input")
        self.ax[1].set_ylabel("Value (%)")
        self.ax[1].grid(True)

        # dt
        if self.show_dt:
            self.ax[2].set_title("Time steps")
            self.ax[2].set_ylabel("Step size (ms)")
            self.ax[2].grid(True)

        # set xlabel on the bottom axis
        self.ax[-1].set_xlabel("Time (s)")

        return fig, ax

    def setup_artists(
        self, shield: Optional[BaseShield] = None
    ) -> tuple[dict[str, plt.Line2D], list[plt.Artist]]:
        """Add artists to the figure. Create :py:class:`matplotlib.lines.Line2D` instances for each plot line and add legends were needed. \
            All lines are added to a dictionary, any other artists (legends and other stuff) are added to a list. Both are returned.

        :param shield: Shield instance whose data will be plotted, defaults to None
        :type shield: ~automationshield.shields.BaseShield, optional
        :return: dictionary of line elements, list of other artists.
        :rtype: tuple[dict[str, plt.Line2D], list[plt.Artist]]
        """
        sensor_line = self.ax[0].plot(0, 0, label="sensor")[0]
        actuator_line = self.ax[1].plot(0, 0, label="actuator")[0]

        lines = {"sensor": sensor_line, "actuator": actuator_line}
        other_artists = list()

        if self.show_ref:
            ref_line = self.ax[0].plot(
                0, 0, label="reference", linestyle="--", color="k", zorder=3
            )[0]
            lines["ref"] = ref_line

            out_legend = self.ax[0].legend()
            other_artists.append(out_legend)

        if self.show_pot:
            pot_line = self.ax[1].plot(0, 0, label="potentiometer")[0]
            lines["pot"] = pot_line

            in_legend = self.ax[1].legend()
            other_artists.append(in_legend)

        if self.show_dt:
            dt_line = self.ax[2].plot(0, 0, label="dt")[0]
            lines["dt"] = dt_line

        # self.lines: { sensor, ref (if shown), actuator, pot (if shown), dt (if shown) }
        # self.other_artists: [ input_legend (if ref), output_legend (if pot) ]

        return lines, other_artists

    def plot(self, data: npt.NDArray[np.float64]) -> tuple[plt.Figure, list[plt.Axes]]:
        """Set the data on the plots. Rescales the plots with the data added.

        :param data: Results from an :py:class:`automationshield.ShieldController` experiment.
        :type data: npt.NDArray[np.float\_]
        :return: Figure and axes of the plot.
        :rtype: tuple[matplotlib.figure.Figure, list[matplotlib.axes.Axes]]
        """
        line_data = self.calculate_plot_lines(data)
        self._plot(line_data)

        for i in range(len(self.ax)):
            self.ax[i].relim()
            self.ax[i].autoscale_view()

        return self.fig, self.ax

    def calculate_plot_lines(
        self, data: npt.NDArray[np.float64]
    ) -> dict[str, tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]]:
        """Calculate the values that should be plotted.

        :param data: Results array received from :py:class:`~automationshield.ShieldController`.
        :type data: npt.NDArray[np.float64]
        :return: Dictionary with tuples containing arrays for :math:`x` and :math:`y` data. The keys in the dictionary must match the ones you assigned in \
            :py:meth:`~Plotter.setup_figure`. Any additional keys in this dictionary are ignored.
        :rtype: dict[str, tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]]
        """
        return {
            "sensor": (data[:, 0], data[:, 3]),
            "ref": (data[:, 0], data[:, 1]),
            "actuator": (data[:, 0], data[:, 4]),
            "pot": (data[:, 0], data[:, 2]),
            "dt": (data[:, 0], 1000 * np.gradient(data[:, 0]))
            if len(data) > 1
            else (0, 0),
        }

    def _plot(self, data):
        """Set data on lines."""
        for key, line in self.lines.items():
            getattr(line, self._update_methods[type(line)])(*data[key])
