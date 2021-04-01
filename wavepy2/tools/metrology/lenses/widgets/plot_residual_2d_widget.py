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
from matplotlib.figure import Figure
from matplotlib.pyplot import cm

from wavepy2.util.common import common_tools
from wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches
from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.tools.common.widgets.plot_profile_widget import PlotProfile

from warnings import filterwarnings
filterwarnings("ignore")

class PlotResidualParabolicLens2D(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(PlotResidualParabolicLens2D, self).__init__(parent=parent, application_name=application_name)

        self.__logger  = get_registered_logger_instance(application_name=application_name)
        self.__plotter = get_registered_plotter_instance(application_name=application_name)

    def get_plot_tab_name(self): return "Residual 2D"

    def build_mpl_figure(self, **kwargs):
        thickness     = kwargs["thickness"]
        pixelsize     = kwargs["pixelsize"]
        fitted        = kwargs["fitted"]
        fitParameters = kwargs["fitParameters"]
        try:    str4title    = kwargs["str4title"]
        except: str4title = ""
        try:    saveSdfData    = kwargs["saveSdfData"]
        except: saveSdfData = False
        try:    vlimErrSigma    = kwargs["vlimErrSigma"]
        except: vlimErrSigma = 1
        try:    plot3dFlag    = kwargs["plot3dFlag"]
        except: plot3dFlag = True
        context_key = kwargs["container_context_key"]
        try:    unique_id   =  kwargs["container_unique_id"]
        except: unique_id = None
        output_data = kwargs["output_data"]

        kwargs4plots = {}

        try:
            figure_width = kwargs["figure_width"]*pixels_to_inches
            kwargs4plots["figure_width"] = kwargs["figure_width"]
        except: figure_width = 7
        try:
            figure_height = kwargs["figure_height"]*pixels_to_inches
            kwargs4plots["figure_height"] = kwargs["figure_height"]
        except: figure_height = 8

        xmatrix, ymatrix = common_tools.grid_coord(thickness, pixelsize)

        errorThickness = thickness - fitted
        argNotNAN = np.isfinite(errorThickness)

        factorx, unitx = common_tools.choose_unit(xmatrix)
        factory, unity = common_tools.choose_unit(ymatrix)
        factorz, unitz = common_tools.choose_unit(errorThickness[argNotNAN])

        ptp = np.ptp(errorThickness[argNotNAN].flatten() * factorz)
        self.__logger.print_message("PV: {0:4.3g} ".format(ptp) + unitz[-1] + "m")

        sigmaError = np.std(errorThickness[argNotNAN].flatten() * factorz)
        self.__logger.print_message("SDV: {0:4.3g} ".format(sigmaError) + unitz[-1] + "m")

        str4title += r" Residual, R $= {:.4g} \mu m$,".format(fitParameters[0] * 1e6) + "\n" + \
                     r"PV $= {0:.2f}$ ".format(ptp) + "$" + unitz + "  m$, SDV $= {0:.2f}$ ".format(sigmaError) + "$" + unitz + "  m$"

        # Plot Histogram

        fig = Figure(figsize=(figure_width, figure_height))
        fig.gca().hist(errorThickness[argNotNAN] * factorz, 100, color="r", histtype="step")
        fig.gca().set_xlabel(r"Residual [$" + unitz + "  m$ ]")
        fig.gca().set_title(str4title)

        # Plot Profiles

        vlimErr = common_tools.mean_plus_n_sigma(errorThickness[argNotNAN] * factorz, vlimErrSigma / 2)
        cmap4graph = cm.Spectral_r
        cmap4graph.set_over("m")
        cmap4graph.set_under("c")

        self.__plotter.push_plot_on_context(context_key, PlotProfile, unique_id,
                                            xmatrix=xmatrix * factorx,
                                            ymatrix=ymatrix * factory,
                                            zmatrix=errorThickness * factorz,
                                            title="Residual",
                                            str4title=str4title,
                                            xlabel=r"[$" + unitx + "  m$ ]",
                                            ylabel=r"[$" + unity + "  m$ ]",
                                            zlabel=r"[$" + unitz + "  m$ ]",
                                            arg4main={"cmap": "Spectral_r",
                                                      "vmin": -vlimErr,
                                                      "vmax": vlimErr,
                                                      "extend": "both"},
                                            **kwargs4plots)

        self.__plotter.push_plot_on_context(context_key, CountourPlot, unique_id,
                                            xmatrix=xmatrix * factorx,
                                            ymatrix=ymatrix * factory,
                                            zmatrix=errorThickness * factorz,
                                            str4title=str4title,
                                            unitx=unitx,
                                            unity=unity,
                                            unitz=unitz,
                                            vlimErr=vlimErr,
                                            cmap4graph=cmap4graph,
                                            **kwargs4plots)

        # Plot 3D

        if plot3dFlag:
            self.__plotter.push_plot_on_context(context_key, Plot3D, unique_id,
                                                xmatrix=xmatrix[argNotNAN].flatten() * factorx,
                                                ymatrix=ymatrix[argNotNAN].flatten() * factory,
                                                zmatrix=errorThickness[argNotNAN].flatten() * factorz,
                                                str4title=str4title,
                                                unitx=unitx,
                                                unity=unity,
                                                unitz=unitz,
                                                vlimErr=vlimErr,
                                                cmap4graph=cmap4graph,
                                                **kwargs4plots)

        if saveSdfData:
            mask_for_sdf = errorThickness * 0.0
            mask_for_sdf[~argNotNAN] = 1.0
            errorThickness[~argNotNAN] = 00000000

            self.__plotter.save_sdf_file(errorThickness, pixelsize, file_suffix="_residual")
            self.__plotter.save_sdf_file(mask_for_sdf, pixelsize, file_suffix="_residual_mask")

        output_data["sigma"] = sigmaError / factorz
        output_data["pv"]    = ptp / factorz

        return fig


class CountourPlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Residual 2D - Countour"

    def build_mpl_figure(self, **kwargs):
        xmatrix    = kwargs["xmatrix"]
        ymatrix    = kwargs["ymatrix"]
        zmatrix    = kwargs["zmatrix"]
        str4title   = kwargs["str4title"]
        unitx      = kwargs["unitx"]
        unity      = kwargs["unity"]
        unitz      = kwargs["unitz"]
        vlimErr    = kwargs["vlimErr"]
        cmap4graph = kwargs["cmap4graph"]

        try:    figure_width = kwargs["figure_width"]*pixels_to_inches
        except: figure_width = 10
        try:    figure_height = kwargs["figure_height"]*pixels_to_inches
        except: figure_height = 7

        fig = Figure(figsize=(figure_width, figure_height))

        cf = fig.gca().contourf(xmatrix,
                                ymatrix ,
                                zmatrix, 256,
                                cmap=cmap4graph,
                                extend="both")

        cf.set_clim(-vlimErr, vlimErr)
        fig.gca().contour(cf, levels=cf.levels[::32], colors="gray")

        fig.gca().set_xlabel(r"[$" + unitx + "  m$ ]", fontsize=22)
        fig.gca().set_ylabel(r"[$" + unity + "  m$ ]", fontsize=22)
        fig.gca().set_title(str4title, fontsize=22)
        cbar = fig.colorbar(cf, shrink=.8, aspect=20)
        cbar.ax.set_title(r"[$" + unitz + "  m$ ]", y=1.01)

        fig.gca().set_aspect("equal", adjustable="box")
        fig.gca().grid(color="grey")

        return fig


class Plot3D(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(Plot3D, self).__init__(parent=parent, application_name=application_name)

        self.__logger  = get_registered_logger_instance(application_name=application_name)

    def get_plot_tab_name(self): return "Residual 2D - Plot 3D"

    def build_mpl_figure(self, **kwargs):
        xmatrix    = kwargs["xmatrix"]
        ymatrix    = kwargs["ymatrix"]
        zmatrix    = kwargs["zmatrix"]
        str4title   = kwargs["str4title"]
        unitx      = kwargs["unitx"]
        unity      = kwargs["unity"]
        unitz      = kwargs["unitz"]
        vlimErr    = kwargs["vlimErr"]
        cmap4graph = kwargs["cmap4graph"]

        try:    figure_width = kwargs["figure_width"]*pixels_to_inches
        except: figure_width = 10
        try:    figure_height = kwargs["figure_width"]*pixels_to_inches
        except: figure_height = 7

        self.__logger.print_message("Plotting 3d in the background")

        fig = Figure(figsize=(figure_width, figure_height), facecolor="white")
        ax = fig.gca(projection="3d")
        fig.tight_layout(pad=2.5)

        surf = ax.plot_trisurf(xmatrix,
                               ymatrix,
                               zmatrix,
                               vmin=-vlimErr, vmax=vlimErr,
                               cmap=cmap4graph, linewidth=0.1, shade=False)

        ax.view_init(azim=-120, elev=40)

        ax.set_xlabel(r"$x$ [$" + unitx + "  m$ ]")
        ax.set_ylabel(r"$y$ [$" + unity + "  m$ ]")

        ax.set_title(str4title)

        cbar = fig.colorbar(surf, shrink=.8, aspect=20, extend="both")
        cbar.ax.set_title(r"[$" + unitz + "  m$ ]", y=1.01)

        fig.tight_layout()

        ax.view_init(azim=690, elev=40)

        return fig
