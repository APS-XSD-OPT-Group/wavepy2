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
from wavepy2.util.common.common_tools import extent_func, is_empty_string
from wavepy2.util.plot.plotter import WavePyWidget

class SingleGratingHarmonicImages(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return self.__image_name + "Intensity in Fourier Space"

    def build_mpl_figure(self, **kwargs):
        # Intensity is Fourier Space
        intFFT00 = np.log10(np.abs(kwargs["imgFFT00"]))
        intFFT01 = np.log10(np.abs(kwargs["imgFFT01"]))
        intFFT10 = np.log10(np.abs(kwargs["imgFFT10"]))
        image_name = kwargs["image_name"]

        self.__image_name = "" if is_empty_string(image_name) else image_name + ": "

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
