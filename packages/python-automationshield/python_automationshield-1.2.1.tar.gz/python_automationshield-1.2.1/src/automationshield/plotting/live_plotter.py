import ctypes
import numpy as np
import numpy.typing as npt
import time

from matplotlib import pyplot as plt
from typing import Any

from .plotter import Plotter
from ..shields import BaseShield


class LivePlotter(Plotter):
    """This class can be used to plot during an experiment. Create an instance of :py:class:`LivePlotter` and \
        pass it to your controller's :py:meth:`~automationshield.ShieldController.run` method with the ``live_plotter`` keyword argument:

        Example:

        >>> shield = AeroShield()
        >>> plotter = LivePlotter(shield=shield, hold=True)
        >>> results = MyController(shield).run(freq=200, cycles=1000, live_plotter=plotter)

        This will show a plot that will update during the experiment.

        :py:class:`LivePlotter` inherits from :py:class:`~automationshield.plotting.Plotter` and looks mostly identical. However, in order to keep the update loop as fast as possible, \
            The plot limits are set beforehand, based on the run time and bounds of the shield that is being used.

        :py:class:`LivePlotter` takes the same arguments as :py:class:`~automationshield.plotting.Plotter` in addition to some extra parameters.
    """

    default_refresh_interval = 1/60
    """Default refresh interval of the plot window in seconds."""

    def __init__(self, shield: BaseShield, show_dt: bool = True, show_ref: bool = True, show_pot: bool = False, hold: bool = False) -> None:
        """
        The `shield` parameter is not optional for a :py:class:`LivePlotter` instance. A shield instance is required to set the plot limits.

        :param hold: Whether to keep showing the plot when the experiment is finished, defaults to False. If ``True``, a call to :py:func:`matplotlib.pyplot.show` will block until the window is closed manually. \
            If used in a Jupyter environment, hold must be set to ``False``. Otherwise, the plot window will stop responding, causing the Jupyter kernel to crash.
        :type hold: bool, optional
        """
        super().__init__(shield=shield, show_dt=show_dt, show_ref=show_ref, show_pot=show_pot)

        self.hold = hold

        self.artists: list[plt.Artist] = list(self.lines.values()) + self.other_artists
        for artist in self.artists:
            artist.set_animated(True)

        self.canvas = self.fig.canvas
        self.background = None

        self.closed = False
        self.canvas.mpl_connect("close_event", self._on_close)
        self.canvas.mpl_connect("draw_event", self._on_draw)

        self.refresh_interval = self.default_refresh_interval

    def setup_figure(self, shield: BaseShield) -> tuple[plt.Figure, np.ndarray[Any, np.dtype[plt.Axes]]]:
        """Create empty figure with axes. Add labels, titles, grids, ...

        :param shield: Shield instance.
        :type shield: ~automationshield.shields.BaseShield
        :return: Figure and (array of) axes.
        :rtype: tuple[plt.Figure, np.ndarray[Any, np.dtype[plt.Axes]]]
        """
        fig, ax = super().setup_figure(shield)

        sensor_border = .05 * (shield.PlotInfo.sensor_max - shield.PlotInfo.sensor_min)
        sensor_minmax = (shield.PlotInfo.sensor_min - sensor_border, shield.PlotInfo.sensor_max + sensor_border)
        ax[0].set_ylim(*sensor_minmax)

        percent_minmax = (-5, 105)
        ax[1].set_ylim(*percent_minmax)

        return fig, ax

    def setup_artists(self, shield: BaseShield) -> tuple[dict[str, plt.Line2D], list[plt.Artist]]:
        """Add lines to plot data for later. Add legends and text. Anything that should be updated/moved or redrawn each loop should be defined here. Anything that should be updated should be added to \
            a dictionary with a key of your choice. Artists that should only be moved/redrawn should be added to a list.

        :param shield: Shield instance.
        :type shield: ~automationshield.shields.BaseShield
        :return: dictionary of artists that should be updated and list of artists that only need to be redrawn.
        :rtype: tuple[dict[str, plt.Line2D], list[plt.Artist]]
        """
        lines, other_artists =  super().setup_artists(shield)

        text = self.fig.text(.13, .9, "0")
        lines["plot_freq"] = text

        return lines, other_artists

    def set_plot_limits_time(self, max_time: int | float, freq: int | float):
        """Set the x-limits on the input and output plots and the x- and y-limits on the dt plot, if shown. \
            Set the refresh rate of the live plotter: minimum of 60Hz and experiment frequency.

        :param max_time: Experiment duration.
        :type max_time: int | float
        :param freq: Experiment frequency.
        :type freq: int | float
        """
        self.refresh_interval = max(1/freq, self.default_refresh_interval)

        self.ax[0].set_xlim(-.05*max_time, 1.1*max_time)
        self.ax[1].set_xlim(-.05*max_time, 1.1*max_time)

        if self.show_dt:
            self.ax[2].set_xlim(-.05*max_time, 1.1*max_time)
            self.ax[2].set_ylim(.95*1000/freq, 2000/freq)

    def close(self):
        """Close the plot window. Used when receiving a KeyboardInterrupt."""

        plt.close(self.fig)
        plt.pause(1)

    def _on_close(self, *args):
        """Callback to register with 'close_event'."""
        self.closed = True

    def _on_draw(self, event):
        """Callback to register with 'draw_event'."""
        if event is not None:
            if event.canvas != self.canvas:
                raise RuntimeError
        self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_animated()

    def _draw_animated(self):
        for artist in self.artists:
            self.fig.draw_artist(artist)

    def _update_figure(self):
        self.canvas.restore_region(self.background)

        self._draw_animated()
        self.canvas.blit(self.fig.bbox)
        self.canvas.flush_events()

    def plot(self, data: npt.NDArray[np.float64], cntr: ctypes.c_ulong):
        """Show live plot and update with experiment data as it is received.

        :param data: Experiment data array.
        :type data: npt.NDArray[np.float64]
        :param cntr: Cycle counter of the experiment.
        :type cntr: ctypes.c_ulong
        """
        self._on_draw(None)
        plt.pause(1)

        t0 = time.perf_counter()
        t1 = t0

        while (not self.closed) and (cntr.value < len(data)):
            while (t1 - t0) < self.refresh_interval:
                t1 = time.perf_counter()

            line_data = self.calculate_plot_lines(data[:cntr.value])
            line_data["plot_freq"] = (f"{round(1/(t1 - t0))}Hz",)

            self._plot(line_data)
            self._update_figure()

            t0 = t1

        if not self.closed:
            if self.hold:
                # hold plot until closed manually
                plt.show()

            else:
                # hold plot for a second before exit
                plt.pause(1)
                plt.close(self.fig)
