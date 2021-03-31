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
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, WavePyInteractiveWidget, pixels_to_inches


class CorrectDPC(WavePyWidget):
    def get_plot_tab_name(self): return "Correct DPC"

    def build_mpl_figure(self, **kwargs):
        angle   = kwargs["angle"]
        pi_jump   = kwargs["pi_jump"]

        figure = Figure()
        h1 = figure.gca().hist(angle[0].flatten()/np.pi, 201, histtype='step', linewidth=2)
        h2 = figure.gca().hist(angle[1].flatten()/np.pi, 201, histtype='step', linewidth=2)

        figure.gca().set_xlabel(r'Angle [$\pi$rad]')
        if pi_jump == [0, 0]:
            lim = np.ceil(np.abs((h1[1][0], h1[1][-1], h2[1][0], h2[1][-1])).max())
            figure.gca().set_xlim([-lim, lim])

        figure.gca().set_title('Correct DPC\n' + 'Angle displacement of fringes [\u03c0 rad]\n' +
                               'Calculated jumps x and y : {:d}, {:d} \u03c0'.format(pi_jump[0], pi_jump[1]))

        figure.gca().legend(('DPC x', 'DPC y'))
        figure.tight_layout()

        return figure

class CorrectDPCHistos(WavePyWidget):
    def get_plot_tab_name(self): return "Correct DPC" if common_tools.is_empty_string(self.__title) else self.__title

    def build_mpl_figure(self, **kwargs):
        angle   = kwargs["angle"]
        self.__title = kwargs["title"]

        figure = Figure()

        figure.gca().hist(angle[0].flatten()/np.pi, 201, histtype='step', linewidth=2)
        figure.gca().hist(angle[1].flatten()/np.pi, 201, histtype='step', linewidth=2)
        figure.gca().set_xlabel(r'Angle [$\pi$rad]')
        figure.gca().set_title('Correct DPC\nAngle displacement of fringes [\u03c0 rad]')
        figure.gca().legend(('DPC x', 'DPC y'))
        figure.tight_layout()

        return figure

from wavepy2.util.log.logger import get_registered_logger_instance, LoggerColor
from wavepy2.util.plot.plot_tools import WIDGET_FIXED_WIDTH
from wavepy2.tools.common.widgets.graphical_select_point_idx import GraphicalSelectPointIdx


class CorrectDPCCenter(WavePyInteractiveWidget):
    __harmonic = ["01", "10"]

    def __init__(self, parent, application_name=None, **kwargs):
        super(CorrectDPCCenter, self).__init__(parent, message="Correct DPC Center", title="Correct DPC Center", application_name=application_name)

        self.__logger  = get_registered_logger_instance(application_name=application_name)

    def build_widget(self, **kwargs):
        self.__initialize(kwargs["angle"])

        main_box = plot_tools.widgetBox(self.get_central_widget(), "", width=WIDGET_FIXED_WIDTH*2, orientation="horizontal")

        harm_box = [plot_tools.widgetBox(main_box, "Harmonic 01"), plot_tools.widgetBox(main_box, "Harmonic 10")]

        self.__tab_widget = [plot_tools.tabWidget(harm_box[0]), plot_tools.tabWidget(harm_box[1])]

        self.__result_canvas_histo = [FigureCanvas(Figure()), FigureCanvas(Figure())]
        self.__result_canvas       = [FigureCanvas(Figure()), FigureCanvas(Figure())]

        for index in [0, 1]:
            self.__update_result_figures(index)

            plot_tools.createTabPage(self.__tab_widget[index], "Correct Zero", GraphicalSelectPointIdx(self,
                                                                                                       image=self.__pi_jump[index],
                                                                                                       selection_listener=self.set_selection,
                                                                                                       args_for_listener=index))
            plot_tools.createTabPage(self.__tab_widget[index], "Angle Displacement of Fringes", self.__result_canvas_histo[index])
            plot_tools.createTabPage(self.__tab_widget[index], "DPC Center",                    self.__result_canvas[index])

            harm_box[index].setFixedHeight(max(self.__result_canvas_histo[index].get_width_height()[1], self.__result_canvas[index].get_width_height()[1])+220)

        self.setFixedWidth(WIDGET_FIXED_WIDTH*2.1)

        self.update()


    def get_accepted_output(self):
        return self.__angle

    def get_rejected_output(self):
        return self.__angle_initial

    def set_selection(self, xo, yo, index):
        j_o, i_o = int(xo), int(yo)
        #i_o, j_o = int(xo), int(yo)

        if not j_o is None:
            self.__angle[index]     = self.__angle_initial[index] - self.__pi_jump[index][i_o, j_o] * np.pi
            self.__pi_jump_i[index] = self.__pi_jump[index][i_o, j_o]
        else:
            self.__pi_jump_i[index] = None

        self.__logger.print_other("MESSAGE: pi jump " + self.__harmonic[index] + ": {:} pi".format(self.__pi_jump_i[index]), color=LoggerColor.BLUE)

        self.__update_result_figures(index)

    def __initialize(self, angle):
        self.__angle     = angle
        self.__pi_jump   = [np.round(self.__angle[0] / np.pi), np.round(self.__angle[1] / np.pi)]
        self.__pi_jump_i = [None, None]

        self.__angle_initial = angle

    def __update_result_figures(self, index):
        figure = self.__result_canvas_histo[index].figure
        figure.clear()

        figure.gca().hist(self.__angle[index].flatten() / np.pi, 101, histtype='step', linewidth=2, color=["#594F83", "orange"][index])
        figure.gca().set_title(r'Angle displacement of fringes [$\pi$ rad]')

        self.__result_canvas_histo[index].draw()

        #if saveFigFlag:
        #    wpu.save_figs_with_idx(saveFileSuf)

        figure = self.__result_canvas[index].figure
        figure.clear()

        vlim = np.max((np.abs(common_tools.mean_plus_n_sigma(self.__angle[index] / np.pi, -5)),
                       np.abs(common_tools.mean_plus_n_sigma(self.__angle[index] / np.pi, 5))))

        im = figure.gca().imshow(self.__angle[index] / np.pi, cmap='RdGy', vmin=-vlim, vmax=vlim)
        figure.colorbar(im)
        figure.gca().set_title("Angle displacement of fringes " + self.__harmonic[index] + r' [$\pi$ rad],')
        figure.gca().set_xlabel('Pixels')
        figure.gca().set_ylabel('Pixels')

        self.__result_canvas[index].draw()

        self.__tab_widget[index].setCurrentIndex(1)
