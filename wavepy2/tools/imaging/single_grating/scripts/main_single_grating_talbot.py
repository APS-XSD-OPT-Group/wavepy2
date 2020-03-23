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
import sys

from wavepy2.util.common.common_tools import FourierTransform
from wavepy2.util.ini.initializer import get_registered_ini_instance, register_ini_instance, IniMode
from wavepy2.util.plot.qt_application import get_registered_qt_application_instance, register_qt_application_instance, QtApplicationMode
from wavepy2.util.log.logger import get_registered_logger_instance, register_logger_single_instance, LoggerMode
from wavepy2.util.plot.plotter import get_registered_plotter_instance, register_plotter_instance, PlotterMode
from wavepy2.util.plot.plot_tools import DefaultMainWindow
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.core.grating_interferometry import *
from wavepy2.core.widgets.grating_interferometry_widgets import *
from wavepy2.tools.imaging.single_grating.single_grating_talbot import main_single_gr_Talbot, hc

register_logger_single_instance(logger_mode=LoggerMode.FULL)
register_ini_instance(IniMode.LOCAL_FILE, ini_file_name=".single_grating_talbot.ini")
register_qt_application_instance(QtApplicationMode.QT)
register_plotter_instance(plotter_mode=PlotterMode.DISPLAY_ONLY)

plotter = get_registered_plotter_instance()

if plotter.is_active():
    main_window = DefaultMainWindow("Single Grating Talbot")
    container_widget = main_window.get_container_widget()
else:
    container_widget = None

# ==========================================================================
# %% Experimental parameters
# ==========================================================================

ini = get_registered_ini_instance()

img    = read_tiff(ini.get_string_from_ini("Files", "sample"))
imgRef = read_tiff(ini.get_string_from_ini("Files", "reference"))

pixel          = ini.get_float_from_ini("Parameters", "pixel size")
pixelsize      = [pixel, pixel]
gratingPeriod  = ini.get_float_from_ini("Parameters", "checkerboard grating period")
pattern        = ini.get_string_from_ini("Parameters", "pattern")
distDet2sample = ini.get_float_from_ini("Parameters", "distance detector to gr")
phenergy       = ini.get_float_from_ini("Parameters", "photon energy")
sourceDistance = ini.get_float_from_ini("Parameters", "source distance")

wavelength = hc/phenergy
kwave = 2*np.pi/wavelength

# calculate the theoretical position of the hamonics
period_harm_Vert = np.int(pixelsize[0]/gratingPeriod*img.shape[0] / (sourceDistance + distDet2sample)*sourceDistance)
period_harm_Hor  = np.int(pixelsize[1]/gratingPeriod*img.shape[1] / (sourceDistance + distDet2sample)*sourceDistance)

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

plotter.draw_context_on_widget("Single Grating Talbot", container_widget=container_widget)

if plotter.is_active(): main_window.show()

get_registered_qt_application_instance().run_qt_application()

