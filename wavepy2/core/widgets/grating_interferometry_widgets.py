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

from wavepy2.util.common.common_tools import get_idxPeak_ij, extent_func
from wavepy2.util.plot.plotter import WavePyWidget

from matplotlib.patches import Rectangle
from matplotlib.figure import Figure

class ExtractHarmonicPlot(WavePyWidget):
    def get_plot_tab_name(self):
        return "Extract Harmonic"

    def build_figure(self, **kwargs):
        intensity = kwargs["intensity"]
        idxPeak_ij = kwargs["idxPeak_ij"]
        harmonic_ij = kwargs["harmonic_ij"]
        nColumns = kwargs["nColumns"]
        nRows = kwargs["nRows"]
        periodHor = kwargs["periodHor"]
        periodVert = kwargs["periodVert"]

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

        ax.set_title('Selected Region ' + harmonic_ij[0] + harmonic_ij[1], fontsize=18, weight='bold')

        ax.figure.canvas.draw()

        return figure


class HarmonicGridPlot(WavePyWidget):
    def get_plot_tab_name(self):
        return "Harmonic Grid"

    def build_figure(self, **kwargs):
        imgFFT = kwargs["imgFFT"]
        harmonicPeriod = kwargs["harmonicPeriod"]

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
        ax.set_title('log scale FFT magnitude, Hamonics Subsets and Indexes', fontsize=16, weight='bold')

        return figure


class HarmonicPeakPlot(WavePyWidget):
    def get_plot_tab_name(self):
        return "Harmonic Peak"

    def build_figure(self, **kwargs):
        imgFFT         = kwargs["imgFFT"]
        harmonicPeriod = kwargs["harmonicPeriod"]
        fname          = kwargs["fname"]

        (nRows, nColumns) = imgFFT.shape

        periodVert = harmonicPeriod[0]
        periodHor = harmonicPeriod[1]

        # adjusts for 1D grating
        if periodVert <= 0 or periodVert is None: periodVert = nRows
        if periodHor <= 0 or periodHor is None: periodHor = nColumns

        figure = Figure(figsize=(8, 7))

        ax1 = figure.add_subplot(121)
        ax2 = figure.add_subplot(122)

        idxPeak_ij = get_idxPeak_ij(0, 1, nRows, nColumns, periodVert, periodHor)

        for i in range(-5, 5):
            ax1.plot(np.abs(imgFFT[idxPeak_ij[0] - 100 : idxPeak_ij[0] + 100, idxPeak_ij[1]-i]), lw=2, label='01 Vert ' + str(i))
        ax1.grid()

        idxPeak_ij = get_idxPeak_ij(1, 0, nRows, nColumns, periodVert, periodHor)

        for i in range(-5, 5):
            ax2.plot(np.abs(imgFFT[idxPeak_ij[0]-i, idxPeak_ij[1] - 100 : idxPeak_ij[1] + 100]), lw=2, label='10 Horz ' + str(i))
        ax2.grid()

        ax1.set_xlabel('Pixels')
        ax1.set_ylabel(r'$| FFT |$ ')
        ax1.legend(loc=1, fontsize='xx-small')
        ax1.title.set_text('Horz')

        ax2.set_xlabel('Pixels')
        ax2.set_ylabel(r'$| FFT |$ ')
        ax2.legend(loc=1, fontsize='xx-small')
        ax2.title.set_text('Vert')

        if fname is not None: figure.savefig(fname, transparent=True)

        return figure

class SingleGratingHarmonicImages(WavePyWidget):
    def get_plot_tab_name(self):
        return "Intensity in Fourier Space"

    def build_figure(self, **kwargs):
        # Intensity is Fourier Space
        intFFT00 = np.log10(np.abs(kwargs["imgFFT00"]))
        intFFT01 = np.log10(np.abs(kwargs["imgFFT01"]))
        intFFT10 = np.log10(np.abs(kwargs["imgFFT10"]))

        figure = Figure(figsize=(14, 5))
        axes = figure.subplots(nrows=1, ncols=3)

        for dat, ax, textTitle in zip([intFFT00, intFFT01, intFFT10],
                                      axes.flat,
                                      ['FFT 00', 'FFT 01', 'FFT 10']):

            # The vmin and vmax arguments specify the color limits
            im = ax.imshow(dat, cmap='inferno', vmin=np.min(intFFT00),
                           vmax=np.max(intFFT00),
                           extent=extent_func(dat))

            ax.set_title(textTitle)
            if textTitle == 'FFT 00': ax.set_ylabel('Pixels')
            ax.set_xlabel('Pixels')

        # Make an axis for the colorbar on the right side
        figure.colorbar(im, cax=figure.add_axes([0.92, 0.1, 0.03, 0.8]))
        figure.suptitle('FFT subsets - Intensity', fontsize=18, weight='bold')

        return figure
