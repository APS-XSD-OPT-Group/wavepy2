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
import sys

from wavepy2.tools.imaging.single_grating.single_grating_talbot import *

from wavepy2.util.common import common_tools
from wavepy2.util.ini.initializer import get_registered_ini_instance, register_ini_instance, IniMode
from wavepy2.util.plot.qt_application import get_registered_qt_application_instance, register_qt_application_instance, QtApplicationMode
from wavepy2.util.log.logger import register_logger_single_instance, register_secondary_logger, LoggerMode
from wavepy2.util.plot.plotter import get_registered_plotter_instance, register_plotter_instance, PlotterMode

MAIN_LOGGER_MODE   = LoggerMode.FULL
SCRIPT_LOGGER_MODE = LoggerMode.FULL

INI_MODE      = IniMode.LOCAL_FILE
INI_FILE_NAME = ".single_grating_talbot.ini"
PLOTTER_MODE  = PlotterMode.DISPLAY_ONLY

if __name__=="__main__":
    # ==========================================================================
    # %% Script initialization
    # ==========================================================================

    register_logger_single_instance(logger_mode=MAIN_LOGGER_MODE)
    register_ini_instance(INI_MODE, ini_file_name=".single_grating_talbot.ini" if INI_MODE == IniMode.LOCAL_FILE else None)
    register_plotter_instance(plotter_mode=PLOTTER_MODE)
    register_qt_application_instance(QtApplicationMode.QT if PLOTTER_MODE in [PlotterMode.FULL, PlotterMode.DISPLAY_ONLY, PlotterMode.SAVE_ONLY] else QtApplicationMode.NONE)

    # ==========================================================================
    # %% Initialization parameters
    # ==========================================================================

    initialization_parameters = get_initialization_parameters()

    plotter = get_registered_plotter_instance()

    register_secondary_logger(stream=open(plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt"),
                              logger_mode=SCRIPT_LOGGER_MODE)

    # ==========================================================================
    # %% Main
    # ==========================================================================

    dpc_result = calculate_dpc(initialization_parameters)
    plotter.show_context_window(CALCULATE_DPC_CONTEXT_KEY)

    # ==========================================================================

    recrop_dpc_result = recrop_dpc(dpc_result, initialization_parameters)
    plotter.show_context_window(RECROP_DPC_CONTEXT_KEY)

    # ==========================================================================

    correct_zero_dpc_result = correct_zero_dpc(recrop_dpc_result, initialization_parameters)
    plotter.show_context_window(CORRECT_ZERO_DPC)

    # ==========================================================================

    remove_linear_fit_result = remove_linear_fit(correct_zero_dpc_result, initialization_parameters)
    plotter.show_context_window(REMOVE_LINEAR_FIT)

    # integration

    get_registered_ini_instance().push()

    get_registered_qt_application_instance().run_qt_application()
