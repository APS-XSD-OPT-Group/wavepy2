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
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger, \
    register_secondary_logger, LoggerMode

from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.plot.plot_tools import PlottingProperties

from wavepy2.tools.common.wavepy_data import WavePyData
from wavepy2.tools.common import physical_properties 
from wavepy2.tools.common.bl import crop_image

from wavepy2.tools.common.widgets.plot_profile_widget import PlotProfile
from wavepy2.tools.common.widgets.simple_plot_widget import SimplePlot
from wavepy2.tools.metrology.lenses.widgets.frl_input_parameters_widget import FRLInputParametersWidget, FRLInputParametersDialog, \
    generate_initialization_parameters_frl, LENS_GEOMETRIES
from wavepy2.tools.metrology.lenses.widgets.fit_radius_dpc_widget import FitRadiusDPC
from wavepy2.tools.metrology.lenses.widgets.plot_residual_1d_widget import PlotResidual1D
from wavepy2.tools.metrology.lenses.widgets.plot_residual_2d_widget import PlotResidualParabolicLens2D
from wavepy2.tools.metrology.lenses.widgets.slope_error_hist_widget import SlopeErrorHist

class FitResidualLensesFacade:
    def draw_initialization_parameters_widget(self, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def get_initialization_parameters(self, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def manager_initialization(self, initialization_parameters, script_logger_mode=LoggerMode.FULL, show_fourier=False): raise NotImplementedError()

    def draw_crop_thickness(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def manage_crop_thickness(self, crop_thickness_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError
    def crop_thickness(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()

    def center_image(self, crop_thickness_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def fit_radius_dpc(self, center_image_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()
    def do_fit(self, fit_radius_dpc_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs): raise NotImplementedError()

def create_fit_residual_lenses_manager():
    return __FitResidualLenses()

APPLICATION_NAME = "Fit Residual Lenses"

INITIALIZATION_PARAMETERS_KEY = APPLICATION_NAME + " Initialization"
CROP_THICKNESS_CONTEXT_KEY = "Crop and Show Thickness"
CENTER_IMAGE_CONTEXT_KEY = "Center Image"
FIT_RADIUS_DPC_CONTEXT_KEY = "Fit Radius DPC"
DO_FIT_CONTEXT_KEY = "Do fit"

class __FitResidualLenses(FitResidualLensesFacade):

    def __init__(self):
        self.__plotter     = get_registered_plotter_instance(application_name=APPLICATION_NAME)
        self.__main_logger = get_registered_logger_instance(application_name=APPLICATION_NAME)
        self.__ini         = get_registered_ini_instance(application_name=APPLICATION_NAME)

    # %% ==================================================================================================

    def draw_initialization_parameters_widget(self, plotting_properties=PlottingProperties(), **kwargs):
        if self.__plotter.is_active():
            show_runtime_options = plotting_properties.get_parameter("show_runtime_options", True)
            add_context_label    = plotting_properties.get_parameter("add_context_label", True)
            use_unique_id        = plotting_properties.get_parameter("use_unique_id", False)

            unique_id = self.__plotter.register_context_window(INITIALIZATION_PARAMETERS_KEY,
                                                               context_window=plotting_properties.get_context_widget(),
                                                               use_unique_id=use_unique_id)

            self.__plotter.push_plot_on_context(INITIALIZATION_PARAMETERS_KEY, FRLInputParametersWidget, unique_id, show_runtime_options=show_runtime_options, **kwargs)
            self.__plotter.draw_context(INITIALIZATION_PARAMETERS_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

            return self.__plotter.get_plots_of_context(INITIALIZATION_PARAMETERS_KEY, unique_id=unique_id)
        else:
            return None

    def get_initialization_parameters(self, plotting_properties=PlottingProperties(), **kwargs):
        if self.__plotter.is_active():
            initialization_parameters = self.__plotter.show_interactive_plot(FRLInputParametersDialog,
                                                                             container_widget=plotting_properties.get_container_widget(),
                                                                             show_runtime_options=plotting_properties.get_parameter("show_runtime_options", True),
                                                                             **kwargs)
        else:
            initialization_parameters = generate_initialization_parameters_frl(thickness_file_name=self.__ini.get_string_from_ini("Files", "file with thickness"),
                                                                               str4title=self.__ini.get_string_from_ini("Parameters", "String for Titles", default="Be Lens"),
                                                                               nominalRadius=self.__ini.get_float_from_ini("Parameters", "nominal radius for fitting", default=1e-4),
                                                                               diameter4fit_str=self.__ini.get_string_from_ini("Parameters", "diameter of active area for fitting", default="800"),
                                                                               lensGeometry=self.__ini.get_string_from_ini("Parameters", "lens geometry", default=LENS_GEOMETRIES[2]),
                                                                               phenergy= self.__ini.get_float_from_ini("Parameters", "photon energy", default=14000.0),
                                                                               crop_image=self.__ini.get_boolean_from_ini("Runtime", "crop image", default=False),
                                                                               fit_radius_dpc=self.__ini.get_boolean_from_ini("Runtime", "fit radius dpc", default=False))

        return initialization_parameters

    def manager_initialization(self, initialization_parameters, script_logger_mode=LoggerMode.FULL):
        self.__plotter.register_save_file_prefix(initialization_parameters.get_parameter("saveFileSuf"))

        if not script_logger_mode == LoggerMode.NONE: stream = open(self.__plotter.get_save_file_prefix() + "_" + common_tools.datetime_now_str() + ".log", "wt")
        else: stream = None

        register_secondary_logger(stream=stream, logger_mode=script_logger_mode, application_name=APPLICATION_NAME)

        self.__wavelength = hc / initialization_parameters.get_parameter("phenergy")
        self.__kwave = 2 * np.pi / self.__wavelength

        self.__script_logger = get_registered_secondary_logger(application_name=APPLICATION_NAME)

        return initialization_parameters



    # %% ==================================================================================================

    def draw_crop_thickness(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        crop_thickness = initialization_parameters.get_parameter("crop_image")
        thickness      = initialization_parameters.get_parameter("thickness")

        if crop_thickness:
            thickness_to_crop = np.copy(thickness)
            thickness_to_crop[np.isnan(thickness)] = 0.0
            thickness_to_crop *= 1e6

            return crop_image.draw_crop_image(img=thickness_to_crop,
                                              plotting_properties=plotting_properties,
                                              application_name=APPLICATION_NAME,
                                              message="Crop Thickness",
                                              **kwargs)
        else:
            return None

    def manage_crop_thickness(self, crop_thickness_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(CROP_THICKNESS_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        crop_thickness = initialization_parameters.get_parameter("crop_image")
        thickness      = initialization_parameters.get_parameter("thickness")
        xx             = initialization_parameters.get_parameter("xx")
        yy             = initialization_parameters.get_parameter("yy")

        if crop_thickness:
            idx4crop = crop_thickness_result.get_parameter("idx4crop", [0, -1, 0, -1])

            thickness = common_tools.crop_matrix_at_indexes(thickness, idx4crop)
            xx = common_tools.crop_matrix_at_indexes(xx, idx4crop)
            yy = common_tools.crop_matrix_at_indexes(yy, idx4crop)

            stride = thickness.shape[0] // 125

            self.__plotter.push_plot_on_context(CROP_THICKNESS_CONTEXT_KEY, PlotProfile, unique_id,
                                                xmatrix=xx[::stride, ::stride] * 1e6,
                                                ymatrix=yy[::stride, ::stride] * 1e6,
                                                zmatrix=thickness[::stride, ::stride] * 1e6,
                                                xlabel=r"$x$ [$\mu m$ ]",
                                                ylabel=r"$y$ [$\mu m$ ]",
                                                zlabel=r"$z$ [$\mu m$ ]",
                                                arg4main={"cmap": "Spectral_r"},
                                                **kwargs)

        self.__plotter.draw_context(CROP_THICKNESS_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(thickness=thickness, xx=xx, yy=yy)

    def crop_thickness(self, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        crop_thickness = initialization_parameters.get_parameter("crop_image")
        thickness      = initialization_parameters.get_parameter("thickness")

        if crop_thickness and  self.__plotter.is_active():
            thickness_to_crop = np.copy(thickness)
            thickness_to_crop[np.isnan(thickness)] = 0.0
            thickness_to_crop *= 1e6

            _, idx4crop, _ = crop_image.crop_image(img=thickness_to_crop,
                                                   plotting_properties=plotting_properties,
                                                   application_name=APPLICATION_NAME,
                                                   message="Crop Thickness",
                                                   **kwargs)

        else:
            idx4crop= [0, -1, 0, -1]

        return self.manage_crop_thickness(WavePyData(idx4crop=idx4crop), initialization_parameters, plotting_properties, **kwargs)


    # %% ==================================================================================================

    def center_image(self, crop_thickness_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(CENTER_IMAGE_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

        pixelsize = initialization_parameters.get_parameter("pixelsize")

        thickness = crop_thickness_result.get_parameter("thickness")
        xx        = crop_thickness_result.get_parameter("xx")
        yy        = crop_thickness_result.get_parameter("yy")

        # %% Center image
        radius4centering = np.min(thickness.shape) * np.min(pixelsize) * .75
        thickness = self.__center_lens_array_max_fit(thickness, pixelsize, radius4centering)

        self.__plotter.push_plot_on_context(CENTER_IMAGE_CONTEXT_KEY, SimplePlot, unique_id,
                                            img=thickness * 1e6,
                                            pixelsize=pixelsize,
                                            title="Thickness",
                                            xlabel=r"$x$ [$\mu m$ ]",
                                            ylabel=r"$y$ [$\mu m$ ]", **kwargs)

        self.__script_logger.print("Array cropped to have the max at the center of the array")

        text2datfile = "# file name, Type of Fit, Curved Radius from fit [um],"
        text2datfile += " diameter4fit [um], sigma [um], pv [um]\n"

        self.__plotter.draw_context(CENTER_IMAGE_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(thickness=thickness, xx=xx, yy=yy, text2datfile=text2datfile)

    def fit_radius_dpc(self, center_image_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(FIT_RADIUS_DPC_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

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

                self.__plotter.push_plot_on_context(FIT_RADIUS_DPC_CONTEXT_KEY, FitRadiusDPC, unique_id,
                                                    dpx=dpx,
                                                    dpy=dpy,
                                                    pixelsize=pixelsize_dpc,
                                                    radius4fit=np.min((-xx[0, 0], xx[-1, -1], -yy[0, 0], yy[-1, -1])) * 0.9,
                                                    kwave=self.__kwave,
                                                    str4title="", **kwargs)

        self.__plotter.draw_context(FIT_RADIUS_DPC_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData(thickness=thickness, xx=xx, yy=yy, text2datfile=text2datfile)

    def do_fit(self, fit_radius_dpc_result, initialization_parameters, plotting_properties=PlottingProperties(), **kwargs):
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = self.__plotter.register_context_window(DO_FIT_CONTEXT_KEY,
                                                           context_window=plotting_properties.get_context_widget(),
                                                           use_unique_id=use_unique_id)

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
            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, PlotResidual1D, unique_id,
                                                xvec=xmatrix[0, isNotNAN],
                                                data=thickness_cropped[thickness_cropped.shape[0] // 2, isNotNAN],
                                                fitted=fitted[thickness_cropped.shape[0] // 2, isNotNAN],
                                                direction="Horizontal",
                                                str4title=str4graphs +
                                                          "\nFit center profile Horizontal, " +
                                                          " R = {:.4g} um".format(fitParameters[0] * 1e6),
                                                saveAscii=True, **kwargs)


            isNotNAN = np.isfinite(thickness_cropped[:, thickness_cropped.shape[1]//2])
            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, PlotResidual1D, unique_id,
                                                xvec=ymatrix[isNotNAN, 0],
                                                data=thickness_cropped[isNotNAN, thickness_cropped.shape[1]//2],
                                                fitted=fitted[isNotNAN, thickness_cropped.shape[1]//2],
                                                direction="Vertical",
                                                str4title=str4graphs +
                                                          "\nFit center profile Vertical, " +
                                                          r" R = {:.4g} $\mu m$".format(fitParameters[0] * 1e6),
                                                saveAscii=True, **kwargs)

            output_data = {}

            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, PlotResidualParabolicLens2D, unique_id,
                                                thickness=thickness_cropped,
                                                pixelsize=pixelsize,
                                                fitted=fitted,
                                                fitParameters=fitParameters,
                                                str4title=str4graphs,
                                                saveSdfData=True,
                                                vlimErrSigma=4,
                                                plot3dFlag=True,
                                                output_data=output_data,
                                                container_context_key=DO_FIT_CONTEXT_KEY,
                                                container_unique_id=unique_id,
                                                **kwargs)

            sigma = output_data["sigma"]
            pv = output_data["pv"]
     
            material = "C"
            delta_lens, _, _ = physical_properties.get_delta(phenergy, material=material)
            
            self.__plotter.push_plot_on_context(DO_FIT_CONTEXT_KEY, SlopeErrorHist, unique_id,
                                                thickness=thickness_cropped,
                                                pixelsize=pixelsize,
                                                fitted=fitted,
                                                delta=delta_lens,
                                                str4title=str4graphs + " " + str(phenergy/1000) + " KeV, " + material,
                                                output_data={}, **kwargs)

            text2datfile += self.__plotter.get_save_file_prefix()
            text2datfile += ",\t Nominal"
            text2datfile += ",\t{:.4g},\t{:.4g}".format(fitParameters[0]*1e6, diameter4fit*1e6)
            text2datfile += ",\t{:.4g},\t{:.4g}\n".format(sigma*1e6, pv*1e6)

        fname_summary = self.__plotter.get_save_file_prefix() + "_2D_summary.csv"
        text_file = open(fname_summary, "w")
        text_file.write(text2datfile)
        text_file.close()
        self.__main_logger.print_message("Data saved at " + fname_summary)

        self.__plotter.draw_context(DO_FIT_CONTEXT_KEY, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return WavePyData()

    ###################################################################
    # PRIVATE METHODS

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
