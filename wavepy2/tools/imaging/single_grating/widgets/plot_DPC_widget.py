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
from wavepy2.util.common import common_tools
from wavepy2.util.plot.plotter import WavePyWidget

from warnings import filterwarnings
filterwarnings("ignore")

class PlotDPC(WavePyWidget):
    def get_plot_tab_name(self): return "Differential Phase [\u03c0 rad]" + self.__title

    def build_mpl_figure(self, **kwargs):
        differential_phase_01 = kwargs["differential_phase_01"]
        differential_phase_10 = kwargs["differential_phase_10"]
        pixelsize = kwargs["pixelsize"]
        titleStr  = kwargs["titleStr"]

        if not common_tools.is_empty_string(titleStr): self.__title = ', ' + titleStr
        else: self.__title = ""

        factor, unit_xy = common_tools.choose_unit(np.sqrt(differential_phase_01.size)*pixelsize[0])

        differential_phase_01_plot = differential_phase_01*pixelsize[1]/np.pi
        differential_phase_10_plot = differential_phase_10*pixelsize[0]/np.pi

        vlim01 = np.max((np.abs(common_tools.mean_plus_n_sigma(differential_phase_01_plot, -5)),
                         np.abs(common_tools.mean_plus_n_sigma(differential_phase_01_plot, 5))))
        vlim10 = np.max((np.abs(common_tools.mean_plus_n_sigma(differential_phase_10_plot, -5)),
                         np.abs(common_tools.mean_plus_n_sigma(differential_phase_10_plot, 5))))

        figure = Figure(figsize=(12, 6))

        def create_plot(ax, img, vlim, title):
            im = ax.imshow(img, cmap='RdGy_r',
                      vmin=-vlim, vmax=vlim,
                      extent=common_tools.extent_func(img, pixelsize)*factor)
            ax.set_xlabel(r'$[{0} m]$'.format(unit_xy))
            ax.set_ylabel(r'$[{0} m]$'.format(unit_xy))
            figure.colorbar(im, shrink=0.5)
            ax.set_title(title, fontsize=18, weight='bold')

        create_plot(figure.add_subplot(1, 2, 1), differential_phase_01_plot, vlim01, 'DPC - Horizontal')
        create_plot(figure.add_subplot(1, 2, 2), differential_phase_10_plot, vlim10, 'DPC - Vertical')

        figure.suptitle('Differential Phase ' + r'[$\pi$ rad]' + self.__title, fontsize=18, weight='bold')
        figure.tight_layout(rect=[0, 0, 1, 1])

        return figure
