# #########################################################################
# Copyright (c) 2020, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2020. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

import numpy as np
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib.pyplot import subplot2grid#, silent_list

from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, WavePyInteractiveWidget, pixels_to_inches

from warnings import filterwarnings
filterwarnings("ignore")

class PlotProfile(WavePyWidget):
    def _allows_saving(self): return False

    def get_plot_tab_name(self):
        return self.__title

    def build_widget(self, **kwargs):
        try: str4title = kwargs["str4title"]
        except: str4title = "Profile Plot"
        try: self.__title = kwargs["title"]
        except: self.__title = str4title

        xmatrix = kwargs["xmatrix"]
        ymatrix = kwargs["ymatrix"]
        zmatrix = kwargs["zmatrix"]
        try:    xlabel = kwargs["xlabel"]
        except: xlabel = "x"
        try:    ylabel = kwargs["ylabel"]
        except: ylabel = "y"
        try:    zlabel = kwargs["zlabel"]
        except: zlabel = "z"
        try:    xo = kwargs["xo"]
        except: xo = None
        try:    yo = kwargs["yo"]
        except: yo = None
        try:    xunit = kwargs["xunit"]
        except: xunit = ''
        try:    yunit = kwargs["yunit"]
        except: yunit = ''
        try:    do_fwhm = kwargs["do_fwhm"]
        except: do_fwhm = True
        try:    arg4main = kwargs["arg4main"]
        except: arg4main = {'cmap': 'viridis'}
        try:    arg4top = kwargs["arg4top"]
        except: arg4top = {}
        try:    arg4side = kwargs["arg4side"]
        except: arg4side = {}

        try:    figure_width = kwargs["figure_width"]*pixels_to_inches
        except: figure_width = 10
        try:    figure_height = kwargs["figure_height"]*pixels_to_inches
        except: figure_height = 7.5

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        plot_profile_widget = PlotProfileWidget(self,
                                                xmatrix=xmatrix,
                                                ymatrix=ymatrix,
                                                zmatrix=zmatrix,
                                                xlabel=xlabel,
                                                ylabel=ylabel,
                                                zlabel=zlabel,
                                                title=str4title,
                                                xo=xo,
                                                yo=yo,
                                                xunit=xunit,
                                                yunit=yunit,
                                                do_fwhm=do_fwhm,
                                                arg4main=arg4main,
                                                arg4top=arg4top,
                                                arg4side=arg4side,
                                                figure_width=figure_width,
                                                figure_height=figure_height)

        self.setFixedWidth(plot_profile_widget.width())
        self.setFixedHeight(plot_profile_widget.height())

        self.update()


class PlotProfileInteractive(WavePyInteractiveWidget):
    def get_plot_tab_name(self):
        return self.__title

    def build_widget(self, **kwargs):
        try:
            self.__title = kwargs["title"]
        except:
            self.__title = "Profile Plot"

        xmatrix = kwargs["xmatrix"]
        ymatrix = kwargs["ymatrix"]
        zmatrix = kwargs["zmatrix"]
        try: xlabel = kwargs["xlabel"]
        except: xlabel = "x"
        try: ylabel = kwargs["ylabel"]
        except: ylabel = "y"
        try: zlabel = kwargs["zlabel"]
        except: zlabel = "z"
        try: xo = kwargs["xo"]
        except: xo = None
        try: yo = kwargs["yo"]
        except: yo = None
        try: xunit = kwargs["xunit"]
        except: xunit = ''
        try: yunit = kwargs["yunit"]
        except: yunit = ''
        try: do_fwhm = kwargs["do_fwhm"]
        except: do_fwhm = True
        try: arg4main = kwargs["arg4main"]
        except: arg4main = {'cmap': 'viridis'}
        try: arg4top = kwargs["arg4top"]
        except: arg4top = {}
        try: arg4side = kwargs["arg4side"]
        except: arg4side = {}

        try:    figure_width = kwargs["figure_width"]*pixels_to_inches
        except: figure_width = 10
        try:    figure_height = kwargs["figure_height"]*pixels_to_inches
        except: figure_height = 7.5

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        self.__plot_profile_widget = PlotProfileWidget(self.get_central_widget(),
                                                       xmatrix=xmatrix,
                                                       ymatrix=ymatrix,
                                                       zmatrix=zmatrix,
                                                       xlabel=xlabel,
                                                       ylabel=ylabel,
                                                       zlabel=zlabel,
                                                       title=self.__title,
                                                       xo=xo,
                                                       yo=yo,
                                                       xunit=xunit,
                                                       yunit=yunit,
                                                       do_fwhm=do_fwhm,
                                                       arg4main=arg4main,
                                                       arg4top=arg4top,
                                                       arg4side=arg4side,
                                                       figure_width=figure_width,
                                                       figure_height=figure_height)

        self.setFixedWidth(self.__plot_profile_widget.width())
        self.setFixedHeight(self.__plot_profile_widget.height())

        self.update()

    def get_accepted_output(self):
        return self.__plot_profile_widget.get_ouput_data()

    def get_rejected_output(self):
        return None

