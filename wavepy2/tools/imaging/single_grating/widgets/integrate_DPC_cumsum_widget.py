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

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt

from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, get_registered_plotter_instance

from warnings import filterwarnings
filterwarnings("ignore")

class IntegrateDPCCumSum(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(IntegrateDPCCumSum, self).__init__(parent=parent, application_name=application_name)

        self.__plotter = get_registered_plotter_instance(application_name=application_name)

    def get_plot_tab_name(self): return "Integrate Cumulative Sum " + self.__title

    def build_widget(self, **kwargs):
        data_DPC          = kwargs["data_DPC"]
        wavelength        = kwargs["wavelength"]
        grazing_angle     = kwargs["grazing_angle"]
        projectionFromDiv = kwargs["projectionFromDiv"]
        remove2ndOrder    = kwargs["remove2ndOrder"]
        labels            = kwargs["labels"]
        xlabel            = kwargs["xlabel"]
        ylabel            = kwargs["ylabel"]
        titleStr          = kwargs["titleStr"]
        saveFileSuf       = kwargs["saveFileSuf"]
        direction         = kwargs["direction"]

        output_data       = kwargs["output_data"]

        self.__title = direction

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        figure1 = Figure(figsize=(12, 12*9/16))

        ls_cycle, lc_cycle = plot_tools.line_style_cycle(['-'], ['o', 's', 'd', '^'], ncurves=data_DPC.shape[1] - 1, cmap_str='gist_rainbow_r')

        if grazing_angle//.00001 > 0: projection = 1/np.sin(grazing_angle)*projectionFromDiv
        else: projection = projectionFromDiv

        xvec = data_DPC[:, 0]*projection
        list_integrated = [xvec]
        header = [xlabel + ' [m]']

        for j_line in range(1, data_DPC.shape[1]):
            integrated = (np.cumsum(data_DPC[:, j_line] - np.mean(data_DPC[:, j_line])) * (xvec[1]-xvec[0])) # TODO: removed mean 20181020
            integrated *= -1/2/np.pi*wavelength*np.abs(projection)

            p02 = np.polyfit(xvec, integrated, 2)
            fitted_pol2 = p02[0]*xvec**2 + p02[1]*xvec + p02[2]

            if remove2ndOrder:
                integrated -= fitted_pol2
                titleStr += 'Removed 2nd order, '

            # TODO: check here!!
            if j_line == 1:
                factor_x, unit_x = common_tools.choose_unit(xvec)
                factor_y, unit_y = common_tools.choose_unit(integrated)

            list_integrated.append(integrated)
            header.append(labels[j_line - 1])
            lc = next(lc_cycle)

            figure1.gca().plot(xvec*factor_x, integrated*factor_y, next(ls_cycle), c=lc, label=labels[j_line - 1])
            if not remove2ndOrder: figure1.gca().plot(xvec*1e6, (fitted_pol2)*factor_y, '--', color=lc, lw=3)

        marginx = 0.1*np.ptp(xvec*factor_x)
        figure1.gca().set_xlim([np.min(xvec*factor_x)-marginx, np.max(xvec*factor_x)+marginx])
        figure1.gca().set_xlabel(xlabel + r' [$' + unit_x + ' m$]')
        figure1.gca().set_ylabel(ylabel + r' [$' + unit_y + ' m$]')
        figure1.legend(loc=7, fontsize=12)

        if grazing_angle//.00001 > 0:
            figure1.gca().set_title(titleStr + 'Mirror Height,\n' +
                                    'grazing angle {:.2f} mrad,\n'.format(grazing_angle*1e3) +
                                    'projection due divergence = ' +
                                    r'$ \times $ {:.2f}'.format(projectionFromDiv))
        else:
            figure1.gca().set_title(titleStr + 'Integration Cumulative Sum')

        figure1.tight_layout()

        self.append_mpl_figure_to_save(figure=figure1, figure_file_name=common_tools.get_unique_filename(saveFileSuf, "png"))

        data2saveV = np.asarray(list_integrated).T

        header.append(ylabel + ' [m]')
        if grazing_angle//.00001 > 0:  header.append('grazing_angle = {:.4g}'.format(grazing_angle))
        if projectionFromDiv//1 != 1: header.append('projection due divergence = {:.2f}x'.format(projectionFromDiv))

        self.__plotter.save_csv_file(data2saveV, file_prefix=saveFileSuf, file_suffix='_integrated_' + xlabel, headerList=header)

        output_data.set_parameter("integrated", np.asarray(list_integrated).T)

        layout.addWidget(FigureCanvas(figure1))

        self.setFixedWidth(plot_tools.WIDGET_FIXED_WIDTH*1.4)
        self.setFixedHeight(700)
