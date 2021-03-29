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


from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import LoggerMode
from wavepy2.util.plot.qt_application import get_registered_qt_application_instance
from wavepy2.util.plot.plotter import get_registered_plotter_instance

from wavepy2.tools.common.wavepy_script import WavePyScript

from wavepy2.tools.metrology.lenses.bl.fit_residual_lenses import create_fit_residual_lenses_manager, APPLICATION_NAME, \
    CROP_THICKNESS_CONTEXT_KEY, CENTER_IMAGE_CONTEXT_KEY, FIT_RADIUS_DPC_CONTEXT_KEY, DO_FIT_CONTEXT_KEY

class MainFitResidualLenses(WavePyScript):
    SCRIPT_ID = "met-frl"

    def _get_script_id(self): return MainFitResidualLenses.SCRIPT_ID
    def _get_application_name(self): return APPLICATION_NAME
    def _get_ini_file_name(self): return ".fit_residual_lenses.ini"

    def _run_script(self, SCRIPT_LOGGER_MODE=LoggerMode.FULL, **args):
        plotter = get_registered_plotter_instance(application_name=self._get_application_name())

        fit_residual_lenses_manager = create_fit_residual_lenses_manager()

        # ==========================================================================
        # %% Initialization parameters
        # ==========================================================================

        initialization_parameters = fit_residual_lenses_manager.manager_initialization(fit_residual_lenses_manager.get_initialization_parameters(),
                                                                                       SCRIPT_LOGGER_MODE)

        crop_result = fit_residual_lenses_manager.crop_thickness(initialization_parameters)
        plotter.show_context_window(CROP_THICKNESS_CONTEXT_KEY)

        center_image_result = fit_residual_lenses_manager.center_image(crop_result, initialization_parameters)
        plotter.show_context_window(CENTER_IMAGE_CONTEXT_KEY)

        fit_radius_dpc_result = fit_residual_lenses_manager.fit_radius_dpc(center_image_result, initialization_parameters)
        plotter.show_context_window(FIT_RADIUS_DPC_CONTEXT_KEY)

        fit_result = fit_residual_lenses_manager.do_fit(fit_radius_dpc_result, initialization_parameters)
        plotter.show_context_window(DO_FIT_CONTEXT_KEY)


        # ==========================================================================
        # %% Final Operations
        # ==========================================================================

        get_registered_ini_instance(self._get_application_name()).push()
        get_registered_qt_application_instance().show_application_closer()

        # ==========================================================================

        get_registered_qt_application_instance().run_qt_application()


import os, sys
if __name__=="__main__":
    if os.getenv('WAVEPY_DEBUG', "0") == "1": MainFitResidualLenses(sys_argv=sys.argv).run_script()
    else: MainFitResidualLenses().show_help()
