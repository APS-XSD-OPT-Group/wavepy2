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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from wavepy2.util.plot.plot_tools import WIDGET_FIXED_WIDTH
from wavepy2.util.log.logger import get_registered_logger_instance

class GraphicalSelectPointIdx(QWidget):
    def __init__(self, parent, image, selection_listener, args_for_listener, application_name=None, **kwargs4imshow):
        super(GraphicalSelectPointIdx, self).__init__(parent)

        logger = get_registered_logger_instance(application_name=application_name)

        layout = QHBoxLayout()

        figure_canvas = FigureCanvas(Figure(facecolor="white", figsize=(10, 8)))
        figure = figure_canvas.figure

        ax = figure.subplots()

        surface = ax.imshow(image, cmap='Spectral', **kwargs4imshow)
        ax.autoscale(False)

        ax1 = ax.plot(image.shape[1] // 2, image.shape[0] // 2, 'r+', ms=30, picker=10)

        ax.grid()
        ax.set_xlabel('Pixels')
        ax.set_ylabel('Pixels')
        ax.set_title('CHOOSE POINT, Click OK when Done\nRight Click: Select point\n',
                      fontsize=16, color='r', weight='bold')
        figure.colorbar(surface)

        def onclick(event):
            if event.button == 3: # right click
                xo, yo = event.xdata, event.ydata

                logger.print_message('Middle Click: Select point:\tx: {:.0f}, y: {:.0f}'.format(xo, yo))

                ax1[0].set_xdata(xo)
                ax1[0].set_ydata(yo)

                ax.set_title('CHOOSE POINT, Click OK when Done\nRight Click: Select point\n' +
                              'x: {:.0f}, y: {:.0f}'.format(xo, yo),
                              fontsize=16, color='r', weight='bold')

                if np.isnan(xo) or np.isnan(yo): selection_listener(None, None, args_for_listener)
                else: selection_listener(xo, yo, args_for_listener)

                figure.canvas.draw()

        Cursor(ax, useblit=True, color='red', linewidth=2)
        figure.canvas.mpl_connect('button_press_event', onclick)

        layout.addWidget(figure_canvas)

        self.setLayout(layout)
        self.setFixedWidth(WIDGET_FIXED_WIDTH)
