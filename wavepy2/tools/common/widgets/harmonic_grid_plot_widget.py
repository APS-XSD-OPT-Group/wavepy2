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
from wavepy2.util.common.common_tools import extent_func, get_idxPeak_ij, is_empty_string
from wavepy2.util.plot.plotter import WavePyWidget


class HarmonicGridPlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return self.__image_name + "Harmonic Grid"

    def build_mpl_figure(self, **kwargs):
        imgFFT         = kwargs["imgFFT"]
        harmonicPeriod = kwargs["harmonicPeriod"]
        image_name     = kwargs["image_name"]

        self.__image_name = "" if is_empty_string(image_name) else image_name + ": "

        (nRows, nColumns) = imgFFT.shape

        periodVert = harmonicPeriod[0]
        periodHor = harmonicPeriod[1]

        # adjusts for 1D grating
        if periodVert <= 0 or periodVert is None: periodVert = nRows
        if periodHor <= 0 or periodHor is None: periodHor = nColumns

        figure = Figure(figsize=(8, 7))
        ax = figure.subplots(1, 1)
        ax.imshow(np.log10(np.abs(imgFFT)), cmap='inferno',
                   extent=extent_func(imgFFT))

        ax.set_xlabel('Pixels')
        ax.set_ylabel('Pixels')

        harV_min = -(nRows + 1) // 2 // periodVert
        harV_max = (nRows + 1) // 2 // periodVert

        harH_min = -(nColumns + 1) // 2 // periodHor
        harH_max = (nColumns + 1) // 2 // periodHor

        for harV in range(harV_min + 1, harV_max + 2):
            idxPeak_ij = get_idxPeak_ij(harV, 0, nRows, nColumns, periodVert, periodHor)
            ax.axhline(idxPeak_ij[0] - periodVert//2 - nRows//2, lw=2, color='r')

        for harH in range(harH_min + 1, harH_max + 2):
            idxPeak_ij = get_idxPeak_ij(0, harH, nRows, nColumns, periodVert, periodHor)
            ax.axvline(idxPeak_ij[1] - periodHor // 2 - nColumns//2, lw=2, color='r')

        for harV in range(harV_min, harV_max + 1):
            for harH in range(harH_min, harH_max + 1):
                idxPeak_ij = get_idxPeak_ij(harV, harH, nRows, nColumns, periodVert, periodHor)
                ax.plot(idxPeak_ij[1] - nColumns//2, idxPeak_ij[0] - nRows//2, 'ko', mew=2, mfc="None", ms=15)
                ax.annotate('{:d}{:d}'.format(-harV, harH), (idxPeak_ij[1] - nColumns//2, idxPeak_ij[0] - nRows//2,), color='red', fontsize=20)

        ax.set_xlim(-nColumns//2, nColumns - nColumns//2)
        ax.set_ylim(-nRows//2, nRows - nRows//2)
        ax.set_title('log scale FFT magnitude, Harmonics Subsets and Indexes', fontsize=16, weight='bold')

        return figure
