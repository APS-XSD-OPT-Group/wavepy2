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

from wavepy2.tools.imaging.single_grating.bl.single_grating_talbot import create_single_grating_talbot_manager, \
    CALCULATE_DPC_CONTEXT_KEY, CORRECT_ZERO_DPC_CONTEXT_KEY, RECROP_DPC_CONTEXT_KEY, REMOVE_LINEAR_FIT_CONTEXT_KEY, FIT_RADIUS_DPC_CONTEXT_KEY, \
    INTEGRATION_CONTEXT_KEY, CALCULATE_THICKNESS_CONTEXT_KEY, CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE, REMOVE_2ND_ORDER

from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import LoggerMode
from wavepy2.util.plot.qt_application import get_registered_qt_application_instance
from wavepy2.util.plot.plotter import get_registered_plotter_instance

from wavepy2.tools.common.wavepy_script import WavePyScript

class MainSingleGratingCoherenceZScan(WavePyScript):

    def get_script_id(self): return "coh-sgz"
    def get_ini_file_name(self): return ".single_grating_coherence_z_scan.ini"

    def _run_script(self, SCRIPT_LOGGER_MODE=LoggerMode.FULL):
        plotter = get_registered_plotter_instance()

        single_grating_coherence_z_scan_manager = create_single_grating_coherence_z_scan_manager()

        # ==========================================================================
        # %% Initialization parameters
        # ==========================================================================

        initialization_parameters = single_grating_coherence_z_scan_manager.get_initialization_parameters(SCRIPT_LOGGER_MODE)

        # ==========================================================================
        # %%
        # ==========================================================================

        #dpc_result = single_grating_talbot_manager.calculate_dpc(initialization_parameters)
        #plotter.show_context_window(CALCULATE_DPC_CONTEXT_KEY)

        # ==========================================================================


        # ==========================================================================
        # %%
        # ==========================================================================


        # ==========================================================================
        # %% Final Operations
        # ==========================================================================

        get_registered_ini_instance().push()
        get_registered_qt_application_instance().show_application_closer()

        # ==========================================================================

        get_registered_qt_application_instance().run_qt_application()

if __name__=="__main__":
    MainSingleGratingCoherenceZScan([]).show_help()