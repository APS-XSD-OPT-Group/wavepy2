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
from wavepy2.util.common.common_tools import FourierTransform
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger, register_secondary_logger, LoggerMode
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.plot.plot_tools import PlottingProperties
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.tools.common.bl import grating_interferometry, crop_image
from wavepy2.tools.common.bl.generic_process_manager import GenericProcessManager

from wavepy2.tools.common.widgets.harmonic_grid_plot_widget import HarmonicGridPlot
from wavepy2.tools.common.widgets.harmonic_peak_plot_widget import HarmonicPeakPlot
from wavepy2.tools.common.widgets.show_cropped_figure_widget import ShowCroppedFigure

from wavepy2.tools.diagnostic.coherence.widgets.sgz_input_parameters_widget import SGZInputParametersWidget, SGZInputParametersDialog, generate_initialization_parameters_sgz, PATTERNS, ZVEC_FROM
from wavepy2.tools.diagnostic.coherence.widgets.visibility_widget import VisibilityPlot
from wavepy2.tools.diagnostic.coherence.widgets.fit_period_vs_z_widget import FitPeriodVsZPlot

SINGLE_THREAD = 0
MULTI_THREAD = 1

class SingleGratingCoherenceZScanFacade(GenericProcessManager):
    def draw_initialization_parameters_widget(self, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def get_initialization_parameters(self, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def manager_initialization(self, initialization_parameters, script_logger_mode=LoggerMode.FULL, show_fourier=False): raise NotImplementedError()

    def draw_crop_initial_image(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def crop_initial_image(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def draw_crop_dark_image(self, initial_crop_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def crop_dark_image(self, initial_crop_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()

    def calculate_harmonic_periods(self, initial_crop_parameters, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def run_calculation(self, harm_periods_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def sort_calculation_result(self, run_calculation_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def fit_calculation_result(self, sort_calculation_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()

def create_single_grating_coherence_z_scan_manager(mode=MULTI_THREAD, n_cpus=None):
    return _SingleGratingCoherenceZScanMultiThread(n_cpus) if mode == MULTI_THREAD else _SingleGratingCoherenceZScanSingleThread()

APPLICATION_NAME = "Single Grating Z Scan"

INITIALIZATION_PARAMETERS_KEY          = APPLICATION_NAME + " Initialization"
CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY = "Calculate Harmonic Periods"
RUN_CALCULATION_CONTEXT_KEY            = "Run Calculation"
SORT_CALCULATION_RESULT_CONTEXT_KEY    = "Sort Calculation Result"
FIT_CALCULATION_RESULT_CONTEXT_KEY     = "Fit Calculation Result"

class __SingleGratingCoherenceZScan(SingleGratingCoherenceZScanFacade):

    def __init__(self):
        self.reload_utils()

    def reload_utils(self):
        self.__plotter    = get_registered_plotter_instance(application_name=APPLICATION_NAME)
        self._main_logger = get_registered_logger_instance(application_name=APPLICATION_NAME)
        self.__ini        = get_registered_ini_instance(application_name=APPLICATION_NAME)

    def draw_initialization_parameters_widget(self, plotting_properties=PlottingProperties(), **kwargs):
        if self.__plotter.is_active():
            add_context_label    = plotting_properties.get_parameter("add_context_label", True)
            use_unique_id        = plotting_properties.get_parameter("use_unique_id", False)

            unique_id = self.__plotter.register_context_window(INITIALIZATION_PARAMETERS_KEY,
                                                               context_window=plotting_properties.get_context_widget(),
                                                               use_unique_id=use_unique_id)

            self.__plotter.push_plot_on_context(INITIALIZATION_PARAMETERS_KEY, SGZInputParametersWidget, unique_id, **kwargs)
            self.__plotter.draw_context(INITIALIZATION_PARAMETERS_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

            return self.__plotter.get_plots_of_context(INITIALIZATION_PARAMETERS_KEY, unique_id=unique_id)
        else:
            return None

    def get_initialization_parameters(self, plotting_properties=PlottingProperties(), **kwargs):
        if self.__plotter.is_active():
            initialization_parameters = self.__plotter.show_interactive_plot(SGZInputParametersDialog,
                                                                             container_widget=plotting_properties.get_container_widget(),
                                                                             **kwargs)
        else:
            initialization_parameters = generate_initialization_parameters_sgz(dataFolder         = self.__ini.get_string_from_ini("Files", "data directory"),
                                                                               samplefileName     = self.__ini.get_string_from_ini("Files", "sample file name"),
                                                                               zvec_from          = self.__ini.get_string_from_ini("Parameters", "z distances from", default="Calculated"),
                                                                               startDist          = self.__ini.get_float_from_ini("Parameters", "starting distance scan", default=20 * 1e-3),
                                                                               step_z_scan        = self.__ini.get_float_from_ini("Parameters", "step size scan", default=5 * 1e-3),
                                                                               image_per_point    = self.__ini.get_int_from_ini("Parameters", "number of images per step", default=1),
                                                                               strideFile         = self.__ini.get_int_from_ini("Parameters", "stride", default=1),
                                                                               zvec_file          = self.__ini.get_string_from_ini("Parameters", "z distances file"),
                                                                               pixelsize          = self.__ini.get_float_from_ini("Parameters", "pixel size", default=6.5e-07),
                                                                               gratingPeriod      = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period", default=4.8e-06),
                                                                               pattern            = self.__ini.get_string_from_ini("Parameters", "pattern", default="Diagonal"),
                                                                               sourceDistanceV    = self.__ini.get_float_from_ini("Parameters", "source distance v", default=-0.73),
                                                                               sourceDistanceH    = self.__ini.get_float_from_ini("Parameters", "source distance h", default=34.0),
                                                                               unFilterSize       = self.__ini.get_int_from_ini("Parameters", "size for uniform filter", default=1),
                                                                               searchRegion       = self.__ini.get_int_from_ini("Parameters", "size for region for searching", default=1),
                                                                               logger=self._main_logger)
        return initialization_parameters

    def manager_initialization(self, initialization_parameters, script_logger_mode=LoggerMode.FULL, show_fourier=False):
        initialization_parameters.set_parameter("show_fourier", show_fourier)

        self.__plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(self.__plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode, application_name=APPLICATION_NAME)

        self.__script_logger = get_registered_secondary_logger(application_name=APPLICATION_NAME)

        return initialization_parameters

    # %% ==================================================================================================

    def draw_crop_initial_image(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        img             = initialization_parameters.get_parameter("img")
        pixelsize       = initialization_parameters.get_parameter("pixelsize")

        return crop_image.draw_colorbar_crop_image(img=img,
                                                   pixelsize=pixelsize,
                                                   plotting_properties=plotting_properties,
                                                   application_name=APPLICATION_NAME,
                                                   message="Crop for all Images",
                                                   **kwargs)

    def crop_initial_image(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        img_original    = initialization_parameters.get_parameter("img")
        pixelsize       = initialization_parameters.get_parameter("pixelsize")

        if self.__plotter.is_active():
            img, idx4crop, img_size_o, cmap, colorlimit = crop_image.colorbar_crop_image(img=img_original,
                                                                                         pixelsize=pixelsize,
                                                                                         plotting_properties=plotting_properties,
                                                                                         application_name=APPLICATION_NAME,
                                                                                         message="Crop for all Images",
                                                                                         **kwargs)

            return WavePyData(img_original=img_original,
                              img=img,
                              idx4crop=idx4crop,
                              img_size_o=img_size_o,
                              cmap=cmap,
                              colorlimit=colorlimit)
        else:
            idx4crop     = self.__ini.get_list_from_ini("Parameters", "Crop")
            img          = common_tools.crop_matrix_at_indexes(img_original, idx4crop)

            return WavePyData(img_original=img_original,
                              img=img,
                              idx4crop=idx4crop)

    def draw_crop_dark_image(self, initial_crop_parameters, plotting_properties=PlottingProperties(), **kwargs):
        img_original = initial_crop_parameters.get_parameter("img_original")
        cmap         = initial_crop_parameters.get_parameter("cmap")
        colorlimit   = initial_crop_parameters.get_parameter("colorlimit")

        return crop_image.draw_crop_image(img=img_original,
                                          plotting_properties=plotting_properties,
                                          application_name=APPLICATION_NAME,
                                          message="Crop for Dark",
                                          default_idx4crop=[0, 20, 0, 20],
                                          kwargs4graph={'cmap': cmap, 'vmin': colorlimit[0], 'vmax': colorlimit[1]},
                                          **kwargs)

    def crop_dark_image(self, initial_crop_parameters, plotting_properties=PlottingProperties(), **kwargs):
        img_original = initial_crop_parameters.get_parameter("img_original")
        cmap         = initial_crop_parameters.get_parameter("cmap")
        colorlimit   = initial_crop_parameters.get_parameter("colorlimit")

        if self.__plotter.is_active():
            _, idx4cropDark, _ = crop_image.crop_image(img=img_original,
                                                       plotting_properties=plotting_properties,
                                                       application_name=APPLICATION_NAME,
                                                       message="Crop for Dark",
                                                       default_idx4crop=[0, 20, 0, 20],
                                                       kwargs4graph={'cmap': cmap, 'vmin': colorlimit[0], 'vmax': colorlimit[1]},
                                                       **kwargs)
        else:
            idx4cropDark = [0, 20, 0, 20]

        initial_crop_parameters.set_parameter("idx4cropDark", idx4cropDark)

        return initial_crop_parameters

    # %% ==================================================================================================

    def calculate_harmonic_periods(self, initial_crop_parameters, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        img            = initial_crop_parameters.get_parameter("img",          default_value=initialization_parameters.get_parameter("img"))
        idx4crop       = initial_crop_parameters.get_parameter("idx4crop",     default_value=self.__ini.get_list_from_ini("Parameters", "Crop"))
        idx4cropDark   = initial_crop_parameters.get_parameter("idx4cropDark", default_value=[0, 20, 0, 20])

        pattern        = initialization_parameters.get_parameter("pattern")
        gratingPeriod  = initialization_parameters.get_parameter("gratingPeriod")
        pixelsize      = initialization_parameters.get_parameter("pixelsize")

        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        # Plot Image AFTER crop
        self.__plotter.push_plot_on_context(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY, ShowCroppedFigure, unique_id,
                                            img=img, pixelsize=[pixelsize, pixelsize], allows_saving=False, **kwargs)

        self._main_logger.print_message("Idx for cropping: " + str(idx4crop))

        # ==============================================================================
        # %% Harmonic Periods
        # ==============================================================================

        if pattern == PATTERNS[0]:
            period_harm_Vert = np.int(np.sqrt(2)*pixelsize/gratingPeriod*img.shape[0])
            period_harm_Horz = np.int(np.sqrt(2)*pixelsize/gratingPeriod*img.shape[1])
        elif pattern == PATTERNS[1]:
            period_harm_Vert = np.int(2*pixelsize/gratingPeriod*img.shape[0])
            period_harm_Horz = np.int(2*pixelsize/gratingPeriod*img.shape[1])

        # Obtain harmonic periods from images

        self._main_logger.print_message('MESSAGE: Obtain harmonic 10 experimentally')

        (period_harm_Vert, _) = grating_interferometry.exp_harm_period(img,
                                                                       [period_harm_Vert, period_harm_Horz],
                                                                       harmonic_ij=['1', '0'],
                                                                       searchRegion=40,
                                                                       isFFT=False,
                                                                       logger=self._main_logger)

        self._main_logger.print_message('Obtain harmonic 01 experimentally')

        (_, period_harm_Horz) = grating_interferometry.exp_harm_period(img,
                                                                       [period_harm_Vert, period_harm_Horz],
                                                                       harmonic_ij=['0', '1'],
                                                                       searchRegion=40,
                                                                       isFFT=False,
                                                                       logger=self._main_logger)

        dataFolder = initialization_parameters.get_parameter("dataFolder")
        startDist = initialization_parameters.get_parameter("startDist")
        strideFile = initialization_parameters.get_parameter("strideFile")
        nfiles = initialization_parameters.get_parameter("nfiles")
        zvec_from = initialization_parameters.get_parameter("zvec_from")
        step_z_scan = initialization_parameters.get_parameter("step_z_scan")
        sourceDistanceV = initialization_parameters.get_parameter("sourceDistanceV")
        sourceDistanceH = initialization_parameters.get_parameter("sourceDistanceH")
        unFilterSize = initialization_parameters.get_parameter("unFilterSize")
        searchRegion = initialization_parameters.get_parameter("searchRegion")

        self.__script_logger.print('Input folder: ' + dataFolder)
        self.__script_logger.print('\nNumber of files : ' + str(nfiles))
        self.__script_logger.print('Stride : ' + str(strideFile))
        self.__script_logger.print('Z distances is ' + zvec_from)
        if zvec_from == ZVEC_FROM[0]:
            self.__script_logger.print('Step zscan [mm] : {:.4g}'.format(step_z_scan*1e3))
            self.__script_logger.print('Start point zscan [mm] : {:.4g}'.format(startDist*1e3))
        self.__script_logger.print('Pixel Size [um] : {:.4g}'.format(pixelsize*1e6))
        self.__script_logger.print('Grating Period [um] : {:.4g}'.format(gratingPeriod*1e6))
        self.__script_logger.print('Grating Pattern : ' + pattern)
        self.__script_logger.print('Crop idxs : ' + str(idx4crop))
        self.__script_logger.print('Dark idxs : ' + str(idx4cropDark))
        self.__script_logger.print('Vertical Source Distance: ' + str(sourceDistanceV))
        self.__script_logger.print('Horizontal Source Distance: ' + str(sourceDistanceH))
        self.__script_logger.print('Uniform Filter Size : {:d}'.format(unFilterSize))
        self.__script_logger.print('Search Region : {:d}'.format(searchRegion))

        self.__plotter.draw_context(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(period_harm_Vert=period_harm_Vert, period_harm_Horz=period_harm_Horz, img=img, idx4crop=idx4crop, idx4cropDark=idx4cropDark)

    # %% ==================================================================================================

    def run_calculation(self, harm_periods_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        period_harm_Vert = harm_periods_result.get_parameter("period_harm_Vert")
        period_harm_Horz = harm_periods_result.get_parameter("period_harm_Horz")
        sample_img       = harm_periods_result.get_parameter("img")
        idx4crop         = harm_periods_result.get_parameter("idx4crop")
        idx4cropDark     = harm_periods_result.get_parameter("idx4cropDark")

        show_fourier    = initialization_parameters.get_parameter("show_fourier", False)
        listOfDataFiles = initialization_parameters.get_parameter("listOfDataFiles")
        zvec            = initialization_parameters.get_parameter("zvec")
        sourceDistanceV = initialization_parameters.get_parameter("sourceDistanceV")
        sourceDistanceH = initialization_parameters.get_parameter("sourceDistanceH")
        unFilterSize    = initialization_parameters.get_parameter("unFilterSize")
        searchRegion    = initialization_parameters.get_parameter("searchRegion")

        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(RUN_CALCULATION_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        result = self._get_calculation_result(period_harm_Vert,
                                              period_harm_Horz,
                                              idx4crop,
                                              idx4cropDark,
                                              listOfDataFiles,
                                              zvec,
                                              sourceDistanceV,
                                              sourceDistanceH,
                                              unFilterSize,
                                              searchRegion,
                                              np.min(zvec))

        if show_fourier:
            for i in range(len(result)):
                imgFFT         = FourierTransform.fft2d(result[i]["img"])
                harmonicPeriod = result[i]["harmonicPeriod"]
                image_name     = result[i]["image_name"]

                self.__plotter.push_plot_on_context(RUN_CALCULATION_CONTEXT_KEY, HarmonicGridPlot, unique_id,
                                                    imgFFT=imgFFT, harmonicPeriod=harmonicPeriod, image_name=image_name, allows_saving=False, **kwargs)
                self.__plotter.push_plot_on_context(RUN_CALCULATION_CONTEXT_KEY, HarmonicPeakPlot, unique_id,
                                                    imgFFT=imgFFT, harmonicPeriod=harmonicPeriod, image_name=image_name, allows_saving=False, **kwargs)

        self.__plotter.draw_context(RUN_CALCULATION_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(res=[res_i["visib_1st_harmonics"] for res_i in result], img=sample_img)

    # %% ==================================================================================================

    def sort_calculation_result(self, run_calculation_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        img       = run_calculation_result.get_parameter("img")
        res       = run_calculation_result.get_parameter("res")

        pixelsize = initialization_parameters.get_parameter("pixelsize")
        zvec      = initialization_parameters.get_parameter("zvec")

        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(SORT_CALCULATION_RESULT_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        contrastV = np.asarray([x[0] for x in res])
        contrastH = np.asarray([x[1] for x in res])

        p0 = np.asarray([x[2] for x in res])
        pv = np.asarray([x[3] for x in res])
        ph = np.asarray([x[4] for x in res])

        pattern_period_Vert_z = pixelsize/(pv[:, 0] - p0[:, 0])*img.shape[0]
        pattern_period_Horz_z = pixelsize/(ph[:, 1] - p0[:, 1])*img.shape[1]

        self.__plotter.save_csv_file(np.c_[zvec.T, contrastV.T, contrastH.T, pattern_period_Vert_z.T, pattern_period_Horz_z.T],
                                     headerList=['z [m]', 'Vert Contrast', 'Horz Contrast', 'Vert Period [m]', 'Horz Period [m]'])

        self.__plotter.push_plot_on_context(SORT_CALCULATION_RESULT_CONTEXT_KEY, VisibilityPlot, unique_id,
                                            zvec=zvec, contrastV=contrastV, contrastH=contrastH, **kwargs)

        self.__plotter.draw_context(SORT_CALCULATION_RESULT_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(pattern_period_Vert_z=pattern_period_Vert_z, pattern_period_Horz_z=pattern_period_Horz_z, contrastV=contrastV, contrastH=contrastH)

    # %% ==================================================================================================

    def fit_calculation_result(self, sort_calculation_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        pattern_period_Vert_z  = sort_calculation_result.get_parameter("pattern_period_Vert_z")
        contrastV              = sort_calculation_result.get_parameter("contrastV")
        pattern_period_Horz_z  = sort_calculation_result.get_parameter("pattern_period_Horz_z")
        contrastH              = sort_calculation_result.get_parameter("contrastH")

        zvec                   = initialization_parameters.get_parameter("zvec")

        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(FIT_CALCULATION_RESULT_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        sourceDistance_from_fit_V, patternPeriodFromData_V = self.__fit_period_vs_z(zvec,
                                                                                    pattern_period_Vert_z,
                                                                                    contrastV,
                                                                                    direction='Vertical',
                                                                                    threshold=0.002,
                                                                                    context_key=FIT_CALCULATION_RESULT_CONTEXT_KEY,
                                                                                    unique_id=unique_id,
                                                                                    **kwargs)

        sourceDistance_from_fit_H, patternPeriodFromData_H = self.__fit_period_vs_z(zvec,
                                                                                    pattern_period_Horz_z,
                                                                                    contrastH,
                                                                                    direction='Horizontal',
                                                                                    threshold=0.0005,
                                                                                    context_key=FIT_CALCULATION_RESULT_CONTEXT_KEY,
                                                                                    unique_id=unique_id,
                                                                                    **kwargs)

        self.__plotter.draw_context(FIT_CALCULATION_RESULT_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(sourceDistance_from_fit_V=sourceDistance_from_fit_V,
                          patternPeriodFromData_V=patternPeriodFromData_V,
                          sourceDistance_from_fit_H=sourceDistance_from_fit_H,
                          patternPeriodFromData_H=patternPeriodFromData_H)

    ###################################################################
    # PRIVATE METHODS

    def _get_calculation_result(self,
                                period_harm_Vert,
                                period_harm_Horz,
                                idx4crop,
                                idx4cropDark,
                                listOfDataFiles,
                                zvec,
                                sourceDistanceV,
                                sourceDistanceH,
                                unFilterSize,
                                searchRegion,
                                min_zvec): raise NotImplementedError()

    def __fit_period_vs_z(self, zvec, pattern_period_z, contrast, direction, threshold=0.005, context_key=FIT_CALCULATION_RESULT_CONTEXT_KEY, unique_id=None, **kwargs):
        args_for_NOfit = np.argwhere(contrast < threshold).flatten()
        args_for_fit = np.argwhere(contrast >= threshold).flatten()

        if 'Hor' in direction:
            ls1 = '-ro'
            lx = 'r'
            lc2 = 'm'
        else:
            ls1 = '-ko'
            lx = 'k'
            lc2 = 'c'

        output_data = WavePyData()

        self.__plotter.push_plot_on_context(context_key, FitPeriodVsZPlot, unique_id,
                                            zvec=zvec,
                                            args_for_NOfit=args_for_NOfit,
                                            args_for_fit=args_for_fit,
                                            pattern_period_z=pattern_period_z,
                                            lx=lx,
                                            ls1=ls1,
                                            lc2=lc2,
                                            direction=direction,
                                            output_data=output_data,
                                            **kwargs)


        return output_data.get_parameter("sourceDistance"), output_data.get_parameter("patternPeriodFromData")

#=========================================================================================
# MULTI-THREADING SECTION
#=========================================================================================

def _run_calculation(parameters):
        i, \
        data_file_i, \
        zvec_i, \
        min_zvec, \
        idx4cropDark, \
        idx4crop, \
        period_harm_Vert, \
        sourceDistanceV, \
        period_harm_Horz, \
        sourceDistanceH, \
        searchRegion, \
        unFilterSize = parameters

        # python3.8 do not share the same environment, so the Singleton is not active
        try: get_registered_logger_instance(application_name=APPLICATION_NAME).print_message("loop " + str(i) + ": " + data_file_i)
        except: print("loop " + str(i) + ": " + data_file_i)

        img = read_tiff(data_file_i)

        darkMeanValue = np.mean(common_tools.crop_matrix_at_indexes(img, idx4cropDark))

        # TODO xshi, need to add option of input one value
        img = img - darkMeanValue  # calculate and remove dark
        img = common_tools.crop_matrix_at_indexes(img, idx4crop)

        pv = int(period_harm_Vert / (sourceDistanceV + zvec_i) * (sourceDistanceV + min_zvec))
        ph = int(period_harm_Horz / (sourceDistanceH + zvec_i) * (sourceDistanceH + min_zvec))

        result = {}
        result["img"] = img
        result["harmonicPeriod"]=[pv, ph]
        result["image_name"] = 'FFT_{:.0f}mm'.format(zvec_i * 1e3)
        result["visib_1st_harmonics"] =  grating_interferometry.visib_1st_harmonics(img, [pv, ph], searchRegion=searchRegion, unFilterSize=unFilterSize)

        return result

#=========================================================================================
# SINGLE THREAD
#=========================================================================================

class _SingleGratingCoherenceZScanSingleThread(__SingleGratingCoherenceZScan):
    def __init__(self):
        super(_SingleGratingCoherenceZScanSingleThread, self).__init__()

    def _get_calculation_result(self,
                                period_harm_Vert,
                                period_harm_Horz,
                                idx4crop,
                                idx4cropDark,
                                listOfDataFiles,
                                zvec,
                                sourceDistanceV,
                                sourceDistanceH,
                                unFilterSize,
                                searchRegion,
                                min_zvec):
        res = []
        for i in range(len(listOfDataFiles)):
            res.append(_run_calculation([i,
                                         listOfDataFiles[i],
                                         zvec[i],
                                         min_zvec,
                                         idx4cropDark,
                                         idx4crop,
                                         period_harm_Vert,
                                         sourceDistanceV,
                                         period_harm_Horz,
                                         sourceDistanceH,
                                         searchRegion,
                                         unFilterSize]))
        return res


#=========================================================================================
# MULTI THREAD
#=========================================================================================

from multiprocessing import Pool, cpu_count
import time

class _SingleGratingCoherenceZScanMultiThread(__SingleGratingCoherenceZScan):
    def __init__(self, n_cpus=None):
        super(_SingleGratingCoherenceZScanMultiThread, self).__init__()
        available_cpus = cpu_count()
        if not n_cpus is None and n_cpus > 0:
            if n_cpus > available_cpus - 1: raise ValueError("Max number of CPUs available = " + str(available_cpus-1))
            self.__n_cpus = n_cpus
        else:
            self.__n_cpus = available_cpus - 2
            if self.__n_cpus < 2: raise ValueError("Auto Nr. CPUs available < 2: Multi-Thread mode not possible")

    def _get_calculation_result(self,
                                period_harm_Vert,
                                period_harm_Horz,
                                idx4crop,
                                idx4cropDark,
                                listOfDataFiles,
                                zvec,
                                sourceDistanceV,
                                sourceDistanceH,
                                unFilterSize,
                                searchRegion,
                                min_zvec):
        tzero = time.time()
        pool = Pool(self.__n_cpus)

        self._main_logger.print_message("%d cpu used for this calculation" % self.__n_cpus)

        parameters = []
        for i in range(len(listOfDataFiles)): parameters.append([i,
                                                                 listOfDataFiles[i],
                                                                 zvec[i],
                                                                 min_zvec,
                                                                 idx4cropDark,
                                                                 idx4crop,
                                                                 period_harm_Vert,
                                                                 sourceDistanceV,
                                                                 period_harm_Horz,
                                                                 sourceDistanceH,
                                                                 searchRegion,
                                                                 unFilterSize])
        res = pool.map(_run_calculation, parameters)
        pool.close()

        self._main_logger.print_message("Time spent: {0:.3f} s".format(time.time() - tzero))

        return res
