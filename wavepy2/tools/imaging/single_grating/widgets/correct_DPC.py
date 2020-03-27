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
from wavepy2.util.plot.plotter import WavePyWidget, WavePyInteractiveWidget


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

class CorrectDPCSubtractMean(WavePyWidget):
    def get_plot_tab_name(self): return "Correct DPC"

    def build_mpl_figure(self, **kwargs):
        angle   = kwargs["angle"]

        figure = Figure()

        figure.gca().hist(angle[0].flatten()/np.pi, 201, histtype='step', linewidth=2)
        figure.gca().hist(angle[1].flatten()/np.pi, 201, histtype='step', linewidth=2)
        figure.gca().set_xlabel(r'Angle [$\pi$rad]')
        figure.gca().set_title('Correct DPC\nAngle displacement of fringes [\u03c0 rad]')
        figure.gca().legend(('DPC x', 'DPC y'))
        figure.tight_layout()

        return figure

from wavepy2.util.plot.plot_tools import WIDGET_FIXED_WIDTH
from wavepy2.util.plot.widgets.graphical_select_point_idx import GraphicalSelectPointIdx

class CorrectZeroFromUnwrap(WavePyInteractiveWidget):
    def __init__(self, parent):
        super(CorrectZeroFromUnwrap, self).__init__(parent, message="Correct Zero", title="Correct Zero")

    def build_widget(self, **kwargs):
        angleArray = kwargs["angleArray"]

        self.__initialize(angleArray)

        self.get_central_widget().layout().addWidget(GraphicalSelectPointIdx(self, image=self.__pi_jump, selection_listener=self.set_selection))

        self.setFixedWidth(WIDGET_FIXED_WIDTH*1.1)

        self.update()

    def get_accepted_output(self):
        return self.__angle_array, self.__pi_jump_i

    def get_rejected_output(self):
        return self.__angle_array_initial, None

    def set_selection(self, xo, yo):
        j_o, i_o = int(xo), int(yo)

        if not j_o is None:
            self.__angle_array -= self.__pi_jump[i_o, j_o] * np.pi
            self.__pi_jump_i = self.__pi_jump[i_o, j_o]
        else:
            self.__pi_jump_i = None

    def __initialize(self, angleArray):
        self.__angle_array = angleArray
        self.__pi_jump     = np.round(self.__angle_array / np.pi)
        self.__pi_jump_i   = None

        self.__angle_array_initial = angleArray
