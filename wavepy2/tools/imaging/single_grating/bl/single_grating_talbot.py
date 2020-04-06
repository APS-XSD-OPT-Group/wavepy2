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

from wavepy2.core import grating_interferometry
from wavepy2.core.widgets.plot_intensities_harms_widget import PlotIntensitiesHarms
from wavepy2.core.widgets.plot_dark_field_widget import PlotDarkField
from wavepy2.core.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.core.widgets.plot_integration_widget import PlotIntegration
from wavepy2.tools.common.physical_properties import get_delta
from wavepy2.tools.imaging.single_grating.widgets.plot_DPC_widget import PlotDPC
from wavepy2.tools.imaging.single_grating.widgets.input_parameters_widget import InputParametersWidget, generate_initialization_parameters
from wavepy2.tools.imaging.single_grating.widgets.first_crop_dialog_widget import FirstCropDialogPlot
from wavepy2.tools.imaging.single_grating.widgets.show_cropped_figure_widget import ShowCroppedFigure
from wavepy2.tools.imaging.single_grating.widgets.correct_DPC_widgets import CorrectDPC, CorrectDPCHistos, CorrectDPCCenter
from wavepy2.tools.imaging.single_grating.widgets.fit_radius_dpc_widget import FitRadiusDPC

from wavepy2.tools.imaging.single_grating.bl.dpc_profile_analysis import create_dpc_profile_analsysis_manager


CALCULATE_DPC_CONTEXT_KEY                  = "Calculate DPC"
RECROP_DPC_CONTEXT_KEY                     = "Recrop DPC"
CORRECT_ZERO_DPC_CONTEXT_KEY               = "Correct Zero DPC"
REMOVE_LINEAR_FIT_CONTEXT_KEY              = "Remove Linear Fit"
FIT_RADIUS_DPC_CONTEXT_KEY                 = "Fit Radius DPC"
INTEGRATION_CONTEXT_KEY                    = "Integration"
CALCULATE_THICKNESS_CONTEXT_KEY            = "Calculate Thickness"
CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE = "Calculate 2nd order component of the phase"
REMOVE_2ND_ORDER                           = "Remove 2nd order"

class SingleGratingTalbotFacade:
    def get_initialization_parameters(self, script_logger_mode): raise NotImplementedError()
    def calculate_dpc(self, initialization_parameters): raise NotImplementedError()
    def recrop_dpc(self, dpc_result, initialization_parameters): raise NotImplementedError()
    def correct_zero_dpc(self, dpc_result, initialization_parameters): raise NotImplementedError()
    def remove_linear_fit(self, correct_zero_dpc_result, initialization_parameters): raise NotImplementedError()
    def dpc_profile_analysis(self, remove_linear_fit_result, initialization_parameters): raise NotImplementedError()
    def fit_radius_dpc(self, correct_zero_dpc_result, initialization_parameters): raise NotImplementedError()
    def do_integration(self, fit_radius_dpc_result, initialization_parameters): raise NotImplementedError()
    def calc_thickness(self, integration_result, initialization_parameters): raise NotImplementedError()
    def calc_2nd_order_component_of_the_phase(self, integration_result, initialization_parameters): raise NotImplementedError()
    def remove_2nd_order(self, integration_result, initialization_parameters): raise NotImplementedError()

def create_single_grating_talbot_manager():
    return __SingleGratingTalbot()

