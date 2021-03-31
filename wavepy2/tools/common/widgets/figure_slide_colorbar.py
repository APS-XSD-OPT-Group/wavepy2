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
from PyQt5.QtWidgets import QWidget, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Slider

from wavepy2.util.common import common_tools
from wavepy2.util.plot.plot_tools import WIDGET_FIXED_WIDTH, widgetBox, separator, button, radioButtons


class FigureSlideColorbar(QWidget):
    def __init__(self, parent, image, title='', xlabel='', ylabel='', cmin_o=None, cmax_o=None, **kwargs):
        super(FigureSlideColorbar, self).__init__(parent)

        __radio1_values = ['gray', 'gray_r', 'viridis', 'viridis_r', 'inferno', 'rainbow', 'RdGy_r']
        __radio2_values = ['lin', 'pow 1/7', 'pow 1/3', 'pow 3', 'pow 7']
        __radio3_values = ['none', 'sigma = 1', 'sigma = 3', 'sigma = 5']

        self.__image = image.astype(float) # avoid problems when masking integerimages. necessary because integer NAN doesn't exist
        self.__images_to_change = []

        layout = QGridLayout(self)

        self.setFixedWidth(WIDGET_FIXED_WIDTH)

        figure_canvas = FigureCanvas(Figure())
        figure = figure_canvas.figure

        ax = figure.subplots()
        figure.subplots_adjust(left=-0.25, bottom=0.25)

        surface = ax.imshow(image, cmap='viridis', **kwargs)
        surface.cmap.set_over('#FF0000')  # Red
        surface.cmap.set_under('#8B008B')  # Light Cyan

        ax.set_title(title, fontsize=14, weight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        figure.colorbar(surface, extend='both')

        #                       [left, bottom, width, height]
        axcmin = figure.add_axes([0.40, 0.05, 0.25, 0.03])
        axcmax = figure.add_axes([0.40, 0.10, 0.25, 0.03])

        if cmin_o is None: cmin_o = surface.get_clim()[0]
        if cmax_o is None: cmax_o = surface.get_clim()[1]

        min_slider_val = (9*cmin_o - cmax_o)/8
        max_slider_val = (9*cmax_o - cmin_o)/8

        scmin = Slider(axcmin, 'Min',
                       min_slider_val, max_slider_val,
                       valinit=cmin_o)
        scmax = Slider(axcmax, 'Max',
                       min_slider_val, max_slider_val,
                       valinit=cmax_o)

        def update(val):
            cmin = scmin.val
            cmax = scmax.val

            if cmin < cmax:
                scmin.label.set_text('Min')
                scmax.label.set_text('Max')
            else:
                scmin.label.set_text('Max')
                scmax.label.set_text('Min')

            surface.set_clim(vmin=min(cmin, cmax), vmax=max(cmin, cmax))

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_clim(vmin=min(cmin, cmax), vmax=max(cmin, cmax))
                image_to_change.get_mpl_figure().canvas.draw()

        scmin.on_changed(update)
        scmax.on_changed(update)

        button_box_container = QWidget()
        button_box_container.setFixedWidth(figure_canvas.get_width_height()[0])
        button_box_container.setFixedHeight(45)
        button_box = widgetBox(button_box_container, orientation="horizontal", width=button_box_container.width())
        separator(button_box, width=button_box_container.width()*0.8)

        def reset():
            scmin.set_val(cmin_o)
            scmax.set_val(cmax_o)
            scmin.reset()
            scmax.reset()

            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_clim(vmin=image_to_change.get_cmin_o(),
                                                         vmax=image_to_change.get_cmax_o())
                image_to_change.get_mpl_figure().canvas.draw()

        def colorfunc():
            surface.set_cmap(__radio1_values[self.radio1])
            surface.cmap.set_over('#FF0000')  # Red
            surface.cmap.set_under('#8B008B')  # Light Cyan
            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_cmap(__radio1_values[self.radio1])
                image_to_change.get_mpl_image().cmap.set_over('#FF0000')  # Red
                image_to_change.get_mpl_image().cmap.set_under('#8B008B')  # Light Cyan
                image_to_change.get_mpl_figure().canvas.draw()

        def lin_or_pow():
            self.radio3 = 0
            self.rb_radio3.buttons[0].setChecked(True)
            filter_sparks()

            if self.radio2   == 0: n = 1
            elif self.radio2 == 1: n = 1/3
            elif self.radio2 == 2: n = 1/7
            elif self.radio2 == 3: n = 3
            elif self.radio2 == 4: n = 7

            def get_image_2plot(image):
                return ((image-image.min())**n*np.ptp(image) / np.ptp(image)**n + image.min())

            surface.set_data(get_image_2plot(self.__image))
            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_data(get_image_2plot(image_to_change.get_mpl_data()))
                image_to_change.get_mpl_figure().canvas.draw()


        def filter_sparks():
            if self.radio3 == 0: reset(); return
            elif self.radio3 == 1: sigma = 1
            elif self.radio3 == 2: sigma = 3
            elif self.radio3 == 3: sigma = 5

            image_2plot = surface.get_array().data

            cmin = common_tools.mean_plus_n_sigma(image_2plot, -sigma)
            cmax = common_tools.mean_plus_n_sigma(image_2plot, sigma)

            scmin.set_val(cmin)
            scmax.set_val(cmax)
            surface.set_clim(vmin=cmin, vmax=cmax)

            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_2plot = image_to_change.get_mpl_image().get_array().data
                cmin = common_tools.mean_plus_n_sigma(image_2plot, -sigma)
                cmax = common_tools.mean_plus_n_sigma(image_2plot, sigma)

                image_to_change.get_mpl_image().set_clim(vmin=cmin, vmax=cmax)
                image_to_change.get_mpl_figure().canvas.draw()

        button(button_box, self, "Reset", callback=reset, width=100, height=35)

        radio_button_box_container = QWidget()
        radio_button_box_container.setFixedWidth(140)
        radio_button_box_container.setFixedHeight(figure_canvas.get_width_height()[1] + button_box_container.height() + 70)
        radio_button_box = widgetBox(radio_button_box_container, "Options", orientation="vertical", width=120)

        self.radio1 = 2
        self.radio2 = 0
        self.radio3 = 0

        self.rb_radio2 = radioButtons(radio_button_box, self, "radio2", btnLabels=__radio2_values, box="Lin or Pow", callback=lin_or_pow)
        self.rb_radio3 = radioButtons(radio_button_box, self, "radio3", btnLabels=__radio3_values, box="Filter Sparks", callback=filter_sparks)
        self.rb_radio1 = radioButtons(radio_button_box, self, "radio1", btnLabels=__radio1_values, box="Color Map", callback=colorfunc)

        layout.addWidget(figure_canvas, 1, 1)
        layout.addWidget(button_box_container, 2, 1)
        layout.addWidget(radio_button_box_container, 0, 0, 2, 1)

        self.setLayout(layout)

    def set_images_to_change(self, images_to_change):
        self.__images_to_change = images_to_change
