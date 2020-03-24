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
from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.io.read_write_file import read_tiff
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core import grating_interferometry
from wavepy2.tools.imaging.single_grating.widgets.input_parameters_widget import InputParametersWidget
from wavepy2.tools.imaging.single_grating.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.tools.imaging.single_grating.widgets.show_cropped_figure_widget import ShowCroppedFigure

from scipy import constants

hc = constants.value('inverse meter-electron volt relationship')  # hc

CALCULATE_DPC_CONTEXT_KEY = "Calculate DPC"

def get_initialization_parameters():
    plotter = get_registered_plotter_instance()

    if plotter.is_active():
        return plotter.show_interactive_plot(InputParametersWidget, container_widget=None)
    else:
        ini = get_registered_ini_instance()

        img = ini.get_string_from_ini("Files", "sample")
        imgRef = ini.get_string_from_ini("Files", "reference")
        imgBlank = ini.get_string_from_ini("Files", "blank")

        mode = ini.get_string_from_ini("Parameters", "mode")
        pixel = ini.get_float_from_ini("Parameters", "pixel size")
        pixelsize = [pixel, pixel]
        gratingPeriod = ini.get_float_from_ini("Parameters", "checkerboard grating period")
        pattern = ini.get_string_from_ini("Parameters", "pattern")
        distDet2sample = ini.get_float_from_ini("Parameters", "distance detector to gr")
        phenergy = ini.get_float_from_ini("Parameters", "photon energy")
        sourceDistance = ini.get_float_from_ini("Parameters", "source distance")

        img = read_tiff(img)
        imgRef = None if (mode == 'Relative' or imgRef is None) else read_tiff(imgRef)
        imgBlank = None if imgBlank is None else read_tiff(imgBlank)

        # calculate the theoretical position of the hamonics
        period_harm_Vert = np.int(pixelsize[0] / gratingPeriod * img.shape[0] / (sourceDistance + distDet2sample) * sourceDistance)
        period_harm_Hor = np.int(pixelsize[1] / gratingPeriod * img.shape[1] / (sourceDistance + distDet2sample) * sourceDistance)

        return WavePyData(img            = img,
                          imgRef         = imgRef,
                          imgBlank       = imgBlank,
                          mode           = mode,
                          pixelsize      = pixelsize,
                          gratingPeriod  = gratingPeriod,
                          pattern        = pattern,
                          distDet2sample = distDet2sample,
                          phenergy       = phenergy,
                          sourceDistance = sourceDistance,
                          period_harm    = [period_harm_Vert, period_harm_Hor],
                          unwrapFlag     = True)


def calculate_dpc(wavepy_data=WavePyData()):
    img  = wavepy_data.get_parameter("img")
    imgRef  = wavepy_data.get_parameter("imgRef")
    phenergy  = wavepy_data.get_parameter("phenergy")
    pixelsize  = wavepy_data.get_parameter("pixelsize")
    distDet2sample  = wavepy_data.get_parameter("distDet2sample")
    period_harm  = wavepy_data.get_parameter("period_harm")
    unwrapFlag  = wavepy_data.get_parameter("unwrapFlag")

    plotter = get_registered_plotter_instance()
    logger = get_registered_logger_instance()
    ini = get_registered_ini_instance()

    plotter.register_context_window(CALCULATE_DPC_CONTEXT_KEY)

    img_size_o = np.shape(img)

    if plotter.is_active():
        img, idx4crop = plotter.show_interactive_plot(CropDialogPlot, container_widget=None, img=img, pixelsize=pixelsize)
    else:
        idx4crop = ini.get_list_from_ini("Parameters", "Crop")
        img = common_tools.crop_matrix_at_indexes(img, idx4crop)

    # Plot Real Image AFTER crop
    plotter.push_plot_on_context(CALCULATE_DPC_CONTEXT_KEY, ShowCroppedFigure, img=img, pixelsize=pixelsize)

    if not imgRef is None: imgRef = common_tools.crop_matrix_at_indexes(imgRef, idx4crop)

    period_harm_Vert_o = int(period_harm[0]*img.shape[0]/img_size_o[0]) + 1
    period_harm_Hor_o = int(period_harm[1]*img.shape[1]/img_size_o[1]) + 1

    # Obtain harmonic periods from images


    if imgRef is None:
        harmPeriod = [period_harm_Vert_o, period_harm_Hor_o]
    else:
        imgRefFFT = FourierTransform.fft(imgRef)

        logger.print_message('Obtain harmonic 01 exprimentally')

        (_, period_harm_Hor) = grating_interferometry.exp_harm_period(imgRefFFT, [period_harm_Vert_o, period_harm_Hor_o], harmonic_ij=['0', '1'], searchRegion=30)

        logger.print_message('MESSAGE: Obtain harmonic 10 exprimentally')

        (period_harm_Vert, _) = grating_interferometry.exp_harm_period(imgRefFFT, [period_harm_Vert_o, period_harm_Hor_o], harmonic_ij=['1', '0'], searchRegion=30)

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

    plotter.draw_context_on_widget(CALCULATE_DPC_CONTEXT_KEY, container_widget=plotter.get_context_container_widget(CALCULATE_DPC_CONTEXT_KEY))

    return WavePyData(int00=int00,
                      int01=int01,
                      int10=int10,
                      darkField01=darkField01,
                      darkField10=darkField10,
                      diffPhase01=diffPhase01,
                      diffPhase10=diffPhase10,
                      virtual_pixelsize=virtual_pixelsize)
