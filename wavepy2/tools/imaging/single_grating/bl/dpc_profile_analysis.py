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
import os

from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core import grating_interferometry
from wavepy2.core.widgets.plot_intensities_harms import PlotIntensitiesHarms
from wavepy2.core.widgets.plot_dark_field import PlotDarkField
from wavepy2.tools.imaging.single_grating.widgets.plot_DPC_widget import PlotDPC

from wavepy2.tools.imaging.single_grating.widgets.input_parameters_widget import InputParametersWidget, generate_initialization_parameters
from wavepy2.tools.imaging.single_grating.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.tools.imaging.single_grating.widgets.second_crop_dialog_widget import SecondCropDialogPlot
from wavepy2.tools.imaging.single_grating.widgets.show_cropped_figure_widget import ShowCroppedFigure
from wavepy2.tools.imaging.single_grating.widgets.correct_DPC_widgets import CorrectDPC, CorrectDPCHistos, CorrectDPCCenter

from wavepy2.util.common.common_tools import hc

class DPCProfileAnalysisFacade():
    @classmethod
    def dpc_profile_analysis(cls, dpc_data): raise NotImplementedError()


def create_dpc_profile_analsysis_manager():
    return __DPCProfileAnalysis()

DPC_PROFILE_ANALYSYS_CONTEXT_KEY = "DPC Profile Analysis"

