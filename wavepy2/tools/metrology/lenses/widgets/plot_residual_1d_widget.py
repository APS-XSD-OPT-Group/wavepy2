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
from wavepy2.util.plot.plotter import get_registered_plotter_instance

from warnings import filterwarnings
filterwarnings("ignore")

class PlotResidual1D(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(PlotResidual1D, self).__init__(parent=parent, application_name=application_name)

        self.__logger   = get_registered_logger_instance(application_name=application_name)
        self.__plotter  = get_registered_plotter_instance(application_name=application_name)

    def get_plot_tab_name(self): return "Fit center profile " + self.__direction

    def build_mpl_figure(self, **kwargs):
        xvec              = kwargs["xvec"]
        data              = kwargs["data"]
        fitted            = kwargs["fitted"]
        self.__direction  = kwargs["direction"]
        str4title         = kwargs["str4title"]
        try:    saveAscii = kwargs["saveAscii"]
        except: saveAscii = False

        errorThickness = -data + fitted
        argNotNAN = np.isfinite(errorThickness)

        factorx, unitx = common_tools.choose_unit(xvec)
        factory1, unity1 = common_tools.choose_unit(data)
        factory2, unity2 = common_tools.choose_unit(errorThickness)

        ptp        = np.ptp(errorThickness[argNotNAN].flatten() * factory2)
        sigmaError = np.std(errorThickness[argNotNAN].flatten() * factory2)

        self.__logger.print_message("PV: {0:4.3g} ".format(ptp) + unity2[-1] + "m")
        self.__logger.print_message("SDV: {0:4.3g} ".format(sigmaError) + unity2[-1] + "m")

        str4title += "\n" + r"PV $= {0:.2f}$ ".format(ptp) + "$" + unity2 + "  m$, SDV $= {0:.2f}$ ".format(sigmaError) + "$" + unity2 + "  m$"

        fig = Figure(figsize=(10, 7))
        ax1 = fig.gca()
        ax1.plot(xvec[argNotNAN] * factorx, data[argNotNAN] * factory1,   "-ko", markersize=5, label="1D data")
        ax1.plot(xvec[argNotNAN] * factorx, fitted[argNotNAN] * factory1, "-+r", label="Fit parabolic")

        ax2 = ax1.twinx()

        # trick to add both axes to legend
        ax2.plot(np.nan, "-ko", label="1D data")
        ax2.plot(np.nan, "-+r", label="Fit parabolic")

        ax2.plot(xvec[argNotNAN] * factorx, errorThickness[argNotNAN] * factory2, "-+", markersize=5, label="fit residual")

        fig.gca().set_title(str4title)

        for tl in ax2.get_yticklabels(): tl.set_color("b")

        ax2.legend(loc=1, fontsize="small")

        ax1.grid(color="gray")
        ax1.set_xlabel(r"[$" + unitx + " m$]")
        ax1.set_ylabel(r"Thickness " + r"[$" + unity1 + " m$]")

        ax2.set_ylim(-1.1 * np.max(np.abs(errorThickness[argNotNAN]) * factory2), 1.1 * np.max(np.abs(errorThickness[argNotNAN]) * factory2))
        ax2.set_ylabel(r"Residual" + r"[$" + unity2 + " m$]")
        ax2.grid(b="off")
        fig.gca().set_xlim(-1.1 * np.max(xvec * factorx), 1.1 * np.max(xvec * factorx))

        fig.tight_layout(rect=(0, 0, 1, .98))

        if saveAscii:
            np.savetxt(common_tools.get_unique_filename(self.__plotter.get_save_file_prefix(), "csv"),
                       np.transpose([xvec, data, fitted, fitted - data]),
                       delimiter=",\t",
                       header="xvec, data, fitted, residual, " + str4title,
                       fmt="%.6g")

        return fig
