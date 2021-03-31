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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from wavepy2.tools.common.widgets.image_to_change import ImageToChange

from wavepy2.util.common import common_tools
from wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches

class SimplePlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return self.__title

    def build_widget(self, **kwargs):
        img                = kwargs["img"]
        pixelsize          = kwargs["pixelsize"]
        try: self.__title = kwargs["title"]
        except: self.__title = "Plot Image"
        try: xlabel = kwargs["xlabel"]
        except: xlabel = r'x [$\mu m$ ]'
        try: ylabel = kwargs["ylabel"]
        except: ylabel = r'y [$\mu m$ ]'

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        widget = SimplePlotWidget(self,
                                  image=img,
                                  title=self.__title,
                                  xlabel=xlabel,
                                  ylabel=ylabel,
                                  extent=common_tools.extent_func(img, pixelsize)*1e6)
        layout.addWidget(widget)

        self.setLayout(layout)

        self.append_mpl_figure_to_save(widget.get_image_to_change().get_mpl_figure())

class SimplePlotWidget(QWidget):
    def __init__(self, parent, image, title='', xlabel='', ylabel='', figure_width=8, figure_height=7, **kwargs4imshow):
        super(SimplePlotWidget, self).__init__(parent)

        figure_canvas = FigureCanvas(Figure((figure_width, figure_height)))
        mpl_figure = figure_canvas.figure

        ax = mpl_figure.subplots(1, 1)
        mpl_image = ax.imshow(image, cmap='viridis', **kwargs4imshow)
        mpl_image.cmap.set_over('#FF0000')  # Red
        mpl_image.cmap.set_under('#8B008B')  # Light Cyan

        ax.set_title(title, fontsize=18, weight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        mpl_figure.colorbar(mpl_image, ax=ax, orientation="vertical")

        self.__image_to_change = ImageToChange(mpl_image=mpl_image, mpl_figure=mpl_figure)

        layout = QVBoxLayout()
        layout.addWidget(figure_canvas)
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

    def get_image_to_change(self):
        return self.__image_to_change
