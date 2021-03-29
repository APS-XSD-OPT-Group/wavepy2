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
from matplotlib.patches import Rectangle
from wavepy2.util.common.common_tools import extent_func, is_empty_string
from wavepy2.util.plot.plotter import WavePyWidget


class ExtractHarmonicPlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return self.__image_name + "Extract Harmonic " + self.__harmonic_name

    def build_mpl_figure(self, **kwargs):
        intensity   = kwargs["intensity"]
        idxPeak_ij  = kwargs["idxPeak_ij"]
        harmonic_ij = kwargs["harmonic_ij"]
        nColumns    = kwargs["nColumns"]
        nRows       = kwargs["nRows"]
        periodHor   = kwargs["periodHor"]
        periodVert  = kwargs["periodVert"]
        image_name  = kwargs["image_name"]

        self.__harmonic_name = harmonic_ij[0] + harmonic_ij[1]
        self.__image_name = "" if is_empty_string(image_name) else image_name + ": "

        figure = Figure(figsize=(8, 7))
        ax = figure.subplots(1, 1)
        ax.imshow(np.log10(intensity), cmap='inferno', extent=extent_func(intensity))

        ax.set_xlabel('Pixels')
        ax.set_ylabel('Pixels')

        # xo yo are the lower left position of the reangle
        xo = idxPeak_ij[1] - nColumns // 2 - periodHor // 2
        yo = nRows // 2 - idxPeak_ij[0] - periodVert // 2

        figure.gca().add_patch(Rectangle((xo, yo),
                               periodHor, periodVert,
                               lw=2, ls='--', color='red',
                               fill=None, alpha=1))

        ax.set_title('Selected Region ' + self.__harmonic_name, fontsize=18, weight='bold')

        ax.figure.canvas.draw()

        return figure