"""
Plot contourf in the main graph plus profiles over vertical and horizontal
lines defined with mouse.

Parameters
----------
xmatrix, ymatrix: ndarray
    `x` and `y` matrix coordinates generated with :py:func:`numpy.meshgrid`

zmatrix: ndarray
    Matrix with the data. Note that ``xmatrix``, ``ymatrix`` and
    ``zmatrix`` must have the same shape

xlabel, ylabel, zlabel: str, optional
    Labels for the axes ``x``, ``y`` and ``z``.

title: str, optional
    title for the main graph #BUG: sometimes this title disappear

xo, yo: float, optional
    if equal to ``None``, it allows to use the mouse to choose the vertical
    and horizontal lines for the profile. If not ``None``, the profiles
    lines are are centered at ``(xo,yo)``

xunit, yunit: str, optional
    String to be shown after the values in the small text box

do_fwhm: Boolean, optional
    Calculate and print the FWHM in the figure. The script to calculate the
    FWHM is not very robust, it works well if only one well defined peak is
    present. Turn this off by setting this var to ``False``

*arg4main:
    `*args` for the main graph

*arg4top:
    `*args` for the top graph

*arg4side:
    `*args` for the side graph

Returns
-------

ax_main, ax_top, ax_side: matplotlib.axes
    return the axes in case one wants to modify them.

delta_x, delta_y: float

Example
-------

>>> import numpy as np
>>> import wavepy.utils as wpu
>>> xx, yy = np.meshgrid(np.linspace(-1, 1, 101), np.linspace(-1, 1, 101))
>>> wpu.plot_profile(xx, yy, np.exp(-(xx**2+yy**2)/.2))

Animation of the example above:

.. image:: img/plot_profile_animation.gif

"""
class PlotProfileWidget(QWidget):
    def __init__(self, parent, xmatrix, ymatrix, zmatrix,
                 xlabel='x', ylabel='y', zlabel='z', title='Title',
                 xo=None, yo=None, xunit='', yunit='', do_fwhm=True,
                 arg4main={'cmap': 'viridis'}, arg4top={}, arg4side={}, figure_width=11, figure_height=8.5):
        super(PlotProfileWidget, self).__init__(parent)

        layout = QHBoxLayout()

        figure_canvas = FigureCanvas(Figure(facecolor="white", figsize=(figure_width, figure_height)))
        fig = figure_canvas.figure

        z_min, z_max = float(np.nanmin(zmatrix)), float(np.nanmax(zmatrix))

        fig.suptitle(title + "\nCLICK: select, RIGHT CLICK: reset", fontsize=14, weight='bold')

        # Main contourf plot
        main_subplot = subplot2grid((4, 5), (1, 1), fig=fig, rowspan=3, colspan=3)
        ax_main = fig.gca()
        ax_main.minorticks_on()
        ax_main.grid(True)
        ax_main.get_yaxis().set_tick_params(which='both', direction='out')
        ax_main.get_xaxis().set_tick_params(which='both', direction='out')
        ax_main.set_xlabel(xlabel)
        ax_main.set_ylabel(ylabel)

        main_plot = main_subplot.contourf(xmatrix, ymatrix, zmatrix, 256, **arg4main)

        colorbar_subplot = subplot2grid((4, 20), (1, 0), fig=fig, rowspan=3, colspan=1)
        fig.colorbar(main_plot, cax=colorbar_subplot)

        def set_xticks(ax, ticks=None, labels=None, **kwargs):
            if ticks is None and labels is None:
                locs = ax.get_xticks()
                labels = ax.get_xticklabels()
            elif labels is None:
                locs = ax.set_xticks(ticks)
                labels = ax.get_xticklabels()
            else:
                locs = ax.set_xticks(ticks)
                labels = ax.set_xticklabels(labels, **kwargs)
            for l in labels:
                l.update(kwargs)

            #return locs, silent_list('Text xticklabel', labels)

        def set_yticks(ax, ticks=None, labels=None, **kwargs):
            if ticks is None and labels is None:
                locs = ax.get_yticks()
                labels = ax.get_yticklabels()
            elif labels is None:
                locs = ax.set_yticks(ticks)
                labels = ax.get_yticklabels()
            else:
                locs = ax.set_yticks(ticks)
                labels = ax.set_yticklabels(labels, **kwargs)
            for l in labels:
                l.update(kwargs)

            #return locs, silent_list('Text xticklabel', labels)

        # Top graph, horizontal profile. Empty, wait data from cursor on the graph.
        top_subplot = subplot2grid((4, 5), (0, 1), fig=fig, rowspan=1, colspan=3)
        ax_top = fig.gca()
        ax_top.set_xticklabels([])
        ax_top.minorticks_on()
        ax_top.grid(True, which='both', axis='both')
        ax_top.set_ylabel(zlabel)
        set_yticks(ax_top, np.linspace(z_min, z_max, 3))
        ax_top.set_ylim(z_min, 1.05 * z_max)

        # Side graph, vertical profile. Empty, wait data from cursor on the graph.
        ax_side = side_subplot = subplot2grid((4, 5), (1, 4), fig=fig, rowspan=3, colspan=1)
        ax_side.set_yticklabels([])
        ax_side.minorticks_on()
        ax_side.grid(True, which='both', axis='both')
        ax_side.set_xlabel(zlabel)
        ax_side.xaxis.set_label_position('top')
        set_xticks(ax_side, np.linspace(z_min, z_max, 3), rotation=-90)
        ax_side.set_xlim(z_min, 1.05 * z_max)

        def onclick(event):
            if (event.xdata is not None and event.ydata is not None and event.button == 1):
                return plot_profiles_at(event.xdata, event.ydata)

            if event.button == 3:
                for subplot in [main_subplot, top_subplot, side_subplot]:
                    subplot.lines = []
                    subplot.legend_ = None

                fig.canvas.draw_idle()

        def plot_profiles_at(_xo, _yo):
            # catch the x and y position to draw the profile
            _xo = xmatrix[1, np.argmin(np.abs(xmatrix[1, :] - _xo))]
            _yo = ymatrix[np.argmin(np.abs(ymatrix[:, 1] - _yo)), 1]

            # plot the vertical and horiz. profiles that pass at xo and yo
            lines = top_subplot.plot(xmatrix[ymatrix == _yo], zmatrix[ymatrix == _yo], lw=2, drawstyle='steps-mid', **arg4top)
            side_subplot.plot(zmatrix[xmatrix == _xo],  ymatrix[xmatrix == _xo], lw=2, drawstyle='steps-mid', **arg4side)

            # plot the vertical and horz. lines in the main graph
            last_color = lines[0].get_color()
            main_subplot.axhline(_yo, ls='--', lw=2, color=last_color)
            main_subplot.axvline(_xo, ls='--', lw=2, color=last_color)

            message = r'$x_o = %.4g %s$' % (_xo, xunit) + '\n' + r'$y_o = %.4g %s$' % (_yo, yunit)

            main_subplot_x_min, main_subplot_x_max = main_subplot.get_xlim()
            main_subplot_y_min, main_subplot_y_max = main_subplot.get_ylim()

            # calculate and plot the FWHM
            _delta_x = None
            _delta_y = None

            if do_fwhm:
                [fwhm_top_x, fwhm_top_y] = plot_tools.fwhm_xy(xmatrix[(ymatrix == _yo) & (xmatrix > main_subplot_x_min) & (xmatrix < main_subplot_x_max)],
                                                              zmatrix[(ymatrix == _yo) & (xmatrix > main_subplot_x_min) & (xmatrix < main_subplot_x_max)])

                [fwhm_side_x, fwhm_side_y] = plot_tools.fwhm_xy(ymatrix[(xmatrix == _xo) & (ymatrix > main_subplot_y_min) & (ymatrix < main_subplot_y_max)],
                                                                zmatrix[(xmatrix == _xo) & (ymatrix > main_subplot_y_min) & (ymatrix < main_subplot_y_max)])

                if len(fwhm_top_x) == 2:
                    _delta_x = abs(fwhm_top_x[0] - fwhm_top_x[1])
                    message += '\n' + r'$FWHM_x = {0:.4g} {1:s}'.format(_delta_x, xunit) + '$'
                    top_subplot.plot(fwhm_top_x, fwhm_top_y, 'r--+', lw=1.5, ms=15, mew=1.4)

                if len(fwhm_side_x) == 2:
                    _delta_y = abs(fwhm_side_x[0] - fwhm_side_x[1])
                    message += '\n' + r'$FWHM_y = {0:.4g} {1:s}'.format(_delta_y, yunit) + '$'
                    side_subplot.plot(fwhm_side_y, fwhm_side_x, 'r--+', lw=1.5, ms=15, mew=1.4)

            # adjust top and side graphs to the zoom of the main graph
            fig.suptitle(title, fontsize=14, weight='bold')

            top_subplot.set_xlim(main_subplot_x_min, main_subplot_x_max)
            side_subplot.set_ylim(main_subplot_y_min, main_subplot_y_max)

            fig.texts = []
            fig.text(.76, .75, message, fontsize=14, va='bottom', bbox=dict(facecolor=last_color, alpha=0.5))
            fig.canvas.draw_idle()

            return [_delta_x, _delta_y]

        [delta_x, delta_y] = [None, None]

        if xo is None and yo is None:
            cursor = Cursor(ax_main, useblit=True, color='red', linewidth=2) # cursor on the main graph
            fig.canvas.mpl_connect('button_press_event', onclick)
        else:
            [delta_x, delta_y] = plot_profiles_at(xo, yo)

        self.__figure_canvas = figure_canvas
        self.__output_data = [ax_main, ax_top, ax_side, delta_x, delta_y]

        self.setFixedWidth(self.__figure_canvas.get_width_height()[0])
        self.setFixedHeight(self.__figure_canvas.get_width_height()[1])

        layout.addWidget(figure_canvas)

        self.setLayout(layout)

    def get_figure_canvas(self):     return self.__figure_canvas
    def get_ouput_data(self): return self.__output_data
