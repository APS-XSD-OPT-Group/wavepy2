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
from wavepy2.util.common.common_tools import PATH_SEPARATOR

from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.plot.plot_tools import PlottingProperties

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.tools.imaging.single_grating.widgets.n_profiles_H_V_widget import NProfilesHV
from wavepy2.tools.imaging.single_grating.widgets.integrate_DPC_cumsum_widget import IntegrateDPCCumSum
from wavepy2.tools.imaging.single_grating.widgets.curv_from_height_widget import CurvFromHeight

from wavepy2.util.common.common_tools import hc

class DPCProfileAnalysisFacade():
    def dpc_profile_analysis(self, dpc_profile_analysis_data, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()

APPLICATION_NAME = "DPC Profile Analysis"

def create_dpc_profile_analsysis_manager(application_name=None):
    return __DPCProfileAnalysis(APPLICATION_NAME if application_name is None else application_name)

DPC_PROFILE_ANALYSYS_CONTEXT_KEY = "DPC Profile Analysis"

class __DPCProfileAnalysis(DPCProfileAnalysisFacade):
    def __init__(self, application_name):
        self.__main_logger   = get_registered_logger_instance(application_name=application_name)
        self.__script_logger = get_registered_secondary_logger(application_name=application_name)
        self.__plotter       = get_registered_plotter_instance(application_name=application_name)

    def dpc_profile_analysis(self, dpc_profile_analysis_data, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        phenergy          = initialization_parameters.get_parameter("phenergy")

        differential_phase_H  = dpc_profile_analysis_data.get_parameter("differential_phase_H", None)
        differential_phase_V  = dpc_profile_analysis_data.get_parameter("differential_phase_V", None)
        virtual_pixelsize     = dpc_profile_analysis_data.get_parameter("virtual_pixelsize")

        fnameH            = dpc_profile_analysis_data.get_parameter("fnameH", None)
        fnameV            = dpc_profile_analysis_data.get_parameter("fnameV", None)
        nprofiles         = dpc_profile_analysis_data.get_parameter("nprofiles", 1)
        remove1stOrderDPC = dpc_profile_analysis_data.get_parameter("remove1stOrderDPC", False)
        remove2ndOrder    = dpc_profile_analysis_data.get_parameter("remove2ndOrder", False)
        filter_width      = dpc_profile_analysis_data.get_parameter("nprofiles", 0)

        wavelength = hc/phenergy

        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(DPC_PROFILE_ANALYSYS_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        if fnameH is None: differential_phase_H = differential_phase_V*np.nan

        if fnameV is None:
            differential_phase_V = differential_phase_H*np.nan
            saveFileSuf = fnameH.rsplit(PATH_SEPARATOR, 1)[0] + PATH_SEPARATOR + 'profiles' + PATH_SEPARATOR + fnameH.rsplit(PATH_SEPARATOR, 1)[1]
            saveFileSuf = saveFileSuf.rsplit('_X')[0] + '_profiles'
        else:
            saveFileSuf = fnameV.rsplit(PATH_SEPARATOR, 1)[0] + PATH_SEPARATOR + 'profiles' + PATH_SEPARATOR + fnameV.rsplit(PATH_SEPARATOR, 1)[1]
            saveFileSuf = saveFileSuf.rsplit('_Y')[0] + '_profiles'

        if self.__plotter.is_saving() and not os.path.exists(saveFileSuf.rsplit(PATH_SEPARATOR, 1)[0]): os.makedirs(saveFileSuf.rsplit(PATH_SEPARATOR, 1)[0])

        n_profiles_H_V_result = WavePyData()

        self.__plotter.push_plot_on_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, NProfilesHV, unique_id,
                                            arrayH=differential_phase_H,
                                            arrayV=differential_phase_V,
                                            virtual_pixelsize=virtual_pixelsize,
                                            zlabel='DPC [rad/m]',
                                            titleH='WF DPC Horz',
                                            titleV='WF DPC Vert',
                                            saveFileSuf=saveFileSuf,
                                            nprofiles=nprofiles,
                                            remove1stOrderDPC=remove1stOrderDPC,
                                            filter_width=filter_width,
                                            output_data=n_profiles_H_V_result,
                                            **kwargs)

        dataH     = n_profiles_H_V_result.get_parameter("dataH")
        dataV     = n_profiles_H_V_result.get_parameter("dataV")
        labels_H  = n_profiles_H_V_result.get_parameter("labels_H")
        labels_V  = n_profiles_H_V_result.get_parameter("labels_V")
        fit_coefs = n_profiles_H_V_result.get_parameter("fit_coefs")

        fit_coefsH = np.array(fit_coefs[0])
        fit_coefsV = np.array(fit_coefs[1])

        if fnameH is not None:
            radii_fit_H = (2*np.pi/wavelength/fit_coefsH[:][0])

            self.__main_logger.print_message('Radius H from fit profiles: ')
            self.__script_logger.print('radius fit Hor = ' + str(radii_fit_H))

            integrate_dpc_cum_sum_result = WavePyData()

            self.__plotter.push_plot_on_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, IntegrateDPCCumSum, unique_id,
                                                data_DPC=dataH,
                                                wavelength=wavelength,
                                                grazing_angle=0.0, #grazing_angle,
                                                projectionFromDiv=1.0, #projectionFromDiv,
                                                remove2ndOrder=remove2ndOrder,
                                                xlabel='x',
                                                ylabel='Height',
                                                labels=labels_H,
                                                titleStr='Horizontal, ',
                                                saveFileSuf=saveFileSuf + '_X',
                                                direction="Horizontal",
                                                output_data=integrate_dpc_cum_sum_result,
                                                **kwargs)

            integratedH = integrate_dpc_cum_sum_result.get_parameter("integrated")

            curv_from_height_result = WavePyData()

            self.__plotter.push_plot_on_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, CurvFromHeight, unique_id,
                                                height=integratedH,
                                                virtual_pixelsize=virtual_pixelsize[0],
                                                grazing_angle=0.0,  # grazing_angle,
                                                projectionFromDiv=1.0,  # projectionFromDiv,
                                                xlabel='x',
                                                ylabel='Curvature',
                                                labels=labels_H,
                                                titleStr='Horizontal, ',
                                                saveFileSuf=saveFileSuf + '_X',
                                                direction="Horizontal",
                                                output_data=curv_from_height_result,
                                                **kwargs)

        if fnameV is not None:
            radii_fit_V = (2*np.pi/wavelength/fit_coefsV[:][0])

            self.__main_logger.print_message('Radius V from fit profiles: ')
            self.__script_logger.print('radius fit Vert = ' + str(radii_fit_V))

            integrate_dpc_cum_sum_result = WavePyData()

            self.__plotter.push_plot_on_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, IntegrateDPCCumSum, unique_id,
                                                data_DPC=dataV,
                                                wavelength=wavelength,
                                                grazing_angle=0.0, #grazing_angle,
                                                projectionFromDiv=1.0, #projectionFromDiv,
                                                remove2ndOrder=remove2ndOrder,
                                                xlabel='y',
                                                ylabel='Height',
                                                labels=labels_V,
                                                titleStr='Vertical, ',
                                                saveFileSuf=saveFileSuf + '_Y',
                                                direction="Vertical",
                                                output_data=integrate_dpc_cum_sum_result,
                                                **kwargs)

            integratedV = integrate_dpc_cum_sum_result.get_parameter("integrated")

            curv_from_height_result = WavePyData()

            self.__plotter.push_plot_on_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, CurvFromHeight, unique_id,
                                                height=integratedV,
                                                virtual_pixelsize=virtual_pixelsize[1],
                                                grazing_angle=0.0,  # grazing_angle,
                                                projectionFromDiv=1.0,  # projectionFromDiv,
                                                xlabel='y',
                                                ylabel='Curvature',
                                                labels=labels_V,
                                                titleStr='Vertical, ',
                                                saveFileSuf=saveFileSuf + '_Y',
                                                direction="Vertical",
                                                output_data=curv_from_height_result,
                                                **kwargs)

        self.__plotter.draw_context(DPC_PROFILE_ANALYSYS_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)
