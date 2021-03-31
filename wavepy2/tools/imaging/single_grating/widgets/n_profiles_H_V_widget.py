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

from matplotlib.pyplot import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt

from scipy.ndimage.filters import uniform_filter1d

from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, get_registered_plotter_instance, pixels_to_inches


from warnings import filterwarnings
filterwarnings("ignore")

class NProfilesHV(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(NProfilesHV, self).__init__(parent=parent, application_name=application_name)

        self.__plotter = get_registered_plotter_instance(application_name=application_name)

    def get_plot_tab_name(self): return "N Profiles H/V"

    def build_widget(self, **kwargs):
        arrayH            = kwargs["arrayH"]
        arrayV            = kwargs["arrayV"]
        virtual_pixelsize = kwargs["virtual_pixelsize"]
        zlabel            = kwargs["zlabel"]
        titleH            = kwargs["titleH"]
        titleV            = kwargs["titleV"]
        saveFileSuf       = kwargs["saveFileSuf"]
        nprofiles         = kwargs["nprofiles"]
        remove1stOrderDPC = kwargs["remove1stOrderDPC"]
        filter_width      = kwargs["filter_width"]
        output_data       = kwargs["output_data"]

        try:    figure_width = kwargs["figure_width"]*pixels_to_inches
        except: figure_width = 11

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        xxGrid, yyGrid = common_tools.grid_coord(arrayH, virtual_pixelsize)

        fit_coefs = [[], []]
        data2saveH = None
        data2saveV = None
        labels_H = None
        labels_V = None

        rcParams['lines.markersize'] = 4
        rcParams['lines.linewidth'] = 2

        # Horizontal
        if np.all(np.isfinite(arrayH)):
            figure1_h, figure2_h, data2saveH, labels_H = self.__create_H_plot(arrayH,
                                                                              arrayV,
                                                                              zlabel,
                                                                              titleH,
                                                                              saveFileSuf,
                                                                              nprofiles,
                                                                              remove1stOrderDPC,
                                                                              filter_width,
                                                                              fit_coefs,
                                                                              xxGrid,
                                                                              fig_width=figure_width)
            tab_index = 0
        else:
            figure1_h = self.__get_empty_figure()
            figure2_h = self.__get_empty_figure()
            tab_index = 1

        # Vertical
        if np.all(np.isfinite(arrayV)):
            figure1_v, figure2_v, data2saveV, labels_V = self.__create_V_plot(arrayH,
                                                                              arrayV,
                                                                              zlabel,
                                                                              titleV,
                                                                              saveFileSuf,
                                                                              nprofiles,
                                                                              remove1stOrderDPC,
                                                                              filter_width,
                                                                              fit_coefs,
                                                                              yyGrid,
                                                                              fig_width=figure_width)
        else:
            figure1_v = self.__get_empty_figure()
            figure2_v = self.__get_empty_figure()
            tab_index = 0

        tabs = plot_tools.tabWidget(self, width=plot_tools.WIDGET_FIXED_WIDTH*1.4)

        tab_h = plot_tools.createTabPage(tabs, "Horizontal")
        tab_v = plot_tools.createTabPage(tabs, "Vertical")

        tabs_h = plot_tools.tabWidget(tab_h)
        tabs_v = plot_tools.tabWidget(tab_v)

        plot_tools.createTabPage(tabs_h, titleH, widgetToAdd=FigureCanvas(figure1_h))
        plot_tools.createTabPage(tabs_h, titleH + ", profile positions", widgetToAdd=FigureCanvas(figure2_h))

        plot_tools.createTabPage(tabs_v, titleV, widgetToAdd=FigureCanvas(figure1_v))
        plot_tools.createTabPage(tabs_v, titleV + ", profile positions", widgetToAdd=FigureCanvas(figure2_v))

        tabs.setCurrentIndex(tab_index)

        output_data.set_parameter("dataH", data2saveH)
        output_data.set_parameter("dataV", data2saveV)
        output_data.set_parameter("labels_H", labels_H)
        output_data.set_parameter("labels_V", labels_V)
        output_data.set_parameter("fit_coefs", fit_coefs)

        self.setFixedWidth(tabs.width()+10)
        self.setFixedHeight(700)

    def __get_empty_figure(self):
        figure = Figure(figsize=(10, 10))
        figure.text(0.25, 0.5, "Nothing to Display", fontsize=24, color="black")

        return figure

    def __create_H_plot(self, arrayH, arrayV, zlabel, titleH, saveFileSuf, nprofiles, remove1stOrderDPC, filter_width, fit_coefs, xxGrid, fig_width=12):
        figure1 = Figure(figsize=(fig_width, fig_width * 9 / 16))

        xvec       = xxGrid[0, :]
        data2saveH = np.c_[xvec]
        header     = ['x [m]']

        if filter_width != 0: arrayH_filtered = uniform_filter1d(arrayH, filter_width, 0)
        else: arrayH_filtered = arrayH

        ls_cycle, lc_jet = plot_tools.line_style_cycle(['-'], ['o', 's', 'd', '^'], ncurves=nprofiles, cmap_str='gist_rainbow_r')

        lc = []
        labels_H = []
        for i, row in enumerate(np.linspace(filter_width // 2, np.shape(arrayV)[0] - filter_width // 2 - 1, nprofiles + 2, dtype=int)):
            if i == 0 or i == nprofiles + 1: continue

            yvec = arrayH_filtered[row, :]
            lc.append(next(lc_jet))
            p01 = np.polyfit(xvec, yvec, 1)
            fit_coefs[0].append(p01)

            if remove1stOrderDPC: yvec -= p01[0] * xvec + p01[1]

            figure1.gca().plot(xvec * 1e6, yvec, next(ls_cycle), color=lc[i - 1], label=str(row))
            if not remove1stOrderDPC: figure1.gca().plot(xvec * 1e6, p01[0] * xvec + p01[1], '--', color=lc[i - 1], lw=3)

            data2saveH = np.c_[data2saveH, yvec]
            header.append(str(row))
            labels_H.append(str(row))

        if remove1stOrderDPC: titleH = titleH + ', 2nd order removed'

        figure1.legend(title='Pixel Y', loc='center left', fontsize=12)
        figure1.gca().set_xlabel(r'x [$\mu m$]', fontsize=18)
        figure1.gca().set_ylabel(zlabel, fontsize=18)
        figure1.gca().set_title(titleH + ', Filter Width = {:d} pixels'.format(filter_width), fontsize=20)

        self.append_mpl_figure_to_save(figure=figure1, figure_file_name=common_tools.get_unique_filename(saveFileSuf + "_H", "png"))

        header.append(zlabel + ', Filter Width = {:d} pixels'.format(filter_width))

        self.__plotter.save_csv_file(data2saveH, file_prefix=saveFileSuf, file_suffix='_WF_profiles_H', headerList=header)

        figure2 = Figure(figsize=(12, 12 * 9 / 16))
        figure2.gca().imshow(arrayH, cmap='RdGy', vmin=common_tools.mean_plus_n_sigma(arrayH, -3), vmax=common_tools.mean_plus_n_sigma(arrayH, 3))
        figure2.gca().set_xlabel('Pixel')
        figure2.gca().set_ylabel('Pixel')
        figure2.gca().set_title(titleH + ', Profiles Position')

        currentAxis = figure2.gca()

        _, lc_jet = plot_tools.line_style_cycle(['-'], ['o', 's', 'd', '^'], ncurves=nprofiles, cmap_str='gist_rainbow_r')

        for i, row in enumerate(np.linspace(filter_width // 2, np.shape(arrayV)[0] - filter_width // 2 - 1, nprofiles + 2, dtype=int)):
            if i == 0 or i == nprofiles + 1: continue

            currentAxis.add_patch(Rectangle((-.5, row - filter_width // 2 - .5), np.shape(arrayH)[1], filter_width, facecolor=lc[i - 1], alpha=.5))
            figure2.gca().axhline(row, color=lc[i - 1])

        self.append_mpl_figure_to_save(figure=figure2, figure_file_name=common_tools.get_unique_filename(saveFileSuf + "_H", "png"))

        return figure1, figure2, data2saveH, labels_H


    def __create_V_plot(self, arrayH, arrayV, zlabel, titleV, saveFileSuf, nprofiles, remove1stOrderDPC, filter_width, fit_coefs, yyGrid, fig_width=12):
        figure1 = Figure(figsize=(fig_width, fig_width * 9 / 16))

        xvec = yyGrid[:, 0]
        data2saveV = np.c_[xvec]
        header = ['y [m]']

        if filter_width != 0: arrayV_filtered = uniform_filter1d(arrayV, filter_width, 1)
        else: arrayV_filtered = arrayV

        ls_cycle, lc_jet = plot_tools.line_style_cycle(['-'], ['o', 's', 'd', '^'], ncurves=nprofiles, cmap_str='gist_rainbow_r')

        lc = []
        labels_V = []
        for i, col in enumerate(np.linspace(filter_width // 2, np.shape(arrayH)[1] - filter_width // 2 - 1, nprofiles + 2, dtype=int)):
            if i == 0 or i == nprofiles + 1: continue

            yvec = arrayV_filtered[:, col]
            lc.append(next(lc_jet))
            p10 = np.polyfit(xvec, yvec, 1)
            fit_coefs[1].append(p10)

            if remove1stOrderDPC: yvec -= p10[0] * xvec + p10[1]

            figure1.gca().plot(xvec * 1e6, yvec, next(ls_cycle), color=lc[i - 1], label=str(col))
            if not remove1stOrderDPC: figure1.gca().plot(xvec * 1e6, p10[0] * xvec + p10[1], '--', color=lc[i - 1], lw=3)

            data2saveV = np.c_[data2saveV, yvec]
            header.append(str(col))
            labels_V.append(str(col))

        if remove1stOrderDPC: titleV = titleV + ', 2nd order removed'

        figure1.legend(title='Pixel X', loc=7, fontsize=12)

        figure1.gca().set_xlabel(r'y [$\mu m$]', fontsize=18)
        figure1.gca().set_ylabel(zlabel, fontsize=18)
        figure1.gca().set_title(titleV + ', Filter Width = {:d} pixels'.format(filter_width), fontsize=20)

        self.append_mpl_figure_to_save(figure=figure1, figure_file_name=common_tools.get_unique_filename(saveFileSuf + "_V", "png"))

        header.append(zlabel + ', Filter Width = {:d} pixels'.format(filter_width))

        self.__plotter.save_csv_file(data2saveV, file_prefix=saveFileSuf, file_suffix='_WF_profiles_V', headerList=header)

        figure2 = Figure(figsize=(12, 12 * 9 / 16))
        figure2.gca().imshow(arrayV, cmap='RdGy', vmin=common_tools.mean_plus_n_sigma(arrayV, -3), vmax=common_tools.mean_plus_n_sigma(arrayV, 3))
        figure2.gca().set_xlabel('Pixel')
        figure2.gca().set_ylabel('Pixel')
        figure2.gca().set_title(titleV + ', Profiles Position')

        currentAxis = figure2.gca()

        for i, col in enumerate(np.linspace(filter_width // 2, np.shape(arrayH)[1] - filter_width // 2 - 1, nprofiles + 2, dtype=int)):
            if i == 0 or i == nprofiles + 1: continue

            currentAxis.add_patch(Rectangle((col - filter_width // 2 - .5, -.5), filter_width, np.shape(arrayV)[0], facecolor=lc[i - 1], alpha=.5))
            figure2.gca().axvline(col, color=lc[i - 1])

        self.append_mpl_figure_to_save(figure=figure2, figure_file_name=common_tools.get_unique_filename(saveFileSuf + "_V", "png"))

        return figure1, figure2, data2saveV, labels_V
