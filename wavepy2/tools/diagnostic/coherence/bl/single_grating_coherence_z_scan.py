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

from wavepy2.util.common import common_tools
from wavepy2.util.common.common_tools import hc
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger, register_secondary_logger, LoggerMode

from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.diagnostic.coherence.widgets.sgz_input_parameters_widget import SGZInputParametersWidget, generate_initialization_parameters_sgz

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core import grating_interferometry

class SingleGratingCoherenceZScanFacade:
    def get_initialization_parameters(self, script_logger_mode): raise NotImplementedError()
    def calculate_harmonic_periods(self, initialization_parameters): raise NotImplementedError()

def create_single_grating_coherence_z_scan_manager():
    return __SingleGratingCoherenceZScan()

class __SingleGratingCoherenceZScan(SingleGratingCoherenceZScanFacade):

    def __init__(self):
        self.__plotter     = get_registered_plotter_instance()
        self.__main_logger = get_registered_logger_instance()
        self.__ini         = get_registered_ini_instance()

    def get_initialization_parameters(self, script_logger_mode):
        if self.__plotter.is_active():
            initialization_parameters = self.__plotter.show_interactive_plot(SGZInputParametersWidget, container_widget=None)
        else:
            initialization_parameters = generate_initialization_parameters_sgz(dataFolder         = self.__ini.get_string_from_ini("Files", "data directory"),
                                                                               samplefileName     = self.__ini.get_string_from_ini("Files", "sample file name"),
                                                                               zvec_from          = self.__ini.get_string_from_ini("Parameters", "z distances from", default="Calculated"),
                                                                               startDist          = self.__ini.get_float_from_ini("Parameters", "starting distance scan", default=20*1e-3),
                                                                               step_z_scan        = self.__ini.get_float_from_ini("Parameters", "step size scan", default=5*1e-3),
                                                                               image_per_point    = self.__ini.get_int_from_ini("Parameters", "number of images per step", default=1),
                                                                               strideFile         = self.__ini.get_int_from_ini("Parameters", "stride", default=1),
                                                                               zvec_file          = self.__ini.get_string_from_ini("Parameters", "z distances file"),
                                                                               pixelSize          = self.__ini.get_float_from_ini("Parameters", "pixel size", default=6.5e-07),
                                                                               gratingPeriod      = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period", default=4.8e-06),
                                                                               pattern            = self.__ini.get_string_from_ini("Parameters", "pattern", default="Diagonal"),
                                                                               sourceDistanceV    = self.__ini.get_float_from_ini("Parameters", "source distance v", default=-0.73),
                                                                               sourceDistanceH    = self.__ini.get_float_from_ini("Parameters", "source distance h", default=34.0),
                                                                               unFilterSize       = self.__ini.get_int_from_ini("Parameters", "size for uniform filter", default=1),
                                                                               searchRegion       = self.__ini.get_int_from_ini("Parameters", "size for region for searching", default=1))

        plotter = get_registered_plotter_instance()
        plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode)

        self.__script_logger = get_registered_secondary_logger()

        return initialization_parameters
