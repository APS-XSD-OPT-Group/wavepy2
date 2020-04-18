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
import itertools
from scipy.optimize import curve_fit

from wavepy2.util.common import common_tools
from wavepy2.util.common.common_tools import hc
from wavepy2.util.plot import plot_tools
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger, register_secondary_logger, LoggerMode

from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.wavepy_data import WavePyData
from wavepy2.tools.common import physical_properties 

from wavepy2.core.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.core.widgets.plot_profile_widget import PlotProfile
from wavepy2.tools.common.widgets.simple_plot_widget import SimplePlot
from wavepy2.tools.metrology.lenses.widgets.frl_input_parameters_widget import FRLInputParametersWidget, generate_initialization_parameters_frl, LENS_GEOMETRIES
from wavepy2.tools.metrology.lenses.widgets.fit_radius_dpc_widget import FitRadiusDPC
from wavepy2.tools.metrology.lenses.widgets.plot_residual_1d_widget import PlotResidual1D
from wavepy2.tools.metrology.lenses.widgets.plot_residual_2d_widget import PlotResidualParabolicLens2D
from wavepy2.tools.metrology.lenses.widgets.slope_error_hist_widget import SlopeErrorHist

class FitResidualLensesFacade:
    def get_initialization_parameters(self, script_logger_mode): raise NotImplementedError()
    def crop_thickness(self, initialization_parameters): raise NotImplementedError()
    def center_image(self, crop_thickness_result, initialization_parameters): raise NotImplementedError()
    def fit_radius_dpc(self, center_image_result, initialization_parameters): raise NotImplementedError()
    def do_fit(self, fit_radius_dpc_result, initialization_parameters): raise NotImplementedError()

def create_fit_residual_lenses_manager():
    return __FitResidualLenses()

