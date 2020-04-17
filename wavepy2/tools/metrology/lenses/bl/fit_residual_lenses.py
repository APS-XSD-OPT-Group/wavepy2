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

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.core.widgets.plot_profile_widget import PlotProfile
from wavepy2.tools.common.physical_properties import get_delta
from wavepy2.tools.common.widgets.colorbar_crop_dialog_widget import ColorbarCropDialogPlot
from wavepy2.tools.common.widgets.show_cropped_figure_widget import ShowCroppedFigure

from wavepy2.tools.metrology.lenses.widgets.frl_input_parameters_widget import FRLInputParametersWidget, generate_initialization_parameters_frl, LENS_GEOMETRIES

class FitResidualLensesFacade:
    def get_initialization_parameters(self, script_logger_mode): raise NotImplementedError()

def create_fit_residual_lenses_manager():
    return __FitResidualLenses()

CROP_THICKNESS_CONTEXT_KEY = "Crop and Show Thickness"

class __FitResidualLenses(FitResidualLensesFacade):

    def __init__(self):
        self.__plotter     = get_registered_plotter_instance()
        self.__main_logger = get_registered_logger_instance()
        self.__ini         = get_registered_ini_instance()

    # %% ==================================================================================================

    def get_initialization_parameters(self, script_logger_mode):
        if self.__plotter.is_active():
            initialization_parameters = self.__plotter.show_interactive_plot(FRLInputParametersWidget, container_widget=None)
        else:
            initialization_parameters = generate_initialization_parameters_frl(thickness_file_name=self.__ini.get_string_from_ini("Files", "file with thickness"),
                                                                               str4title=self.__ini.get_string_from_ini("Parameters", "String for Titles", default="Be Lens"),
                                                                               nominalRadius=self.__ini.get_float_from_ini("Parameters", "nominal radius for fitting", default=1e-4),
                                                                               diameter4fit_str=self.__ini.get_string_from_ini("Parameters", "diameter of active area for fitting", default="800"),
                                                                               lensGeometry=self.__ini.get_string_from_ini("Parameters", "lens geometry", default=LENS_GEOMETRIES[2]))

        plotter = get_registered_plotter_instance()
        plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode)

        self.__script_logger = get_registered_secondary_logger()

        return initialization_parameters

    def crop_thickness(self, initialization_parameters):
        self.__plotter.register_context_window(CROP_THICKNESS_CONTEXT_KEY)

        thickness = initialization_parameters.get_parameter("thickness")
        xx = initialization_parameters.get_parameter("xx")
        yy = initialization_parameters.get_parameter("yy")

        thickness_temp = np.copy(thickness)
        thickness_temp[np.isnan(thickness)] = 0.0

        if self.__plotter.is_active(): _, idx4crop = self.__plotter.show_interactive_plot(CropDialogPlot, container_widget=None, img=thickness_temp*1e6)
        else: idx4crop = [0, -1, 0, -1]

        thickness = common_tools.crop_matrix_at_indexes(thickness, idx4crop)
        xx = common_tools.crop_matrix_at_indexes(xx, idx4crop)
        yy = common_tools.crop_matrix_at_indexes(yy, idx4crop)

        stride = thickness.shape[0] // 125

        self.__plotter.push_plot_on_context(CROP_THICKNESS_CONTEXT_KEY, PlotProfile,
                                            xmatrix=xx[::stride, ::stride] * 1e6,
                                            ymatrix=yy[::stride, ::stride] * 1e6,
                                            zmatrix=thickness[::stride, ::stride] * 1e6,
                                            xlabel=r'$x$ [$\mu m$ ]',
                                            ylabel=r'$y$ [$\mu m$ ]',
                                            zlabel=r'$z$ [$\mu m$ ]',
                                            arg4main={'cmap': 'Spectral_r'})

        self.__draw_context(CROP_THICKNESS_CONTEXT_KEY)

        return WavePyData(thickness=thickness, xx=xx, yy=yy)

    ###################################################################
    # PRIVATE METHODS

    def __draw_context(self, context_key):
        self.__plotter.draw_context_on_widget(context_key, container_widget=self.__plotter.get_context_container_widget(context_key))
