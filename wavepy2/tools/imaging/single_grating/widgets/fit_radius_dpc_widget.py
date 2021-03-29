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
from wavepy2.util.log.logger import get_registered_logger_instance

from warnings import filterwarnings
filterwarnings("ignore")

class FitRadiusDPC(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(FitRadiusDPC, self).__init__(parent=parent, application_name=application_name)

        self.__logger  = get_registered_logger_instance(application_name=application_name)

    def get_plot_tab_name(self): return "Fit Radius"

    def build_mpl_figure(self, **kwargs):
        dpx       = kwargs["dpx"]
        dpy       = kwargs["dpy"]
        pixelsize = kwargs["pixelsize"]
        kwave     = kwargs["kwave"]
        str4title = kwargs["str4title"]

        xVec = common_tools.realcoordvec(dpx.shape[1], pixelsize[1])
        yVec = common_tools.realcoordvec(dpx.shape[0], pixelsize[0])

        fig = Figure(figsize=(14, 5))
        fig.suptitle(str4title + 'Phase [rad]', fontsize=14)

        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122, sharex=ax1, sharey=ax1)

        ax1.plot(xVec * 1e6, dpx[dpx.shape[0] // 4, :],     '-ob', label='1/4')
        ax1.plot(xVec * 1e6, dpx[dpx.shape[0] // 4 * 3, :], '-og', label='3/4')
        ax1.plot(xVec * 1e6, dpx[dpx.shape[0] // 2, :],     '-or', label='1/2')

        lin_fitx = np.polyfit(xVec, dpx[dpx.shape[0] // 2, :], 1)
        lin_funcx = np.poly1d(lin_fitx)
        ax1.plot(xVec * 1e6, lin_funcx(xVec), '--c', lw=2, label='Fit 1/2')
        curvrad_x = kwave / (lin_fitx[0])

        self.__logger.print_message('lin_fitx[0] x: {:.3g} m'.format(lin_fitx[0]))
        self.__logger.print_message('lin_fitx[1] x: {:.3g} m'.format(lin_fitx[1]))
        self.__logger.print_message('Curvature Radius of WF x: {:.3g} m'.format(curvrad_x))

        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 1))
        ax1.set_xlabel(r'[$\mu m$]')
        ax1.set_ylabel('dpx [radians]')
        ax1.legend(loc=7, fontsize='small')
        ax1.set_title('H Curvature Radius of WF {:.3g} m'.format(curvrad_x), fontsize=16)
        ax1.set_adjustable('box')

        ax2.plot(yVec * 1e6, dpy[:, dpy.shape[1] // 4],     '-ob', label='1/4')
        ax2.plot(yVec * 1e6, dpy[:, dpy.shape[1] // 4 * 3], '-og', label='3/4')
        ax2.plot(yVec * 1e6, dpy[:, dpy.shape[1] // 2],     '-or', label='1/2')

        lin_fity = np.polyfit(yVec,
                              dpy[:, dpy.shape[1] // 2], 1)
        lin_funcy = np.poly1d(lin_fity)
        ax2.plot(yVec * 1e6, lin_funcy(yVec),
                 '--c', lw=2,
                 label='Fit 1/2')
        curvrad_y = kwave / (lin_fity[0])
        self.__logger.print_message('Curvature Radius of WF y: {:.3g} m'.format(curvrad_y))

        ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 1))
        ax2.set_xlabel(r'[$\mu m$]')
        ax2.set_ylabel('dpy [radians]')
        ax2.legend(loc=7, fontsize='small')
        ax2.set_title('V Curvature Radius of WF {:.3g} m'.format(curvrad_y), fontsize=16)
        ax2.set_adjustable('box')

        return fig