CROP_THICKNESS_CONTEXT_KEY = "Crop and Show Thickness"
CENTER_IMAGE_CONTEXT_KEY = "Center Image"
FIT_RADIUS_DPC_CONTEXT_KEY = "Fit Radius DPC"
DO_FIT_CONTEXT_KEY = "Do fit"

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
                                                                               lensGeometry=self.__ini.get_string_from_ini("Parameters", "lens geometry", default=LENS_GEOMETRIES[2]),
                                                                               phenergy= self.__ini.get_float_from_ini("Parameters", "photon energy", default=14000.0),
                                                                               crop_image=self.__ini.get_boolean_from_ini("Runtime", "crop image", default=False),
                                                                               fit_radius_dpc=self.__ini.get_boolean_from_ini("Runtime", "fit radius dpc", default=False))

        plotter = get_registered_plotter_instance()
        plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode)

        self.__wavelength = hc / initialization_parameters.get_parameter("phenergy")
        self.__kwave = 2 * np.pi / self.__wavelength

        self.__script_logger = get_registered_secondary_logger()

        return initialization_parameters

    def crop_thickness(self, initialization_parameters):
        self.__plotter.register_context_window(CROP_THICKNESS_CONTEXT_KEY)

        crop_thickness = initialization_parameters.get_parameter("crop_image")
        thickness      = initialization_parameters.get_parameter("thickness")
        xx             = initialization_parameters.get_parameter("xx")
        yy             = initialization_parameters.get_parameter("yy")

        if crop_thickness:
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
                                                xlabel=r"$x$ [$\mu m$ ]",
                                                ylabel=r"$y$ [$\mu m$ ]",
                                                zlabel=r"$z$ [$\mu m$ ]",
                                                arg4main={"cmap": "Spectral_r"})

        self.__draw_context(CROP_THICKNESS_CONTEXT_KEY)

        return WavePyData(thickness=thickness, xx=xx, yy=yy)

    def center_image(self, crop_thickness_result, initialization_parameters):
        self.__plotter.register_context_window(CENTER_IMAGE_CONTEXT_KEY)

        pixelsize = initialization_parameters.get_parameter("pixelsize")

        thickness = crop_thickness_result.get_parameter("thickness")
        xx        = crop_thickness_result.get_parameter("xx")
        yy        = crop_thickness_result.get_parameter("yy")

        # %% Center image
        radius4centering = np.min(thickness.shape) * np.min(pixelsize) * .75
        thickness = self.__center_lens_array_max_fit(thickness, pixelsize, radius4centering)

        self.__plotter.push_plot_on_context(CENTER_IMAGE_CONTEXT_KEY, SimplePlot,
                                            img=thickness * 1e6,
                                            pixelsize=pixelsize,
                                            title="Thickness",
                                            xlabel=r"$x$ [$\mu m$ ]",
                                            ylabel=r"$y$ [$\mu m$ ]")

        self.__script_logger.print("Array cropped to have the max at the center of the array")

        text2datfile = "# file name, Type of Fit, Curved Radius from fit [um],"
        text2datfile += " diameter4fit [um], sigma [um], pv [um]\n"

        self.__draw_context(CENTER_IMAGE_CONTEXT_KEY)

        return WavePyData(thickness=thickness, xx=xx, yy=yy, text2datfile=text2datfile)

    def fit_radius_dpc(self, center_image_result, initialization_parameters):
        self.__plotter.register_context_window(FIT_RADIUS_DPC_CONTEXT_KEY)

        fname        = initialization_parameters.get_parameter("thickness_file_name")
        thickness    = center_image_result.get_parameter("thickness")
        xx           = center_image_result.get_parameter("xx")
        yy           = center_image_result.get_parameter("yy")
        text2datfile = center_image_result.get_parameter("text2datfile")

        fit_radius_dpc = initialization_parameters.get_parameter("fit_radius_dpc")

        if fit_radius_dpc:
            dpcFiles = []
            dpcFiles.append(fname.replace("thickness", "dpc_X"))
            dpcFiles.append(fname.replace("thickness", "dpc_Y"))

            if len(dpcFiles) == 2:
                (dpx, pixelsize_dpc, _) = plot_tools.load_sdf_file(dpcFiles[0])

                (dpy, _, _) = plot_tools.load_sdf_file(dpcFiles[1])

                self.__plotter.push_plot_on_context(FIT_RADIUS_DPC_CONTEXT_KEY, FitRadiusDPC,
                                                    dpx=dpx,
                                                    dpy=dpy,
                                                    pixelsize=pixelsize_dpc,
                                                    radius4fit=np.min((-xx[0, 0], xx[-1, -1], -yy[0, 0], yy[-1, -1])) * 0.9,
                                                    kwave=self.__kwave,
                                                    str4title="")

        self.__draw_context(FIT_RADIUS_DPC_CONTEXT_KEY)

        return WavePyData(thickness=thickness, xx=xx, yy=yy, text2datfile=text2datfile)


    def do_fit(self, fit_radius_dpc_result, initialization_parameters):
        self.__plotter.register_context_window(DO_FIT_CONTEXT_KEY)

        nominalRadius     = initialization_parameters.get_parameter("nominalRadius")
        diameter4fit_list = initialization_parameters.get_parameter("diameter4fit_list")
        pixelsize         = initialization_parameters.get_parameter("pixelsize")
        str4title         = initialization_parameters.get_parameter("str4title")
        lensGeometry      = initialization_parameters.get_parameter("lensGeometry")
        phenergy          = initialization_parameters.get_parameter("phenergy")

        thickness    = fit_radius_dpc_result.get_parameter("thickness")
        text2datfile = fit_radius_dpc_result.get_parameter("text2datfile")

        self.__main_logger.print_message("Start Fit")

        if nominalRadius > 0: opt = [1, 2]
        else: opt = [1]

        for diameter4fit, i in itertools.product(diameter4fit_list, opt):
            radius4fit = self.__biggest_radius(thickness, pixelsize, diameter4fit / 2)

            self.__script_logger.print("Radius of the area for fit = {:.2f} um".format(radius4fit * 1e6))

            if i == 1:
                str4graphs = str4title
                (thickness_cropped, fitted, fitParameters) = self.__fit_parabolic_lens_2d(thickness, pixelsize, radius4fit=radius4fit, mode=lensGeometry)
            elif i == 2:
                # this overwrite the previous fit, but I need that fit because it
                # is fast (least square fit) and it provides initial values for the
                # interactive fit below
                str4graphs = "Nominal Radius Fit - " + str4title
                p0 = [nominalRadius, fitParameters[1], fitParameters[2], fitParameters[3]]
                bounds = ([p0[0] * .999999, -200.05e-6, -200.05e-6, -120.05e-6], [p0[0] * 1.00001, 200.05e-6, 200.05e-6, 120.05e-6])

                (thickness_cropped, fitted, fitParameters) = self.__fit_nominal_lens_2d(thickness,
                                                                                        pixelsize,
                                                                                        radius4fit=radius4fit,
                                                                                        p0=p0,
                                                                                        bounds=bounds,
                                                                                        kwargs4fit={"verbose": 2, "ftol": 1e-12, "gtol": 1e-12})

            xmatrix, ymatrix = common_tools.grid_coord(thickness_cropped, pixelsize)

            isNotNAN = np.isfinite(thickness_cropped[thickness_cropped.shape[0] // 2, :])
            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, PlotResidual1D,
                                                xvec=xmatrix[0, isNotNAN],
                                                data=thickness_cropped[thickness_cropped.shape[0] // 2, isNotNAN],
                                                fitted=fitted[thickness_cropped.shape[0] // 2, isNotNAN],
                                                direction="Horizontal",
                                                str4title=str4graphs +
                                                          "\nFit center profile Horizontal, " +
                                                          " R = {:.4g} um".format(fitParameters[0] * 1e6),
                                                saveAscii=True)


            isNotNAN = np.isfinite(thickness_cropped[:, thickness_cropped.shape[1]//2])
            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, PlotResidual1D,
                                                xvec=ymatrix[isNotNAN, 0],
                                                data=thickness_cropped[isNotNAN, thickness_cropped.shape[1]//2],
                                                fitted=fitted[isNotNAN, thickness_cropped.shape[1]//2],
                                                direction="Vertical",
                                                str4title=str4graphs +
                                                          "\nFit center profile Vertical, " +
                                                          r" R = {:.4g} $\mu m$".format(fitParameters[0] * 1e6),
                                                saveAscii=True)

            output_data = {}

            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, PlotResidualParabolicLens2D,
                                                thickness=thickness_cropped,
                                                pixelsize=pixelsize,
                                                fitted=fitted,
                                                fitParameters=fitParameters,
                                                str4title=str4graphs,
                                                saveSdfData=True,
                                                vlimErrSigma=4,
                                                plot3dFlag=True,
                                                output_data=output_data,
                                                context=DO_FIT_CONTEXT_KEY)

            sigma = output_data["sigma"]
            pv = output_data["pv"]
     
            material = "C"
            delta_lens, _, _ = physical_properties.get_delta(phenergy, material=material)
            
            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, SlopeErrorHist,
                                                thickness=thickness_cropped,
                                                pixelsize=pixelsize,
                                                fitted=fitted,
                                                delta=delta_lens,
                                                str4title=str4graphs + " " + str(phenergy/1000) + " KeV, " + material,
                                                output_data={})

            text2datfile += self.__plotter.get_save_file_prefix()
            text2datfile += ",\t Nominal"
            text2datfile += ",\t{:.4g},\t{:.4g}".format(fitParameters[0]*1e6, diameter4fit*1e6)
            text2datfile += ",\t{:.4g},\t{:.4g}\n".format(sigma*1e6, pv*1e6)

        fname_summary = self.__plotter.get_save_file_prefix() + "_2D_summary.csv"
        text_file = open(fname_summary, "w")
        text_file.write(text2datfile)
        text_file.close()
        self.__main_logger.print_message("Data saved at " + fname_summary)

        self.__draw_context(DO_FIT_CONTEXT_KEY)

        return WavePyData()

    ###################################################################
    # PRIVATE METHODS

    def __draw_context(self, context_key):
        self.__plotter.draw_context_on_widget(context_key, container_widget=self.__plotter.get_context_container_widget(context_key))

    # =============================================================================
    # %% 2D Fit
    # =============================================================================

    def __center_lens_array_max_fit(self, thickness, pixelsize, radius4fit=100e-6):
        """
        crop the array in order to have the max at the center of the array. It uses
        a fitting procedure of a 2D parabolic function to determine the center

        """

        radius4fit = self.__biggest_radius(thickness, pixelsize, radius4fit * 0.8)

        thickness = np.copy(thickness)

        xx, yy = common_tools.grid_coord(thickness, pixelsize)

        (_, _, fitParameters) = self.__fit_parabolic_lens_2d(thickness, pixelsize, radius4fit=radius4fit)

        center_i = np.argmin(np.abs(yy[:, 0]-fitParameters[2]))
        center_j = np.argmin(np.abs(xx[0, :]-fitParameters[1]))

        if 2*center_i > thickness.shape[0]: thickness = thickness[2 * center_i - thickness.shape[0]:, :]
        else: thickness = thickness[0:2 * center_i, :]

        if 2*center_j > thickness.shape[1]: thickness = thickness[:, 2 * center_j - thickness.shape[1]:]
        else: thickness = thickness[:, 0:2 * center_j]

        return thickness

    # =============================================================================

    def __biggest_radius(self, thickness, pixelsize, radius4fit):
        bool_x = (thickness.shape[0] // 2 < radius4fit // pixelsize[0])
        bool_y = (thickness.shape[1] // 2 < radius4fit // pixelsize[1])

        if bool_x or bool_y:
            radius4fit = 0.9*np.min((thickness.shape[0] * pixelsize[0] / 2, thickness.shape[1] * pixelsize[1] / 2))

            self.__main_logger.print_warning("WARNING: Image size smaller than the region for fit")
            self.__main_logger.print_warning("New Radius: {:.3f}um".format(radius4fit*1e6))

        return radius4fit


    # =============================================================================

    def __fit_parabolic_lens_2d(self, thickness, pixelsize, radius4fit, mode="2D"):

        # FIT
        xx, yy = common_tools.grid_coord(thickness, pixelsize)
        mask = xx*np.nan

        lim_x = np.argwhere(xx[0, :] <= -radius4fit*1.01)[-1, 0]
        lim_y = np.argwhere(yy[:, 0] <= -radius4fit*1.01)[-1, 0]

        if "2D" in mode:

            r2 = np.sqrt(xx**2 + yy**2)
            mask[np.where(r2 < radius4fit)] = 1.0

        elif "1Dx" in mode:
            mask[np.where(xx**2 < radius4fit)] = 1.0
            lim_y = 2

        elif "1Dy" in mode:
            mask[np.where(yy**2 < radius4fit)] = 1.0
            lim_x = 2

        fitted, popt = self.__lsq_fit_parabola(thickness*mask, pixelsize, mode=mode)

        self.__main_logger.print_message("Parabolic 2D Fit")
        self.__main_logger.print_message("Curv Radius, xo, yo, offset")
        self.__main_logger.print_message(popt)

        self.__main_logger.print_message("Parabolic 2D Fit: Radius of 1 face  / nfaces, x direction: {:.4g} um".format(popt[0]*1e6))

        if (lim_x <= 1 or lim_y <= 1):
            thickness_cropped = thickness*mask
            fitted_cropped = fitted*mask
        else:
            thickness_cropped = (thickness[lim_y:-lim_y+1, lim_x:-lim_x+1] * mask[lim_y:-lim_y+1, lim_x:-lim_x+1])
            fitted_cropped = (fitted[lim_y:-lim_y+1, lim_x:-lim_x+1] * mask[lim_y:-lim_y+1, lim_x:-lim_x+1])

        return (thickness_cropped, fitted_cropped, popt)

    # =============================================================================

    def __lsq_fit_parabola(self, zz, pixelsize, mode="2D"):
        xx, yy = common_tools.grid_coord(zz, pixelsize)

        if np.all(np.isfinite(zz)):  # if there is no nan
            f = zz.flatten()
            x = xx.flatten()
            y = yy.flatten()
        else:
            argNotNAN = np.isfinite(zz)
            f = zz[argNotNAN].flatten()
            x = xx[argNotNAN].flatten()
            y = yy[argNotNAN].flatten()

        if "2D" in mode:
            X_matrix = np.vstack([x**2 + y**2, x, y, x*0.0 + 1]).T

            beta_matrix = np.linalg.lstsq(X_matrix, f)[0]

            fit = (beta_matrix[0]*(xx**2 + yy**2) +
                   beta_matrix[1]*xx +
                   beta_matrix[2]*yy +
                   beta_matrix[3])

        elif "1Dx" in mode:
            X_matrix = np.vstack([x**2, x, y, x*0.0 + 1]).T

            beta_matrix = np.linalg.lstsq(X_matrix, f)[0]

            fit = (beta_matrix[0]*(xx**2) +
                   beta_matrix[1]*xx +
                   beta_matrix[2]*yy +
                   beta_matrix[3])

        elif "1Dy" in mode:
            X_matrix = np.vstack([y**2, x, y, x*0.0 + 1]).T

            beta_matrix = np.linalg.lstsq(X_matrix, f)[0]

            fit = (beta_matrix[0]*(yy**2) +
                   beta_matrix[1]*xx +
                   beta_matrix[2]*yy +
                   beta_matrix[3])

        if np.all(np.isfinite(zz)):
            mask = zz*0.0 + 1.0
        else:
            mask = zz*0.0 + 1.0
            mask[~argNotNAN] = np.nan

        R_o = 1/2/beta_matrix[0]
        x_o = -beta_matrix[1]/beta_matrix[0]/2
        y_o = -beta_matrix[2]/beta_matrix[0]/2
        offset = beta_matrix[3]

        popt = [R_o, x_o, y_o, offset]

        return fit*mask, popt

    # =============================================================================

    def __fit_nominal_lens_2d(self, thickness, pixelsize, radius4fit,
                              p0=[20e-6, 1.005e-6, -.005e-6, -.005e-6],
                              bounds=([10e-6, -2.05e-6, -2.05e-6, -2.05e-6],
                                      [50e-6, 2.05e-6, 2.05e-6, 2.05e-6]),
                              kwargs4fit={}):

        xmatrix, ymatrix = common_tools.grid_coord(thickness, pixelsize)
        r2 = np.sqrt(xmatrix**2 + ymatrix**2)
        args4fit = np.where(r2.flatten() < radius4fit)

        mask = xmatrix*np.nan
        mask[np.where(r2 < radius4fit)] = 1.0

        data2fit = thickness.flatten()[args4fit]

        xxfit = xmatrix.flatten()[args4fit]
        yyfit = ymatrix.flatten()[args4fit]

        xyfit = [xxfit, yyfit]

        # FIT

        def _2Dparabol_4_fit(xy, Radius, xo, yo, offset):
            x, y = xy
            return (x - xo) ** 2 / 2 / Radius + (y - yo) ** 2 / 2 / Radius + offset

        popt, pcov = curve_fit(_2Dparabol_4_fit, xyfit, data2fit,
                               p0=p0, bounds=bounds, method="trf",
                               **kwargs4fit)

        self.__main_logger.print_message("Nominal Parabolic 2D Fit")
        self.__main_logger.print_message("Curv Radius, xo, yo, offset")
        self.__main_logger.print_message(popt)

        self.__main_logger.print_message("Nominal Parabolic 2D Fit: Radius of 1 face  / nfaces, x direction: {:.4g} um".format(popt[0]*1e6))

        lim_x = np.argwhere(xmatrix[0, :] <= -radius4fit*1.01)[-1, 0]
        lim_y = np.argwhere(ymatrix[:, 0] <= -radius4fit*1.01)[-1, 0]

        fitted = _2Dparabol_4_fit([xmatrix, ymatrix], popt[0], popt[1], popt[2], popt[3])

        if (lim_x <= 1 or lim_y <= 1):
            thickness_cropped = thickness*mask
            fitted_cropped = fitted*mask
        else:
            thickness_cropped = (thickness[lim_y:-lim_y+1, lim_x:-lim_x+1] * mask[lim_y:-lim_y+1, lim_x:-lim_x+1])
            fitted_cropped = (fitted[lim_y:-lim_y+1, lim_x:-lim_x+1] * mask[lim_y:-lim_y+1, lim_x:-lim_x+1])

        return (thickness_cropped, fitted_cropped, popt)
