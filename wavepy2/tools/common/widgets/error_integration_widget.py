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

class ErrorIntegration(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Error Integration"

    def build_mpl_figure(self, **kwargs):
        delx_f     = kwargs["delx_f"]
        dely_f     = kwargs["dely_f"]

        func     = kwargs["func"]
        pixelsize = kwargs["pixelsize"]

        grad_x  = kwargs["grad_x"]
        grad_y  = kwargs["grad_y"]
        error_x  = kwargs["error_x"]
        error_y  = kwargs["error_y"]

        xx, yy = common_tools.realcoordmatrix(func.shape[1], pixelsize[1], func.shape[0], pixelsize[0])
        midleX = xx.shape[0] // 2
        midleY = xx.shape[1] // 2

        figure = Figure(figsize=(9, 6.4)) # 14, 10

        ax1 = figure.add_subplot(221)
        ax1.ticklabel_format(style='sci', axis='both', scilimits=(0, 1))
        ax1.plot(xx[midleX, :], delx_f[midleX, :], '-kx', markersize=10, label='dx data')
        ax1.plot(xx[midleX, :], grad_x[midleX, :], '-r+', markersize=10, label='dx reconstructed')
        ax1.legend(loc=7)

        ax2 = figure.add_subplot(223, sharex=ax1)
        ax2.plot(xx[midleX, :], error_x[midleX, :], '-g.', label='error x')
        ax2.set_title(r'$\mu$ = {:.2g}'.format(np.mean(error_x[midleX, :])))
        ax2.legend(loc=7)

        ax3 = figure.add_subplot(222, sharex=ax1, sharey=ax1)
        ax3.plot(yy[:, midleY], dely_f[:, midleY], '-kx', markersize=10, label='dy data')
        ax3.plot(yy[:, midleY], grad_y[:, midleY], '-r+', markersize=10, label='dy reconstructed')
        ax3.legend(loc=7)

        ax4 = figure.add_subplot(224, sharex=ax1, sharey=ax2)
        ax4.plot(yy[:, midleY], error_y[:, midleY], '-g.', label='error y')
        ax4.set_title(r'$\mu$ = {:.2g}'.format(np.mean(error_y[:, midleY])))
        ax4.legend(loc=7)

        figure.suptitle('Error integration', fontsize=22)

        return figure