class __DPCProfileAnalysis(DPCProfileAnalysisFacade):
    @classmethod
    def dpc_profile_analysis(cls, dpc_profile_analysis_data, initialization_parameters):
        phenergy          = initialization_parameters.get_parameter("phenergy")

        diffPhaseH        = dpc_profile_analysis_data.get_parameter("diffPhaseH", None)
        diffPhaseV        = dpc_profile_analysis_data.get_parameter("diffPhaseV", None)
        virtual_pixelsize = dpc_profile_analysis_data.get_parameter("virtual_pixelsize")

        fnameH            = dpc_profile_analysis_data.get_parameter("fnameH", None)
        fnameV            = dpc_profile_analysis_data.get_parameter("fnameV", None)
        grazing_angle     = dpc_profile_analysis_data.get_parameter("grazing_angle", 0.0)
        projectionFromDiv = dpc_profile_analysis_data.get_parameter("projectionFromDiv", 1.0)
        nprofiles         = dpc_profile_analysis_data.get_parameter("nprofiles", 1)
        remove1stOrderDPC = dpc_profile_analysis_data.get_parameter("remove1stOrderDPC", False)
        remove2ndOrder    = dpc_profile_analysis_data.get_parameter("remove2ndOrder", False)
        filter_width      = dpc_profile_analysis_data.get_parameter("nprofiles", 0)

        wavelength = hc/phenergy

        main_logger   = get_registered_logger_instance()
        script_logger = get_registered_secondary_logger()

        if fnameH is None: diffPhaseH = diffPhaseV*np.nan

        if fnameV is None:
            diffPhaseV = diffPhaseH*np.nan
            saveFileSuf = fnameH.rsplit('/', 1)[0] + '/profiles/' + fnameH.rsplit('/', 1)[1]
            saveFileSuf = saveFileSuf.rsplit('_X')[0] + '_profiles'
        else:
            saveFileSuf = fnameV.rsplit('/', 1)[0] + '/profiles/' + fnameV.rsplit('/', 1)[1]
            saveFileSuf = saveFileSuf.rsplit('_Y')[0] + '_profiles'

        if not os.path.exists(saveFileSuf.rsplit('/', 1)[0]): os.makedirs(saveFileSuf.rsplit('/', 1)[0])

        n_profiles_H_V_result = cls.__n_profiles_H_V(WavePyData(arrayH=diffPhaseH,
                                                                arrayV=diffPhaseV,
                                                                virtual_pixelsize=virtual_pixelsize,
                                                                zlabel='DPC [rad/m]',
                                                                titleH='WF DPC Horz',
                                                                titleV='WF DPC Vert',
                                                                saveFileSuf=saveFileSuf,
                                                                nprofiles=nprofiles,
                                                                remove1stOrderDPC=remove1stOrderDPC,
                                                                filter_width=filter_width))

        dataH     = n_profiles_H_V_result.get_parameter("dataH")
        dataV     = n_profiles_H_V_result.get_parameter("dataV")
        labels_H  = n_profiles_H_V_result.get_parameter("labels_H")
        labels_V  = n_profiles_H_V_result.get_parameter("labels_V")
        fit_coefs = n_profiles_H_V_result.get_parameter("fit_coefs")

        fit_coefsH = np.array(fit_coefs[0])
        fit_coefsV = np.array(fit_coefs[1])

        if fnameH is not None:
            radii_fit_H = (2*np.pi/wavelength/fit_coefsH[:][0])

            main_logger.print_message('Radius H from fit profiles: ')
            script_logger.print('radius fit Hor = ' + str(radii_fit_H))

            integratedH = cls.__integrate_DPC_cumsum(WavePyData(data_DPC=dataH,
                                                                wavelength=wavelength,
                                                                remove2ndOrder=remove2ndOrder,
                                                                xlabel='x',
                                                                labels=labels_H,
                                                                titleStr='Horizontal, ',
                                                                saveFileSuf=saveFileSuf + '_X'))

            curv_H = cls.__curv_from_height(height=integratedH,
                                            virtual_pixelsize=virtual_pixelsize[0],
                                            xlabel='x',
                                            labels=labels_H,
                                            titleStr='Horizontal, ',
                                            saveFileSuf=saveFileSuf + '_X')

        if fnameV is not None:
            radii_fit_V = (2*np.pi/wavelength/fit_coefsV[:][0])

            main_logger.print_message('Radius V from fit profiles: ')
            script_logger.print('radius fit Vert = ' + str(radii_fit_V))

            integratedV = cls.__integrate_DPC_cumsum(WavePyData(data_DPC=dataV,
                                                                wavelength=wavelength,
                                                                remove2ndOrder=remove2ndOrder,
                                                                xlabel='y',
                                                                labels=labels_V,
                                                                titleStr='Vertical, ',
                                                                saveFileSuf=saveFileSuf + '_Y'))

            curv_V = cls.__curv_from_height(height=integratedV,
                                            virtual_pixelsize=virtual_pixelsize[1],
                                            xlabel='y',
                                            labels=labels_V,
                                            titleStr='Vertical, ',
                                            saveFileSuf=saveFileSuf + '_Y')

    @classmethod
    def ___n_profiles_H_V(cls, n_profiles_H_V_data=WavePyData()):
        arrayH = n_profiles_H_V_data.get_parameter("arrayH")
        arrayV = n_profiles_H_V_data.get_parameter("arrayV")
        virtual_pixelsize = n_profiles_H_V_data.get_parameter("virtual_pixelsize")
        zlabel = n_profiles_H_V_data.get_parameter("zlabel")
        titleH = n_profiles_H_V_data.get_parameter("data_DPC")
        titleV = n_profiles_H_V_data.get_parameter("titleH")
        saveFileSuf = n_profiles_H_V_data.get_parameter("saveFileSuf")
        nprofiles = n_profiles_H_V_data.get_parameter("nprofiles")
        remove1stOrderDPC = n_profiles_H_V_data.get_parameter("remove1stOrderDPC")
        filter_width = n_profiles_H_V_data.get_parameter("filter_width")

        xxGrid, yyGrid = common_tools.grid_coord(arrayH, virtual_pixelsize)

        fit_coefs = [[], []]
        data2saveH = None
        data2saveV = None
        labels_H = None
        labels_V = None

        #plt.rcParams['lines.markersize'] = 4
        #plt.rcParams['lines.linewidth'] = 2

        # Horizontal
        if np.all(np.isfinite(arrayH)):
            pass


        return WavePyData(dataH=data2saveH,
                          dataV=data2saveV,
                          labels_H=labels_H,
                          labels_V=labels_V,
                          fit_coefs=fit_coefs)

    @classmethod
    def ___integrate_DPC_cumsum(cls, integrate_DPC_cumsum_data=WavePyData()):
        data_DPC = integrate_DPC_cumsum_data.get_parameter("data_DPC")
        wavelength = integrate_DPC_cumsum_data.get_parameter("wavelength")
        remove2ndOrder = integrate_DPC_cumsum_data.get_parameter("remove2ndOrder")
        xlabel = integrate_DPC_cumsum_data.get_parameter("xlabel")
        labels = integrate_DPC_cumsum_data.get_parameter("labels")
        titleStr = integrate_DPC_cumsum_data.get_parameter("titleStr")
        saveFileSuf = integrate_DPC_cumsum_data.get_parameter("saveFileSuf")

        list_integrated = None

        return np.asarray(list_integrated).T

    @classmethod
    def ___curv_from_height(cls, curv_from_height_data=WavePyData()):
        height = curv_from_height_data.get_parameter("height")
        virtual_pixelsize = curv_from_height_data.get_parameter("virtual_pixelsize")
        xlabel = curv_from_height_data.get_parameter("xlabel")
        labels = curv_from_height_data.get_parameter("labels")
        titleStr = curv_from_height_data.get_parameter("titleStr")
        saveFileSuf = curv_from_height_data.get_parameter("saveFileSuf")

        list_curv = None

        return np.asarray(list_curv).T

