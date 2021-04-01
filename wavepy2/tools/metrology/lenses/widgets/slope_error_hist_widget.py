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
from wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches
from wavepy2.util.log.logger import get_registered_secondary_logger

from warnings import filterwarnings
filterwarnings("ignore")

class SlopeErrorHist(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(SlopeErrorHist, self).__init__(parent=parent, application_name=application_name)

        self.__script_logger  = get_registered_secondary_logger(application_name=application_name)

    def get_plot_tab_name(self): return "Slope Error"

    def build_mpl_figure(self, **kwargs):
        thickness     = kwargs["thickness"]
        pixelsize     = kwargs["pixelsize"]
        fitted        = kwargs["fitted"]
        try: delta    = kwargs["delta"]
        except: delta = 1
        try: str4title    = kwargs["str4title"]
        except: str4title = ""
        output_data = kwargs["output_data"]

        errorThickness = thickness - fitted

        fig = Figure(figsize=(15, 8))
        fig.add_subplot(121)

        slope_error_h = np.diff(errorThickness, axis=0) / pixelsize[0] * delta
        argNotNAN = np.isfinite(slope_error_h)
        factor_seh, unit_seh = common_tools.choose_unit(slope_error_h[argNotNAN])
        sigma_seh = np.std(slope_error_h[argNotNAN].flatten())

        fig.gca().hist(slope_error_h[argNotNAN].flatten() * factor_seh, 100, histtype="stepfilled")
        fig.gca().set_xlabel(r"Slope Error [$  " + unit_seh + " rad$ ]")
        fig.gca().set_title("Horizontal, SDV = {:.2f}".format(sigma_seh * factor_seh) +  " $" + unit_seh + " rad$")

        fig.add_subplot(122)

        slope_error_v = np.diff(errorThickness, axis=1) / pixelsize[1] * delta
        argNotNAN = np.isfinite(slope_error_v)
        factor_sev, unit_sev = common_tools.choose_unit(slope_error_v[argNotNAN])
        sigma_sev = np.std(slope_error_v[argNotNAN].flatten())

        fig.gca().hist(slope_error_v[argNotNAN].flatten() * factor_sev, 100, histtype="stepfilled")
        fig.gca().set_xlabel(r"Slope Error [$  " + unit_sev + " rad$ ]")
        fig.gca().set_title("Vertical, SDV = {:.2f}".format(sigma_sev * factor_sev) + " $" + unit_sev + " rad$")

        if delta != 1:  str4title += " WF slope error"
        else: str4title += " Thickness slope error"
        
        fig.suptitle(str4title, fontsize=18, weight="bold")

        self.__script_logger.print("Slope Error Hor SDV = " + "{:.3f}".format(sigma_seh * factor_seh) + unit_seh + " rad")
        self.__script_logger.print("Slope Error Ver SDV = " + "{:.3f}".format(sigma_sev * factor_sev) + unit_sev + " rad")

        output_data["sigma_seh"] = sigma_seh
        output_data["sigma_sev"] = sigma_sev

        return fig
