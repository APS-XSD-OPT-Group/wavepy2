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

from wavepy2.util.common.common_tools import FourierTransform
from wavepy2.util.log.logger import get_registered_logger_instance, LoggerMode
from wavepy2.util.plot.plotter import get_registered_plotter_instance, PlotterMode
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.core.grating_interferometry import *
from wavepy2.core.widgets.grating_interferometry import *


def main_single_gr_Talbot(img, imgRef,
                          phenergy, pixelsize, distDet2sample,
                          period_harm,
                          unwrapFlag=True,
                          context_key="main_single_gr_Talbot"):

    logger = get_registered_logger_instance()

    img_size_o = np.shape(img)

    #img, idx4crop = crop_dialog(img, saveFigFlag=saveFigFlag)
    #if imgRef is not None:
    #    imgRef = wpu.crop_matrix_at_indexes(imgRef, idx4crop)

    period_harm_Vert_o = int(period_harm[0]*img.shape[0]/img_size_o[0]) + 1
    period_harm_Hor_o = int(period_harm[1]*img.shape[1]/img_size_o[1]) + 1

    # Obtain harmonic periods from images

    logger.print_message('Obtain harmonic 01 exprimentally')

    if imgRef is None:
        harmPeriod = [period_harm_Vert_o, period_harm_Hor_o]
    else:
        imgRefFFT = FourierTransform.fft(imgRef)

        (_, period_harm_Hor) = exp_harm_period(imgRefFFT, [period_harm_Vert_o, period_harm_Hor_o], harmonic_ij=['0', '1'], searchRegion=30)

        logger.print_message('MESSAGE: Obtain harmonic 10 exprimentally')

        (period_harm_Vert, _) = exp_harm_period(imgRefFFT, [period_harm_Vert_o, period_harm_Hor_o], harmonic_ij=['1', '0'], searchRegion=30)

        harmPeriod = [period_harm_Vert, period_harm_Hor]

    # Calculate everything

    [int00, int01, int10,
     darkField01, darkField10,
     phaseFFT_01,
     phaseFFT_10] = single_2Dgrating_analyses(img,
                                              img_ref=imgRef,
                                              harmonicPeriod=harmPeriod,
                                              unwrapFlag=unwrapFlag,
                                              context_key=context_key)

    virtual_pixelsize = [0, 0]
    virtual_pixelsize[0] = pixelsize[0]*img.shape[0]/int00.shape[0]
    virtual_pixelsize[1] = pixelsize[1]*img.shape[1]/int00.shape[1]

    diffPhase01 = -phaseFFT_01*virtual_pixelsize[1]/distDet2sample/hc*phenergy
    diffPhase10 = -phaseFFT_10*virtual_pixelsize[0]/distDet2sample/hc*phenergy
    # Note: the signals above were defined base in experimental data

    return [int00, int01, int10,
            darkField01, darkField10,
            diffPhase01, diffPhase10,
            virtual_pixelsize]


import sys

from wavepy2.util.plot.plotter import register_plotter_instance
from wavepy2.util.log.logger import register_logger_single_instance
from PyQt5.Qt import QApplication
from PyQt5.QtWidgets import QWidget, QMainWindow
from scipy import constants



if __name__=="__main__":
    a = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Single Grating Talbot")
    container_widget = QWidget()
    main_window.setCentralWidget(container_widget)

    hc = constants.value('inverse meter-electron volt relationship')  # hc

    register_logger_single_instance(logger_mode=LoggerMode.WARNING)
    register_plotter_instance(plotter_mode=PlotterMode.FULL)

    # ==========================================================================
    # %% Experimental parameters
    # ==========================================================================

    img    = read_tiff("/Users/lrebuffi/Desktop/grating_200mm/sample_5s_005.tif")
    imgRef = read_tiff("/Users/lrebuffi/Desktop/grating_200mm/ref_5s_006.tif")

    pixelsize = [6.5e-07, 6.5e-07]
    gratingPeriod = 4.8e-06
    pattern = "Diagonal half pi"
    distDet2sample = 0.33
    phenergy = 14000.0
    sourceDistance = 32.0

    wavelength = hc/phenergy
    kwave = 2*np.pi/wavelength

    # calculate the theoretical position of the hamonics
    period_harm_Vert = np.int(pixelsize[0]/gratingPeriod*img.shape[0] /
                              (sourceDistance + distDet2sample)*sourceDistance)
    period_harm_Hor = np.int(pixelsize[1]/gratingPeriod*img.shape[1] /
                             (sourceDistance + distDet2sample)*sourceDistance)

    saveFigFlag = True

    # ==========================================================================
    # %% do the magic
    # ==========================================================================

    # for relative mode we need to have imgRef=None,
    result = main_single_gr_Talbot(img, imgRef,
                                   phenergy, pixelsize, distDet2sample,
                                   period_harm=[period_harm_Vert,
                                                period_harm_Hor],
                                   unwrapFlag=True,
                                   context_key="Single Grating Talbot")

    [int00, int01, int10,
     darkField01, darkField10,
     diffPhase01, diffPhase10,
     virtual_pixelsize] = result

    plotter = get_registered_plotter_instance()

    plotter.draw_context_on_widget("Single Grating Talbot", container_widget=container_widget)

    main_window.show()

    a.exec_()