'''
# %%
def _n_profiles_H_V(arrayH, arrayV, virtual_pixelsize,
                    zlabel=r'z',
                    titleH='Horiz', titleV='Vert',
                    nprofiles=5, filter_width=0,
                    remove1stOrderDPC=False,
                    saveFileSuf='',
                    saveFigFlag=True):

    xxGrid, yyGrid = wpu.grid_coord(arrayH, virtual_pixelsize)

    fit_coefs = [[], []]
    data2saveH = None
    data2saveV = None
    labels_H = None
    labels_V = None

    plt.rcParams['lines.markersize'] = 4
    plt.rcParams['lines.linewidth'] = 2

    # Horizontal
    if np.all(np.isfinite(arrayH)):

        plt.figure(figsize=(12, 12*9/16))

        xvec = xxGrid[0, :]
        data2saveH = np.c_[xvec]
        header = ['x [m]']

        if filter_width != 0:
            arrayH_filtered = uniform_filter1d(arrayH, filter_width, 0)
        else:
            arrayH_filtered = arrayH

        ls_cycle, lc_jet = wpu.line_style_cycle(['-'], ['o', 's', 'd', '^'],
                                                ncurves=nprofiles,
                                                cmap_str='gist_rainbow_r')

        lc = []
        labels_H = []
        for i, row in enumerate(np.linspace(filter_width//2,
                                            np.shape(arrayV)[0]-filter_width//2-1,
                                            nprofiles + 2, dtype=int)):

            if i == 0 or i == nprofiles + 1:
                continue

            yvec = arrayH_filtered[row, :]

            lc.append(next(lc_jet))
            p01 = np.polyfit(xvec, yvec, 1)
            fit_coefs[0].append(p01)

            if remove1stOrderDPC:
                yvec -= p01[0]*xvec + p01[1]

            plt.plot(xvec*1e6, yvec, next(ls_cycle), color=lc[i-1],
                     label=str(row))

            if not remove1stOrderDPC:
                plt.plot(xvec*1e6, p01[0]*xvec + p01[1], '--',
                         color=lc[i-1], lw=3)

            data2saveH = np.c_[data2saveH, yvec]
            header.append(str(row))
            labels_H.append(str(row))

        if remove1stOrderDPC:
            titleH = titleH + ', 2nd order removed'
        plt.legend(title='Pixel Y', loc=0, fontsize=12)

        plt.xlabel(r'x [$\mu m$]', fontsize=18)
        plt.ylabel(zlabel, fontsize=18)
        plt.title(titleH + ', Filter Width = {:d} pixels'.format(filter_width),
                  fontsize=20)

        if saveFigFlag:
            wpu.save_figs_with_idx(saveFileSuf + '_H')

        plt.show(block=False)

        header.append(zlabel + ', Filter Width = {:d} pixels'.format(filter_width))

        wpu.save_csv_file(data2saveH,
                          wpu.get_unique_filename(saveFileSuf +
                                                  '_WF_profiles_H', 'csv'),
                          headerList=header)

        plt.figure(figsize=(12, 12*9/16))
        plt.imshow(arrayH, cmap='RdGy',
                   vmin=wpu.mean_plus_n_sigma(arrayH, -3),
                   vmax=wpu.mean_plus_n_sigma(arrayH, 3))
        plt.xlabel('Pixel')
        plt.ylabel('Pixel')
        plt.title(titleH + ', Profiles Position')

        currentAxis = plt.gca()

        _, lc_jet = wpu.line_style_cycle(['-'], ['o', 's', 'd', '^'],
                                         ncurves=nprofiles,
                                         cmap_str='gist_rainbow_r')

        for i, row in enumerate(np.linspace(filter_width//2,
                                            np.shape(arrayV)[0]-filter_width//2-1,
                                            nprofiles + 2, dtype=int)):

            if i == 0 or i == nprofiles + 1:
                continue

            currentAxis.add_patch(Rectangle((-.5, row - filter_width//2 - .5),
                                            np.shape(arrayH)[1], filter_width,
                                            facecolor=lc[i-1], alpha=.5))
            plt.axhline(row, color=lc[i-1])

        if saveFigFlag:
            wpu.save_figs_with_idx(saveFileSuf + '_H')

        plt.show(block=True)

    # Vertical
    if np.all(np.isfinite(arrayV)):

        plt.figure(figsize=(12, 12*9/16))

        xvec = yyGrid[:, 0]
        data2saveV = np.c_[xvec]
        header = ['y [m]']

        if filter_width != 0:
            arrayV_filtered = uniform_filter1d(arrayV, filter_width, 1)
        else:
            arrayV_filtered = arrayV

        ls_cycle, lc_jet = wpu.line_style_cycle(['-'], ['o', 's', 'd', '^'],
                                                ncurves=nprofiles,
                                                cmap_str='gist_rainbow_r')

        lc = []
        labels_V = []
        for i, col in enumerate(np.linspace(filter_width//2,
                                            np.shape(arrayH)[1]-filter_width//2-1,
                                            nprofiles + 2, dtype=int)):

            if i == 0 or i == nprofiles + 1:
                continue

            yvec = arrayV_filtered[:, col]

            lc.append(next(lc_jet))
            p10 = np.polyfit(xvec, yvec, 1)
            fit_coefs[1].append(p10)

            if remove1stOrderDPC:
                yvec -= p10[0]*xvec + p10[1]

            plt.plot(xvec*1e6, yvec, next(ls_cycle), color=lc[i-1],
                     label=str(col))

            if not remove1stOrderDPC:
                plt.plot(xvec*1e6, p10[0]*xvec + p10[1], '--',
                         color=lc[i-1], lw=3)

            data2saveV = np.c_[data2saveV, yvec]
            header.append(str(col))
            labels_V.append(str(col))

        if remove1stOrderDPC:
            titleV = titleV + ', 2nd order removed'

        plt.legend(title='Pixel X', loc=0, fontsize=12)

        plt.xlabel(r'y [$\mu m$]', fontsize=18)
        plt.ylabel(zlabel, fontsize=18)

        plt.title(titleV + ', Filter Width = {:d} pixels'.format(filter_width),
                  fontsize=20)
        if saveFigFlag:
            wpu.save_figs_with_idx(saveFileSuf + '_Y')
        plt.show(block=False)

        header.append(zlabel + ', Filter Width = {:d} pixels'.format(filter_width))

        wpu.save_csv_file(data2saveV,
                          wpu.get_unique_filename(saveFileSuf +
                                                  '_WF_profiles_V', 'csv'),
                          headerList=header)

        plt.figure(figsize=(12, 12*9/16))
        plt.imshow(arrayV, cmap='RdGy',
                   vmin=wpu.mean_plus_n_sigma(arrayV, -3),
                   vmax=wpu.mean_plus_n_sigma(arrayV, 3))
        plt.xlabel('Pixel')
        plt.ylabel('Pixel')
        plt.title(titleV + ', Profiles Position')

        currentAxis = plt.gca()

        for i, col in enumerate(np.linspace(filter_width//2,
                                            np.shape(arrayH)[1]-filter_width//2-1,
                                            nprofiles + 2, dtype=int)):

            if i == 0 or i == nprofiles + 1:
                continue


            currentAxis.add_patch(Rectangle((col - filter_width//2 - .5, -.5),
                                            filter_width, np.shape(arrayV)[0],
                                            facecolor=lc[i-1], alpha=.5))
            plt.axvline(col, color=lc[i-1])

        if saveFigFlag:
            wpu.save_figs_with_idx(saveFileSuf + '_Y')

        plt.show(block=True)

    return data2saveH, data2saveV, labels_H, labels_V, fit_coefs


'''
