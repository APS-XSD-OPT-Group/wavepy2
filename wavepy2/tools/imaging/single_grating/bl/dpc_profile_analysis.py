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
import os

from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core import grating_interferometry
from wavepy2.tools.imaging.single_grating.widgets.n_profiles_H_V_widget import NProfilesHV

from wavepy2.util.common.common_tools import hc

class DPCProfileAnalysisFacade():
    @classmethod
    def dpc_profile_analysis(cls, dpc_data): raise NotImplementedError()


def create_dpc_profile_analsysis_manager():
    return __DPCProfileAnalysis()

DPC_PROFILE_ANALYSYS_CONTEXT_KEY = "DPC Profile Analysis"

class __DPCProfileAnalysis(DPCProfileAnalysisFacade):
    @classmethod
    def dpc_profile_analysis(cls, dpc_profile_analysis_data, initialization_parameters):
        phenergy          = initialization_parameters.get_parameter("phenergy")

        diffPhaseH        = dpc_profile_analysis_data.get_parameter("diffPhaseH", None)
        diffPhaseV        = dpc_profile_analysis_data.get_parameter("diffPhaseV", None)
        virtual_pixelsize = dpc_profile_analysis_data.get_parameter("virtual_pixelsize")

        fnameH            = dpc_profile_analysis_data.get_parameter("fnameH", None)
        fnameV            = dpc_profile_analysis_data.get_parameter("fnameV", None)
        grazing_angle     = dpc_profile_analysis_data.get_parameter("grazing_angle", 0.0)
        projectionFromDiv = dpc_profile_analysis_data.get_parameter("projectionFromDiv", 1.0)
        nprofiles         = dpc_profile_analysis_data.get_parameter("nprofiles", 1)
        remove1stOrderDPC = dpc_profile_analysis_data.get_parameter("remove1stOrderDPC", False)
        remove2ndOrder    = dpc_profile_analysis_data.get_parameter("remove2ndOrder", False)
        filter_width      = dpc_profile_analysis_data.get_parameter("nprofiles", 0)

        wavelength = hc/phenergy

        main_logger   = get_registered_logger_instance()
        script_logger = get_registered_secondary_logger()
        plotter = get_registered_plotter_instance()

        plotter.register_context_window(DPC_PROFILE_ANALYSYS_CONTEXT_KEY)

        if fnameH is None: diffPhaseH = diffPhaseV*np.nan

        if fnameV is None:
            diffPhaseV = diffPhaseH*np.nan
            saveFileSuf = fnameH.rsplit('/', 1)[0] + '/profiles/' + fnameH.rsplit('/', 1)[1]
            saveFileSuf = saveFileSuf.rsplit('_X')[0] + '_profiles'
        else:
            saveFileSuf = fnameV.rsplit('/', 1)[0] + '/profiles/' + fnameV.rsplit('/', 1)[1]
            saveFileSuf = saveFileSuf.rsplit('_Y')[0] + '_profiles'

        if not os.path.exists(saveFileSuf.rsplit('/', 1)[0]): os.makedirs(saveFileSuf.rsplit('/', 1)[0])

        n_profiles_H_V_result = WavePyData()

        plotter.push_plot_on_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, NProfilesHV,
                                     arrayH=diffPhaseH,
                                     arrayV=diffPhaseV,
                                     virtual_pixelsize=virtual_pixelsize,
                                     zlabel='DPC [rad/m]',
                                     titleH='WF DPC Horz',
                                     titleV='WF DPC Vert',
                                     saveFileSuf=saveFileSuf,
                                     nprofiles=nprofiles,
                                     remove1stOrderDPC=remove1stOrderDPC,
                                     filter_width=filter_width,
                                     output_data=n_profiles_H_V_result)

        dataH     = n_profiles_H_V_result.get_parameter("dataH")
        dataV     = n_profiles_H_V_result.get_parameter("dataV")
        labels_H  = n_profiles_H_V_result.get_parameter("labels_H")
        labels_V  = n_profiles_H_V_result.get_parameter("labels_V")
        fit_coefs = n_profiles_H_V_result.get_parameter("fit_coefs")

        fit_coefsH = np.array(fit_coefs[0])
        fit_coefsV = np.array(fit_coefs[1])

        # TO BE REMOVED
        fnameH = None
        fnameV = None

        if fnameH is not None:
            radii_fit_H = (2*np.pi/wavelength/fit_coefsH[:][0])

            main_logger.print_message('Radius H from fit profiles: ')
            script_logger.print('radius fit Hor = ' + str(radii_fit_H))

            integratedH = cls.__integrate_DPC_cumsum(plotter,
                                                     WavePyData(data_DPC=dataH,
                                                                wavelength=wavelength,
                                                                remove2ndOrder=remove2ndOrder,
                                                                xlabel='x',
                                                                labels=labels_H,
                                                                titleStr='Horizontal, ',
                                                                saveFileSuf=saveFileSuf + '_X'))

            curv_H = cls.__curv_from_height(plotter,
                                            height=integratedH,
                                            virtual_pixelsize=virtual_pixelsize[0],
                                            xlabel='x',
                                            labels=labels_H,
                                            titleStr='Horizontal, ',
                                            saveFileSuf=saveFileSuf + '_X')

        if fnameV is not None:
            radii_fit_V = (2*np.pi/wavelength/fit_coefsV[:][0])

            main_logger.print_message('Radius V from fit profiles: ')
            script_logger.print('radius fit Vert = ' + str(radii_fit_V))

            integratedV = cls.__integrate_DPC_cumsum(plotter,
                                                     WavePyData(data_DPC=dataV,
                                                                wavelength=wavelength,
                                                                remove2ndOrder=remove2ndOrder,
                                                                xlabel='y',
                                                                labels=labels_V,
                                                                titleStr='Vertical, ',
                                                                saveFileSuf=saveFileSuf + '_Y'))

            curv_V = cls.__curv_from_height(plotter,
                                            height=integratedV,
                                            virtual_pixelsize=virtual_pixelsize[1],
                                            xlabel='y',
                                            labels=labels_V,
                                            titleStr='Vertical, ',
                                            saveFileSuf=saveFileSuf + '_Y')

        plotter.draw_context_on_widget(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, container_widget=plotter.get_context_container_widget(DPC_PROFILE_ANALYSYS_CONTEXT_KEY))


    @classmethod
    def ___integrate_DPC_cumsum(cls, plotter, integrate_DPC_cumsum_data=WavePyData()):
        data_DPC = integrate_DPC_cumsum_data.get_parameter("data_DPC")
        wavelength = integrate_DPC_cumsum_data.get_parameter("wavelength")
        remove2ndOrder = integrate_DPC_cumsum_data.get_parameter("remove2ndOrder")
        xlabel = integrate_DPC_cumsum_data.get_parameter("xlabel")
        labels = integrate_DPC_cumsum_data.get_parameter("labels")
        titleStr = integrate_DPC_cumsum_data.get_parameter("titleStr")
        saveFileSuf = integrate_DPC_cumsum_data.get_parameter("saveFileSuf")

        list_integrated = None

        return np.asarray(list_integrated).T

    @classmethod
    def ___curv_from_height(cls, plotter, curv_from_height_data=WavePyData()):
        height = curv_from_height_data.get_parameter("height")
        virtual_pixelsize = curv_from_height_data.get_parameter("virtual_pixelsize")
        xlabel = curv_from_height_data.get_parameter("xlabel")
        labels = curv_from_height_data.get_parameter("labels")
        titleStr = curv_from_height_data.get_parameter("titleStr")
        saveFileSuf = curv_from_height_data.get_parameter("saveFileSuf")

        list_curv = None

        return np.asarray(list_curv).T
