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
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core import grating_interferometry

from wavepy2.core.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.core.widgets.harmonic_grid_plot_widget import HarmonicGridPlot
from wavepy2.core.widgets.harmonic_peak_plot_widget import HarmonicPeakPlot
from wavepy2.tools.common.widgets.colorbar_crop_dialog_widget import ColorbarCropDialogPlot
from wavepy2.tools.common.widgets.show_cropped_figure_widget import ShowCroppedFigure

from wavepy2.tools.diagnostic.coherence.widgets.sgz_input_parameters_widget import SGZInputParametersWidget, generate_initialization_parameters_sgz, PATTERNS, ZVEC_FROM
from wavepy2.tools.diagnostic.coherence.widgets.visibility_widget import VisibilityPlot
from wavepy2.tools.diagnostic.coherence.widgets.fit_period_vs_z_widget import FitPeriodVsZPlot

SINGLE_THREAD = 0
MULTI_THREAD = 1

class SingleGratingCoherenceZScanFacade:
    def get_initialization_parameters(self, script_logger_mode): raise NotImplementedError()
    def calculate_harmonic_periods(self, initialization_parameters): raise NotImplementedError()
    def run_calculation(self, harm_periods_result, initialization_parameters): raise NotImplementedError()
    def sort_calculation_result(self, run_calculation_result, initialization_parameters): raise NotImplementedError()

def create_single_grating_coherence_z_scan_manager(mode=MULTI_THREAD, n_cpus=None):
    return __SingleGratingCoherenceZScanMultiThread(n_cpus) if mode == MULTI_THREAD else __SingleGratingCoherenceZScanSingleThread()

CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY = "Calculate Harmonic Periods"
RUN_CALCULATION_CONTEXT_KEY            = "Run Calculation"
SORT_CALCULATION_RESULT_CONTEXT_KEY    = "Sort Calculation Result"
FIT_CALCULATION_RESULT_CONTEXT_KEY     = "Fit Calculation Result"