class __SingleGratingTalbot(SingleGratingTalbotFacade):

    def __init__(self):
        self.__plotter     = get_registered_plotter_instance()
        self.__main_logger = get_registered_logger_instance()
        self.__ini         = get_registered_ini_instance()

    # %% ==================================================================================================

    def get_initialization_parameters(self, script_logger_mode):
        if self.__plotter.is_active():
            initialization_parameters = self.__plotter.show_interactive_plot(InputParametersWidget, container_widget=None)
        else:
            initialization_parameters = generate_initialization_parameters(img_file_name      = self.__ini.get_string_from_ini("Files", "sample"),
                                                                           imgRef_file_name   = self.__ini.get_string_from_ini("Files", "reference"),
                                                                           imgBlank_file_name = self.__ini.get_string_from_ini("Files", "blank"),
                                                                           mode               = self.__ini.get_string_from_ini("Parameters", "mode", default="Relative"),
                                                                           pixel              = self.__ini.get_float_from_ini("Parameters", "pixel size", default=6.5e-07),
                                                                           gratingPeriod      = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period", default=4.8e-06),
                                                                           pattern            = self.__ini.get_string_from_ini("Parameters", "pattern", default="Diagonal half pi"),
                                                                           distDet2sample     = self.__ini.get_float_from_ini("Parameters", "distance detector to gr", default=0.33),
                                                                           phenergy           = self.__ini.get_float_from_ini("Parameters", "photon energy", default=14000.0),
                                                                           sourceDistance     = self.__ini.get_float_from_ini("Parameters", "source distance", default=32.0),
                                                                           correct_pi_jump    = self.__ini.get_boolean_from_ini("Runtime", "correct pi jump", default=False),
                                                                           remove_mean        = self.__ini.get_boolean_from_ini("Runtime", "remove mean", default=False),
                                                                           correct_dpc_center = self.__ini.get_boolean_from_ini("Runtime", "correct dpc center", default=False),
                                                                           remove_linear      = self.__ini.get_boolean_from_ini("Runtime", "remove linear", default=False),
                                                                           do_integration     = self.__ini.get_boolean_from_ini("Runtime", "do integration", default=False),
                                                                           calc_thickness     = self.__ini.get_boolean_from_ini("Runtime", "calc thickness", default=False),
                                                                           remove_2nd_order   = self.__ini.get_boolean_from_ini("Runtime", "remove 2nd order", default=False),
                                                                           material_idx       = self.__ini.get_int_from_ini("Runtime", "material idx", default=0))

        plotter = get_registered_plotter_instance()
        plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode)

        self.__wavelength = hc / initialization_parameters.get_parameter("phenergy")
        self.__kwave = 2 * np.pi / self.__wavelength

        self.__script_logger                = get_registered_secondary_logger()
        self.__dpc_profile_analysis_manager = create_dpc_profile_analsysis_manager()

        return initialization_parameters

    # %% ==================================================================================================

    def calculate_dpc(self, initialization_parameters):
        img             = initialization_parameters.get_parameter("img")
        imgRef          = initialization_parameters.get_parameter("imgRef")
        phenergy        = initialization_parameters.get_parameter("phenergy")
        pixelsize       = initialization_parameters.get_parameter("pixelsize")
        distDet2sample  = initialization_parameters.get_parameter("distDet2sample")
        period_harm     = initialization_parameters.get_parameter("period_harm")
        unwrapFlag      = True

        self.__plotter.register_context_window(CALCULATE_DPC_CONTEXT_KEY)

        img_size_o = np.shape(img)

        if self.__plotter.is_active():
            img, idx4crop = self.__plotter.show_interactive_plot(FirstCropDialogPlot, container_widget=None, img=img, pixelsize=pixelsize)
        else:
            idx4crop = self.__ini.get_list_from_ini("Parameters", "Crop")
            img = common_tools.crop_matrix_at_indexes(img, idx4crop)

        # Plot Real Image AFTER crop
        self.__plotter.push_plot_on_context(CALCULATE_DPC_CONTEXT_KEY, ShowCroppedFigure, img=img, pixelsize=pixelsize)

        if not imgRef is None: imgRef = common_tools.crop_matrix_at_indexes(imgRef, idx4crop)

        period_harm_Vert_o = int(period_harm[0]*img.shape[0]/img_size_o[0]) + 1
        period_harm_Hor_o = int(period_harm[1]*img.shape[1]/img_size_o[1]) + 1

        # Obtain harmonic periods from images

        if imgRef is None:
            harmPeriod = [period_harm_Vert_o, period_harm_Hor_o]
        else:
            self.__main_logger.print_message('Obtain harmonic 01 experimentally')

            (_, period_harm_Hor) = grating_interferometry.exp_harm_period(imgRef, [period_harm_Vert_o, period_harm_Hor_o],
                                                                          harmonic_ij=['0', '1'],
                                                                          searchRegion=30,
                                                                          isFFT=False)

            self.__main_logger.print_message('MESSAGE: Obtain harmonic 10 experimentally')

            (period_harm_Vert, _) = grating_interferometry.exp_harm_period(imgRef, [period_harm_Vert_o, period_harm_Hor_o],
                                                                           harmonic_ij=['1', '0'],
                                                                           searchRegion=30,
                                                                           isFFT=False)

            harmPeriod = [period_harm_Vert, period_harm_Hor]

        # Calculate everything

        [int00, int01, int10,
         darkField01, darkField10,
         phaseFFT_01,
         phaseFFT_10] = grating_interferometry.single_2Dgrating_analyses(img,
                                                                         img_ref=imgRef,
                                                                         harmonicPeriod=harmPeriod,
                                                                         unwrapFlag=unwrapFlag,
                                                                         context_key=CALCULATE_DPC_CONTEXT_KEY)

        virtual_pixelsize = [0, 0]
        virtual_pixelsize[0] = pixelsize[0]*img.shape[0]/int00.shape[0]
        virtual_pixelsize[1] = pixelsize[1]*img.shape[1]/int00.shape[1]

        diffPhase01 = -phaseFFT_01*virtual_pixelsize[1]/distDet2sample/hc*phenergy
        diffPhase10 = -phaseFFT_10*virtual_pixelsize[0]/distDet2sample/hc*phenergy
        # Note: the signals above were defined base in experimental data

        self.__draw_context(CALCULATE_DPC_CONTEXT_KEY)

        self.__main_logger.print_message('VALUES: virtual pixelsize i, j: {:.4f}um, {:.4f}um'.format(virtual_pixelsize[0]*1e6, virtual_pixelsize[1]*1e6))
        self.__script_logger.print('\nvirtual_pixelsize = ' + str(virtual_pixelsize))

        self.__main_logger.print_message('wavelength [m] = ' + str('{:.5g}'.format(self.__wavelength)))
        self.__script_logger.print('wavelength [m] = ' + str('{:.5g}'.format(self.__wavelength)))

        lengthSensitivy100 = virtual_pixelsize[0]**2/distDet2sample/100

        # the 100 means that I arbitrarylly assumed the angular error in
        #  fringe displacement to be 2pi/100 = 3.6 deg

        self.__main_logger.print_message('WF Length Sensitivy 100 [m] = ' + str('{:.5g}'.format(lengthSensitivy100)))
        self.__main_logger.print_message('WF Length Sensitivy 100 [1/lambda] = ' + str('{:.5g}'.format(lengthSensitivy100/self.__wavelength)) + '\n')

        self.__script_logger.print('WF Length Sensitivy 100 [m] = ' + str('{:.5g}'.format(lengthSensitivy100)))
        self.__script_logger.print('WF Length Sensitivy 100 [1/lambda] = ' + str('{:.5g}'.format(lengthSensitivy100/self.__wavelength)) + '\n')

        return WavePyData(int00=int00,
                          int01=int01,
                          int10=int10,
                          darkField01=darkField01,
                          darkField10=darkField10,
                          diffPhase01=diffPhase01,
                          diffPhase10=diffPhase10,
                          virtual_pixelsize=virtual_pixelsize)

    # %% ==================================================================================================

    def recrop_dpc(self, dpc_result, initialization_parameters):
        img             = initialization_parameters.get_parameter("img")
        imgRef          = initialization_parameters.get_parameter("imgRef")
        pixelsize       = initialization_parameters.get_parameter("pixelsize")

        int00             = dpc_result.get_parameter("int00")
        int01             = dpc_result.get_parameter("int01")
        int10             = dpc_result.get_parameter("int10")
        darkField01       = dpc_result.get_parameter("darkField01")
        darkField10       = dpc_result.get_parameter("darkField10")
        diffPhase01       = dpc_result.get_parameter("diffPhase01")
        diffPhase10       = dpc_result.get_parameter("diffPhase10")
        virtual_pixelsize = dpc_result.get_parameter("virtual_pixelsize")

        self.__plotter.register_context_window(RECROP_DPC_CONTEXT_KEY)

        img_to_crop = np.sqrt((diffPhase01 - diffPhase01.mean())**2 + (diffPhase10 - diffPhase10.mean())**2)

        if self.__plotter.is_active(): _, idx2ndCrop = self.__plotter.show_interactive_plot(CropDialogPlot, container_widget=None, img=img_to_crop, pixelsize=pixelsize)
        else: idx2ndCrop = [0, -1, 0, -1] #self.__ini.get_list_from_ini("Parameters", "Crop")

        if idx2ndCrop != [0, -1, 0, -1]:
            int00       = common_tools.crop_matrix_at_indexes(int00, idx2ndCrop)
            int01       = common_tools.crop_matrix_at_indexes(int01, idx2ndCrop)
            int10       = common_tools.crop_matrix_at_indexes(int10, idx2ndCrop)
            darkField01 = common_tools.crop_matrix_at_indexes(darkField01, idx2ndCrop)
            darkField10 = common_tools.crop_matrix_at_indexes(darkField10, idx2ndCrop)
            diffPhase01 = common_tools.crop_matrix_at_indexes(diffPhase01, idx2ndCrop)
            diffPhase10 = common_tools.crop_matrix_at_indexes(diffPhase10, idx2ndCrop)

            factor_i = virtual_pixelsize[0]/pixelsize[0]
            factor_j = virtual_pixelsize[1]/pixelsize[1]

            idx1stCrop = self.__ini.get_list_from_ini("Parameters", "Crop")

            idx4crop = [0, -1, 0, -1]
            idx4crop[0] = int(np.rint(idx1stCrop[0] + idx2ndCrop[0]*factor_i))
            idx4crop[1] = int(np.rint(idx1stCrop[0] + idx2ndCrop[1]*factor_i))
            idx4crop[2] = int(np.rint(idx1stCrop[2] + idx2ndCrop[2]*factor_j))
            idx4crop[3] = int(np.rint(idx1stCrop[2] + idx2ndCrop[3]*factor_j))

            self.__main_logger.print('New Crop: {}, {}, {}, {}'.format(idx4crop[0], idx4crop[1], idx4crop[2], idx4crop[3]))

            self.__ini.set_list_at_ini("Parameters", "Crop", idx4crop)

            # Plot Real Image AFTER crop
            self.__plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, ShowCroppedFigure, img=common_tools.crop_matrix_at_indexes(img, idx4crop), pixelsize=pixelsize, title="Raw Image with 2nd Crop")

            self.__ini.push()

        if not imgRef is None:
            self.__plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, PlotIntensitiesHarms, int00=int00, int01=int01, int10=int10, pixelsize=virtual_pixelsize, titleStr='Intensity')
            self.__plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, PlotDarkField, darkField01=darkField01, darkField10=darkField10, pixelsize=virtual_pixelsize)
            self.__plotter.save_sdf_file(int00, virtual_pixelsize, file_suffix="_intensity", extraHeader={'Title': 'Intensity', 'Zunit': 'au'})

        self.__plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, PlotDPC, dpc01=diffPhase01, dpc10=diffPhase10, pixelsize=virtual_pixelsize, titleStr="")

        self.__draw_context(RECROP_DPC_CONTEXT_KEY)

        return WavePyData(int00=int00,
                          int01=int01,
                          int10=int10,
                          darkField01=darkField01,
                          darkField10=darkField10,
                          diffPhase01=diffPhase01,
                          diffPhase10=diffPhase10,
                          virtual_pixelsize=virtual_pixelsize)

    # %% ==================================================================================================

    def correct_zero_dpc(self, dpc_result, initialization_parameters):
        dpc01              = dpc_result.get_parameter("diffPhase01")
        dpc10              = dpc_result.get_parameter("diffPhase10")
        virtual_pixelsize  = dpc_result.get_parameter("virtual_pixelsize")

        phenergy           = initialization_parameters.get_parameter("phenergy")
        pixelsize          = initialization_parameters.get_parameter("pixelsize")
        distDet2sample     = initialization_parameters.get_parameter("distDet2sample")
        correct_pi_jump    = initialization_parameters.get_parameter("correct_pi_jump")
        remove_mean        = initialization_parameters.get_parameter("remove_mean")
        correct_dpc_center = initialization_parameters.get_parameter("correct_dpc_center")

        self.__plotter.register_context_window(CORRECT_ZERO_DPC_CONTEXT_KEY)

        def __get_pi_jump(angle_i):
            return int(np.round(np.mean(angle_i / np.pi)))

        factor = distDet2sample*hc/phenergy
        angle = [dpc01/pixelsize[1]*factor, dpc10/pixelsize[0]*factor]
        pi_jump = [__get_pi_jump(angle[0]), __get_pi_jump(angle[1])]

        self.__script_logger.print('Initial Hrz Mean angle/pi : {:} pi'.format(np.mean(angle[0]/np.pi)))
        self.__script_logger.print('Initial Vt Mean angle/pi : {:} pi'.format(np.mean(angle[1]/np.pi)))

        self.__plotter.push_plot_on_context(CORRECT_ZERO_DPC_CONTEXT_KEY, CorrectDPC, angle=angle, pi_jump=pi_jump)

        def __get_dpc(angle_i, pixelsize_i):
            return angle_i * pixelsize_i / factor

        if not sum(pi_jump) == 0 and correct_pi_jump:
            angle[0] -= pi_jump[0] * np.pi
            angle[1] -= pi_jump[1] * np.pi

            dpc01 = __get_dpc(angle[0], pixelsize[0])
            dpc10 = __get_dpc(angle[1], pixelsize[1])

            self.__plotter.push_plot_on_context(CORRECT_ZERO_DPC_CONTEXT_KEY, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Correct \u03c0 jump")

        self.__main_logger.print_message('mean angle/pi 0: {:} pi'.format(np.mean(angle[0]/np.pi)))
        self.__main_logger.print_message('mean angle/pi 1: {:} pi'.format(np.mean(angle[1]/np.pi)))
        self.__script_logger.print('Horz Mean angle/pi : {:} pi'.format(np.mean(angle[0]/np.pi)))
        self.__script_logger.print('Vert Mean angle/pi : {:} pi'.format(np.mean(angle[1]/np.pi)))

        if remove_mean:
            angle[0] -= np.mean(angle[0])
            angle[1] -= np.mean(angle[1])

            dpc01 = __get_dpc(angle[0], pixelsize[0])
            dpc10 = __get_dpc(angle[1], pixelsize[1])

            self.__plotter.push_plot_on_context(CORRECT_ZERO_DPC_CONTEXT_KEY, CorrectDPCHistos, angle=angle, title="Remove mean")
            self.__plotter.push_plot_on_context(CORRECT_ZERO_DPC_CONTEXT_KEY, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Remove Mean")

        if correct_dpc_center and self.__plotter.is_active():
            angle = self.__plotter.show_interactive_plot(CorrectDPCCenter, container_widget=None, angle=angle)

            dpc01 = __get_dpc(angle[0], pixelsize[0])
            dpc10 = __get_dpc(angle[1], pixelsize[1])

            self.__plotter.push_plot_on_context(CORRECT_ZERO_DPC_CONTEXT_KEY, CorrectDPCHistos, angle=angle, title="Correct DPC Center")
            self.__plotter.push_plot_on_context(CORRECT_ZERO_DPC_CONTEXT_KEY, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Correct DPC Center")

        self.__draw_context(CORRECT_ZERO_DPC_CONTEXT_KEY)

        return WavePyData(diffPhase01=dpc01, diffPhase10=dpc10, virtual_pixelsize=virtual_pixelsize)

    # %% ==================================================================================================

    def remove_linear_fit(self, correct_zero_dpc_result, initialization_parameters):
        diffPhase01        = correct_zero_dpc_result.get_parameter("diffPhase01")
        diffPhase10        = correct_zero_dpc_result.get_parameter("diffPhase10")
        virtual_pixelsize  = correct_zero_dpc_result.get_parameter("virtual_pixelsize")

        remove_linear      = initialization_parameters.get_parameter("remove_linear")

        if not remove_linear:
            diffPhase01_2save = diffPhase01
            diffPhase10_2save = diffPhase10
            linfitDPC01 = None
            linfitDPC10 = None
        else:
            self.__plotter.register_context_window(REMOVE_LINEAR_FIT_CONTEXT_KEY)

            def __fit_lin_surfaceH(zz, pixelsize):
                xx, yy = common_tools.grid_coord(zz, pixelsize)
                argNotNAN = np.isfinite(zz)
                f = zz[argNotNAN].flatten()
                x = xx[argNotNAN].flatten()
                X_matrix = np.vstack([x, x * 0.0 + 1]).T
                beta_matrix = np.linalg.lstsq(X_matrix, f)[0]
                fit = (beta_matrix[0] * xx + beta_matrix[1])
                mask = zz * 0.0 + 1.0
                mask[~argNotNAN] = np.nan

                return fit * mask, beta_matrix

            def __fit_lin_surfaceV(zz, pixelsize):
                xx, yy = common_tools.grid_coord(zz, pixelsize)
                argNotNAN = np.isfinite(zz)
                f = zz[argNotNAN].flatten()
                y = yy[argNotNAN].flatten()
                X_matrix = np.vstack([y, y * 0.0 + 1]).T
                beta_matrix = np.linalg.lstsq(X_matrix, f)[0]
                fit = (beta_matrix[0] * yy + beta_matrix[1])
                mask = zz * 0.0 + 1.0
                mask[~argNotNAN] = np.nan

                return fit * mask, beta_matrix

            linfitDPC01, cH = __fit_lin_surfaceH(diffPhase01, virtual_pixelsize)
            linfitDPC10, cV = __fit_lin_surfaceV(diffPhase10, virtual_pixelsize)

            self.__ini.set_list_at_ini('Parameters','lin fitting coef cH', cH)
            self.__ini.set_list_at_ini('Parameters','lin fitting coef cV', cV)
            self.__ini.push()

            diffPhase01_2save = diffPhase01 - linfitDPC01
            diffPhase10_2save = diffPhase10 - linfitDPC10

            self.__plotter.push_plot_on_context(REMOVE_LINEAR_FIT_CONTEXT_KEY, PlotDPC, dpc01=linfitDPC01,       dpc10=linfitDPC10,       pixelsize=virtual_pixelsize, titleStr="Linear DPC Component")
            self.__plotter.push_plot_on_context(REMOVE_LINEAR_FIT_CONTEXT_KEY, PlotDPC, dpc01=diffPhase01_2save, dpc10=diffPhase10_2save, pixelsize=virtual_pixelsize, titleStr="(removed linear DPC component)")

            self.__draw_context(REMOVE_LINEAR_FIT_CONTEXT_KEY)

        return WavePyData(diffPhase01=diffPhase01_2save,
                          diffPhase10=diffPhase10_2save,
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=linfitDPC01,
                          linfitDPC10=linfitDPC10)

    # %% ==================================================================================================

    def dpc_profile_analysis(self, remove_linear_fit_result, initialization_parameters):
        diffPhase01        = remove_linear_fit_result.get_parameter("diffPhase01")
        diffPhase10        = remove_linear_fit_result.get_parameter("diffPhase10")
        virtual_pixelsize  = remove_linear_fit_result.get_parameter("virtual_pixelsize")

        fnameH = self.__plotter.save_sdf_file(diffPhase01, virtual_pixelsize, file_suffix="_dpc_X", extraHeader={'Title': 'DPC 01', 'Zunit': 'rad'})
        fnameV = self.__plotter.save_sdf_file(diffPhase10, virtual_pixelsize, file_suffix="_dpc_Y", extraHeader={'Title': 'DPC 10', 'Zunit': 'rad'})

        projectionFromDiv = 1.0

        self.__script_logger.print('projectionFromDiv : {:.4f}'.format(projectionFromDiv))

        self.__dpc_profile_analysis_manager.dpc_profile_analysis(WavePyData(diffPhaseH=diffPhase01, #None,
                                                                            diffPhaseV=diffPhase10,
                                                                            virtual_pixelsize=virtual_pixelsize,
                                                                            fnameH=fnameH, #None,
                                                                            fnameV=fnameV,
                                                                            grazing_angle=0,
                                                                            projectionFromDiv=projectionFromDiv,
                                                                            remove1stOrderDPC=False,
                                                                            remove2ndOrder=False,
                                                                            nprofiles=5,
                                                                            filter_width=50),
                                                                 initialization_parameters)

        return WavePyData(diffPhase01=diffPhase01,
                          diffPhase10=diffPhase10,
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=remove_linear_fit_result.get_parameter("linfitDPC01"),
                          linfitDPC10=remove_linear_fit_result.get_parameter("linfitDPC10"))

    # %% ==================================================================================================

    def fit_radius_dpc(self, dpc_profile_analysis_result, initialization_parameters):
        diffPhase01       = dpc_profile_analysis_result.get_parameter("diffPhase01")
        diffPhase10       = dpc_profile_analysis_result.get_parameter("diffPhase10")
        virtual_pixelsize = dpc_profile_analysis_result.get_parameter("virtual_pixelsize")

        self.__plotter.register_context_window(FIT_RADIUS_DPC_CONTEXT_KEY)
        self.__plotter.push_plot_on_context(FIT_RADIUS_DPC_CONTEXT_KEY, FitRadiusDPC, dpx=diffPhase01, dpy=diffPhase10, pixelsize=virtual_pixelsize, kwave=self.__kwave, str4title="")

        self.__draw_context(FIT_RADIUS_DPC_CONTEXT_KEY)

        return WavePyData(diffPhase01=diffPhase01,
                          diffPhase10=diffPhase10,
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=dpc_profile_analysis_result.get_parameter("linfitDPC01"),
                          linfitDPC10=dpc_profile_analysis_result.get_parameter("linfitDPC10"))

    # %% ==================================================================================================

    def do_integration(self, fit_radius_dpc_result, initialization_parameters):
        diffPhase01       = fit_radius_dpc_result.get_parameter("diffPhase01")
        diffPhase10       = fit_radius_dpc_result.get_parameter("diffPhase10")
        virtual_pixelsize = fit_radius_dpc_result.get_parameter("virtual_pixelsize")

        do_integration   = initialization_parameters.get_parameter("do_integration")

        if do_integration:
            self.__plotter.register_context_window(INTEGRATION_CONTEXT_KEY)

            self.__main_logger.print_message('Performing Frankot-Chellappa Integration')

            phase = self.__doIntegration(diffPhase01, diffPhase10, virtual_pixelsize,
                                         INTEGRATION_CONTEXT_KEY, message="Crop Differential Phase")

            self.__main_logger.print_message('DONE')
            self.__main_logger.print_message('Plotting Phase in meters')

            integrated_data = -1 / 2 / np.pi * phase * self.__wavelength

            self.__plotter.push_plot_on_context(INTEGRATION_CONTEXT_KEY, PlotIntegration,
                                                data=integrated_data * 1e9,
                                                pixelsize=virtual_pixelsize,
                                                titleStr = r'-WF $[nm]$',
                                                ctitle="",
                                                max3d_grid_points=101,
                                                kwarg4surf={})

            self.__plotter.save_sdf_file(integrated_data, virtual_pixelsize, file_suffix='_phase', extraHeader={'Title': 'WF Phase', 'Zunit': 'meters'})

            self.__draw_context(INTEGRATION_CONTEXT_KEY)

        self.__script_logger.print("\n\n" + self.__ini.dump())

        return WavePyData(diffPhase01=diffPhase01,
                          diffPhase10=diffPhase10,
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=fit_radius_dpc_result.get_parameter("linfitDPC01"),
                          linfitDPC10=fit_radius_dpc_result.get_parameter("linfitDPC10"),
                          phase=phase if do_integration else None)

    # %% ==================================================================================================

    def calc_thickness(self, integration_result, initialization_parameters):
        virtual_pixelsize = integration_result.get_parameter("virtual_pixelsize")
        phase             = integration_result.get_parameter("phase")

        do_integration   = initialization_parameters.get_parameter("do_integration")
        calc_thickness   = initialization_parameters.get_parameter("calc_thickness")

        if do_integration and calc_thickness:
            self.__plotter.register_context_window(CALCULATE_THICKNESS_CONTEXT_KEY)

            self.__main_logger.print_message('Plotting Thickness')

            material_idx   = initialization_parameters.get_parameter("material_idx")
            phenergy       = initialization_parameters.get_parameter("phenergy")
            distDet2sample = initialization_parameters.get_parameter("distDet2sample")

            delta, material, density = get_delta(phenergy, material_idx=material_idx)

            thickness = -(phase - np.min(phase)) / self.__kwave / delta

            titleStr = r'Material: ' + material + ', Thickness $[\mu m]$'

            self.__plotter.push_plot_on_context(CALCULATE_THICKNESS_CONTEXT_KEY, PlotIntegration,
                                                title="Thickness",
                                                data=thickness * 1e6,
                                                pixelsize=virtual_pixelsize,
                                                titleStr=titleStr,
                                                ctitle=r'$[\mu m]$',
                                                max3d_grid_points=101,
                                                kwarg4surf={})

            # Log thickness properties
            self.__script_logger.print('Material = ' + material)
            self.__script_logger.print('density = ' + str('{:.3g}'.format(density)) + ' g/cm^3')
            self.__script_logger.print('delta = ' + str('{:.5g}'.format(delta)))

            thickSensitivy100 = virtual_pixelsize[0] ** 2 / distDet2sample / delta / 100
            # the 100 means that I arbitrarylly assumed the angular error in
            #  fringe displacement to be 2pi/100 = 3.6 deg
            self.__script_logger.print('Thickness Sensitivy 100 [m] = ' + str('{:.5g}'.format(thickSensitivy100)))
            self.__plotter.save_sdf_file(thickness, virtual_pixelsize, file_suffix='_thickness', extraHeader={'Title': 'Thickness', 'Zunit': 'meters'})

            self.__draw_context(CALCULATE_THICKNESS_CONTEXT_KEY)

        return WavePyData(diffPhase01=integration_result.get_parameter("diffPhase01"),
                          diffPhase10=integration_result.get_parameter("diffPhase10"),
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=integration_result.get_parameter("linfitDPC01"),
                          linfitDPC10=integration_result.get_parameter("linfitDPC10"),
                          phase=phase,
                          thickness=thickness if calc_thickness else None)

    # %% ==================================================================================================

    def calc_2nd_order_component_of_the_phase(self, integration_result, initialization_parameters):
        diffPhase01       = integration_result.get_parameter("diffPhase01")
        diffPhase10       = integration_result.get_parameter("diffPhase10")
        virtual_pixelsize = integration_result.get_parameter("virtual_pixelsize")
        linfitDPC01       = integration_result.get_parameter("linfitDPC01")
        linfitDPC10       = integration_result.get_parameter("linfitDPC10")

        do_integration = initialization_parameters.get_parameter("do_integration")
        remove_linear  = initialization_parameters.get_parameter("remove_linear")

        # % 2nd order component of phase

        if do_integration and remove_linear:
            self.__plotter.register_context_window(CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE)

            data = 1 / 2 / np.pi * self.__doIntegration(linfitDPC01, linfitDPC10, virtual_pixelsize,
                                                        CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE, message="New Crop for 2nd order component of the phase?") # phase_2nd_order

            self.__plotter.push_plot_on_context(CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE, PlotIntegration,
                                                title="2nd order component of the phase",
                                                data=data,
                                                pixelsize=virtual_pixelsize,
                                                titleStr=r'WF, 2nd order component' + r'$[\lambda$ units $]$',
                                                ctitle='',
                                                max3d_grid_points=101,
                                                kwarg4surf={})

            data = 1 / 2 / np.pi * self.__doIntegration(diffPhase01 - linfitDPC01, diffPhase10 - linfitDPC10, virtual_pixelsize,
                                                        CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE, message="New Crop for difference to 2nd order of the phase?")

            self.__plotter.push_plot_on_context(CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE, PlotIntegration,
                                                title="Difference to 2nd order of the phase",
                                                data=data,
                                                pixelsize=virtual_pixelsize,
                                                titleStr=r'WF, difference to 2nd order component' + r'$[\lambda$ units $]$',
                                                ctitle='',
                                                max3d_grid_points=101,
                                                kwarg4surf={})


            self.__plotter.save_sdf_file(data * self.__wavelength, virtual_pixelsize, file_suffix='_phase', extraHeader={'Title': 'WF Phase 2nd order removed', 'Zunit': 'meters'})

            self.__draw_context(CALCULATE_2ND_ORDER_COMPONENT_OF_THE_PHASE)

        return WavePyData(diffPhase01=diffPhase01,
                          diffPhase10=diffPhase10,
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=linfitDPC01,
                          linfitDPC10=linfitDPC10,
                          phase=integration_result.get_parameter("phase"),
                          thickness=integration_result.get_parameter("thickness", None))

    # %% ==================================================================================================

    def remove_2nd_order(self, integration_result, initialization_parameters):
        virtual_pixelsize = integration_result.get_parameter("virtual_pixelsize")
        phase             = integration_result.get_parameter("phase")

        do_integration = initialization_parameters.get_parameter("do_integration")
        calc_thickness = initialization_parameters.get_parameter("calc_thickness")
        remove_2nd_order = initialization_parameters.get_parameter("remove_2nd_order")

        if do_integration and remove_2nd_order:
            self.__plotter.register_context_window(REMOVE_2ND_ORDER)

            if calc_thickness:
                thickness = integration_result.get_parameter("thickness")

                err, popt = self.__remove2ndOrder(thickness, virtual_pixelsize)

                self.__main_logger.print_message('Thickness Radius of WF x: {:.3g} m'.format(popt[0]))
                self.__main_logger.print_message('Thickness Radius of WF y: {:.3g} m'.format(popt[1]))

                self.__plotter.push_plot_on_context(REMOVE_2ND_ORDER, PlotIntegration,
                                                    title="Thickness Residual",
                                                    data=err * 1e6,
                                                    pixelsize=virtual_pixelsize,
                                                    titleStr=r'Thickness $[\mu m ]$' + '\n' +
                                                             r'Rx = {:.3f} $\mu m$, '.format(popt[0] * 1e6) +
                                                             r'Ry = {:.3f} $\mu m$'.format(popt[1] * 1e6),
                                                    ctitle='',
                                                    max3d_grid_points=101,
                                                    kwarg4surf={})

                self.__plotter.save_sdf_file(err, virtual_pixelsize, file_suffix='_thickness_residual', extraHeader={'Title': 'Thickness Residual', 'Zunit': 'meters'})

            err, _ = self.__remove2ndOrder(phase, virtual_pixelsize)
            _, popt = common_tools.lsq_fit_parabola(1 / 2 / np.pi * phase * self.__wavelength, virtual_pixelsize)

            self.__main_logger.print_message('Curvature Radius of WF x: {:.3g} m'.format(popt[0]))
            self.__main_logger.print_message('Curvature Radius of WF y: {:.3g} m'.format(popt[1]))

            data = err / 2 / np.pi * self.__wavelength

            self.__plotter.push_plot_on_context(REMOVE_2ND_ORDER, PlotIntegration,
                                                title="Phase Residual",
                                                data=data * 1e9,
                                                pixelsize=virtual_pixelsize,
                                                titleStr=r'WF $[nm ]$' +
                                                         '\nRx = {:.3f} m, Ry = {:.3f} m'.format(popt[0], popt[1]),
                                                ctitle='',
                                                max3d_grid_points=101,
                                                kwarg4surf={})

            self.__plotter.save_sdf_file(err, virtual_pixelsize, file_suffix='_phase_residual', extraHeader={'Title': 'WF Phase Residual', 'Zunit': 'meters'})

            self.__main_logger.print_message('DONE')

            self.__draw_context(REMOVE_2ND_ORDER)


        return WavePyData(diffPhase01=integration_result.get_parameter("diffPhase01"),
                          diffPhase10=integration_result.get_parameter("diffPhase10"),
                          virtual_pixelsize=virtual_pixelsize,
                          linfitDPC01=integration_result.get_parameter("linfitDPC01"),
                          linfitDPC10=integration_result.get_parameter("linfitDPC10"),
                          phase=phase,
                          thickness=thickness if calc_thickness else None)

    ###################################################################
    # PRIVATE METHODS

    def __draw_context(self, context_key):
        self.__plotter.draw_context_on_widget(context_key, container_widget=self.__plotter.get_context_container_widget(context_key))

    @classmethod
    def __doIntegration(cls, diffPhase01, diffPhase10, virtual_pixelsize, context_key, message="New Crop for Integration?"):
        phase = grating_interferometry.dpc_integration(diffPhase01, diffPhase10, virtual_pixelsize, context_key=context_key, message=message)
        phase -= np.min(phase)

        return phase

    @classmethod
    def __remove2ndOrder(cls, data, virtual_pixelsize):
        data_2nd_order_lsq, popt = common_tools.lsq_fit_parabola(data, virtual_pixelsize)
        err = -(data - data_2nd_order_lsq)
        err -= np.min(err)

        return err, popt
