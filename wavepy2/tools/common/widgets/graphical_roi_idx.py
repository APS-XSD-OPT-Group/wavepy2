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
from matplotlib.widgets import RectangleSelector

from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.tools.common.widgets.image_to_change import ImageToChange
from wavepy2.util.plot.plotter import pixels_to_inches

class GraphicalRoiIdx(QWidget):
    def __init__(self, parent, image, set_crop_output_listener, kwargs4graph={'cmap': 'viridis'}, application_name=None, figure_width=10, figure_height=7.5, **kwargs):
        super(GraphicalRoiIdx, self).__init__(parent)

        logger = get_registered_logger_instance(application_name=application_name)

        layout = QHBoxLayout()

        figure_canvas = FigureCanvas(Figure(facecolor="white", figsize=(figure_width, figure_height)))
        figure = figure_canvas.figure

        ax = figure.subplots()

        surface = ax.imshow(image, **kwargs4graph)
        surface.cmap.set_over('#FF0000')  # Red
        surface.cmap.set_under('#8B008B')  # Light Cyan

        ax.set_xlabel('Pixels')
        ax.set_ylabel('Pixels')
        ax.set_title("Choose Roi, Right Click: reset", fontsize=16, color='r', weight='bold')

        figure.colorbar(surface)

        def onselect(eclick, erelease):
            """eclick and erelease are matplotlib events at press and release"""

            if eclick.button == 3: # right click
                ax.set_xlim(0, np.shape(image)[1])
                ax.set_ylim(np.shape(image)[0], 0)

                set_crop_output_listener([0, -1, 0, -1])

            elif eclick.button == 1:
                ROI_j_lim = np.sort([eclick.xdata, erelease.xdata]).astype(int).tolist()
                ROI_i_lim = np.sort([eclick.ydata, erelease.ydata]).astype(int).tolist()
                # this round method has an error of +-1pixel

                ax.set_xlim(ROI_j_lim[0] - 1, ROI_j_lim[1] + 1)
                ax.set_ylim(ROI_i_lim[1] + 1, ROI_i_lim[0] - 1)

                logger.print('\nSelecting ROI:')
                logger.print(' lower position : (%d, %d)' % (ROI_j_lim[0], ROI_i_lim[0]))
                logger.print(' higher position   : (%d, %d)' % (ROI_j_lim[1], ROI_i_lim[1]))
                logger.print(' width x and y: (%d, %d)' % (ROI_j_lim[1] - ROI_j_lim[0], ROI_i_lim[1] - ROI_i_lim[0]))

                set_crop_output_listener(ROI_i_lim + ROI_j_lim)

        def toggle_selector(event):
            logger.print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                logger.print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                logger.print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)

        toggle_selector.RS = RectangleSelector(figure.gca(), onselect,
                                               drawtype='box',
                                               rectprops=dict(facecolor='purple',
                                                              edgecolor='black',
                                                              alpha=0.5,
                                                              fill=True))

        figure.canvas.mpl_connect('key_press_event', toggle_selector)
        figure.tight_layout(rect=[0, 0, 1, 1])

        layout.addWidget(figure_canvas)

        self.__image_to_change = ImageToChange(mpl_image=surface, mpl_figure=figure)

        self.setLayout(layout)

    def get_image_to_change(self): return self.__image_to_change