class __SingleGratingCoherenceZScan(SingleGratingCoherenceZScanFacade):

    def __init__(self):
        self.__plotter     = get_registered_plotter_instance()
        self.__main_logger = get_registered_logger_instance()
        self.__ini         = get_registered_ini_instance()

    def get_initialization_parameters(self, script_logger_mode, show_fourier=False):
        if self.__plotter.is_active():
            initialization_parameters = self.__plotter.show_interactive_plot(SGZInputParametersWidget, container_widget=None)
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
                                                                               logger=self.__main_logger)

        initialization_parameters.set_parameter("show_fourier", show_fourier)

        plotter = get_registered_plotter_instance()
        plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode)

        self.__script_logger = get_registered_secondary_logger()

        return initialization_parameters

    def calculate_harmonic_periods(self, initialization_parameters):
        imgOriginal    = initialization_parameters.get_parameter("img")
        pattern        = initialization_parameters.get_parameter("pattern")
        gratingPeriod  = initialization_parameters.get_parameter("gratingPeriod")
        pixelsize      = initialization_parameters.get_parameter("pixelsize")

        self.__plotter.register_context_window(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY)

        if self.__plotter.is_active():
            img, idx4crop, cmap, colorlimit = self.__plotter.show_interactive_plot(ColorbarCropDialogPlot, container_widget=None, img=imgOriginal, pixelsize=[pixelsize, pixelsize], message="Crop for all Images")

            _, idx4cropDark = self.__plotter.show_interactive_plot(CropDialogPlot,
                                                                   container_widget=None,
                                                                   img=imgOriginal,
                                                                   message="Crop for Dark ",
                                                                   default_idx4crop=[0, 20, 0, 20],
                                                                   kwargs4graph={'cmap': cmap, 'vmin': colorlimit[0], 'vmax': colorlimit[1]})
            self.__ini.push()
        else:
            idx4crop     = self.__ini.get_list_from_ini("Parameters", "Crop")
            img          = common_tools.crop_matrix_at_indexes(imgOriginal, idx4crop)
            idx4cropDark = [0, 20, 0, 20]

        # Plot Image AFTER crop
        self.__plotter.push_plot_on_context(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY, ShowCroppedFigure, img=img, pixelsize=[pixelsize, pixelsize], allows_saving=False)

        self.__main_logger.print_message("Idx for cropping: " + str(idx4crop))

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

        self.__main_logger.print_message('MESSAGE: Obtain harmonic 10 experimentally')

        (period_harm_Vert, _) = grating_interferometry.exp_harm_period(img,
                                                                       [period_harm_Vert, period_harm_Horz],
                                                                       harmonic_ij=['1', '0'],
                                                                       searchRegion=40,
                                                                       isFFT=False)

        self.__main_logger.print_message('Obtain harmonic 01 experimentally')

        (_, period_harm_Horz) = grating_interferometry.exp_harm_period(img,
                                                                       [period_harm_Vert, period_harm_Horz],
                                                                       harmonic_ij=['0', '1'],
                                                                       searchRegion=40,
                                                                       isFFT=False)

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

        self.__draw_context(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY)

        return WavePyData(period_harm_Vert=period_harm_Vert, period_harm_Horz=period_harm_Horz, img=img, idx4crop=idx4crop, idx4cropDark=idx4cropDark)


    def run_calculation(self, harm_periods_result, initialization_parameters):
        self.__plotter.register_context_window(RUN_CALCULATION_CONTEXT_KEY)

        period_harm_Vert = harm_periods_result.get_parameter("period_harm_Vert")
        period_harm_Horz = harm_periods_result.get_parameter("period_harm_Horz")
        sample_img       = harm_periods_result.get_parameter("img")
        idx4crop         = harm_periods_result.get_parameter("idx4crop")
        idx4cropDark     = harm_periods_result.get_parameter("idx4cropDark")

        show_fourier    = initialization_parameters.get_parameter("show_fourier", False)
        listOfDataFiles = initialization_parameters.get_parameter("listOfDataFiles")
        zvec = initialization_parameters.get_parameter("zvec")
        sourceDistanceV = initialization_parameters.get_parameter("sourceDistanceV")
        sourceDistanceH = initialization_parameters.get_parameter("sourceDistanceH")
        unFilterSize = initialization_parameters.get_parameter("unFilterSize")
        searchRegion = initialization_parameters.get_parameter("searchRegion")

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

                self.__plotter.push_plot_on_context(RUN_CALCULATION_CONTEXT_KEY, HarmonicGridPlot, imgFFT=imgFFT, harmonicPeriod=harmonicPeriod, image_name=image_name, allows_saving=False)
                self.__plotter.push_plot_on_context(RUN_CALCULATION_CONTEXT_KEY, HarmonicPeakPlot, imgFFT=imgFFT, harmonicPeriod=harmonicPeriod, image_name=image_name, allows_saving=False)

        self.__draw_context(RUN_CALCULATION_CONTEXT_KEY)

        return WavePyData(res=[res_i["visib_1st_harmonics"] for res_i in result], img=sample_img)

    def sort_calculation_result(self, run_calculation_result, initialization_parameters):
        self.__plotter.register_context_window(SORT_CALCULATION_RESULT_CONTEXT_KEY)

        pixelsize = initialization_parameters.get_parameter("pixelsize")
        zvec      = initialization_parameters.get_parameter("zvec")

        img       = run_calculation_result.get_parameter("img")
        res       = run_calculation_result.get_parameter("res")

        contrastV = np.asarray([x[0] for x in res])
        contrastH = np.asarray([x[1] for x in res])

        p0 = np.asarray([x[2] for x in res])
        pv = np.asarray([x[3] for x in res])
        ph = np.asarray([x[4] for x in res])

        pattern_period_Vert_z = pixelsize/(pv[:, 0] - p0[:, 0])*img.shape[0]
        pattern_period_Horz_z = pixelsize/(ph[:, 1] - p0[:, 1])*img.shape[1]

        self.__plotter.save_csv_file(np.c_[zvec.T, contrastV.T, contrastH.T, pattern_period_Vert_z.T, pattern_period_Horz_z.T],
                                     headerList=['z [m]', 'Vert Contrast', 'Horz Contrast', 'Vert Period [m]', 'Horz Period [m]'])

        self.__plotter.push_plot_on_context(SORT_CALCULATION_RESULT_CONTEXT_KEY, VisibilityPlot, zvec=zvec, contrastV=contrastV, contrastH=contrastH)

        self.__draw_context(SORT_CALCULATION_RESULT_CONTEXT_KEY)

        return WavePyData(pattern_period_Vert_z=pattern_period_Vert_z, pattern_period_Horz_z=pattern_period_Horz_z, contrastV=contrastV, contrastH=contrastH)

    def fit_calculation_result(self, sort_calculation_result, initialization_parameters):
        self.__plotter.register_context_window(FIT_CALCULATION_RESULT_CONTEXT_KEY)

        zvec                   = initialization_parameters.get_parameter("zvec")

        pattern_period_Vert_z  = sort_calculation_result.get_parameter("pattern_period_Vert_z")
        contrastV              = sort_calculation_result.get_parameter("contrastV")
        pattern_period_Horz_z  = sort_calculation_result.get_parameter("pattern_period_Horz_z")
        contrastH              = sort_calculation_result.get_parameter("contrastH")

        sourceDistance_from_fit_V, patternPeriodFromData_V = self.__fit_period_vs_z(zvec,
                                                                                    pattern_period_Vert_z,
                                                                                    contrastV,
                                                                                    direction='Vertical',
                                                                                    threshold=0.002)

        sourceDistance_from_fit_H, patternPeriodFromData_H = self.__fit_period_vs_z(zvec,
                                                                                    pattern_period_Horz_z,
                                                                                    contrastH,
                                                                                    direction='Horizontal',
                                                                                    threshold=0.0005)

        self.__draw_context(FIT_CALCULATION_RESULT_CONTEXT_KEY)

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

    def __fit_period_vs_z(self, zvec, pattern_period_z, contrast, direction, threshold=0.005, context_key=FIT_CALCULATION_RESULT_CONTEXT_KEY):
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

        self.__plotter.push_plot_on_context(context_key, FitPeriodVsZPlot,
                                            zvec=zvec,
                                            args_for_NOfit=args_for_NOfit,
                                            args_for_fit=args_for_fit,
                                            pattern_period_z=pattern_period_z,
                                            lx=lx,
                                            ls1=ls1,
                                            lc2=lc2,
                                            direction=direction,
                                            output_data=output_data)


        return output_data.get_parameter("sourceDistance"), output_data.get_parameter("patternPeriodFromData")

    def __draw_context(self, context_key):
        self.__plotter.draw_context_on_widget(context_key, container_widget=self.__plotter.get_context_container_widget(context_key))

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
        try: get_registered_logger_instance().print_message("loop " + str(i) + ": " + data_file_i)
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

class __SingleGratingCoherenceZScanSingleThread(__SingleGratingCoherenceZScan):
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

class __SingleGratingCoherenceZScanMultiThread(__SingleGratingCoherenceZScan):
    def __init__(self, n_cpus=None):
        super().__init__()
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

        get_registered_logger_instance().print_message("%d cpu used for this calculation" % self.__n_cpus)

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

        get_registered_logger_instance().print_message("Time spent: {0:.3f} s".format(time.time() - tzero))

        return res
