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
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import get_registered_logger_instance, LoggerColor
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyInteractiveWidget
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.tools.common.wavepy_data import WavePyData

class InputParametersWidget(WavePyInteractiveWidget):

    def __init__(self, parent):
        super(InputParametersWidget, self).__init__(parent, message="Input Parameters", title="Input Parameters")
        self.__ini     = get_registered_ini_instance()
        self.__logger  = get_registered_logger_instance()

        self.img            = self.__ini.get_string_from_ini("Files", "sample")
        self.imgRef         = self.__ini.get_string_from_ini("Files", "reference")
        self.imgBlank       = self.__ini.get_string_from_ini("Files", "blank")
        self.mode           = self.__ini.get_string_from_ini("Parameters", "Mode")
        pixel                 = self.__ini.get_float_from_ini("Parameters", "pixel size")
        self.pixelsize      = [pixel, pixel]
        self.gratingPeriod  = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period")
        self.pattern        = self.__ini.get_string_from_ini("Parameters", "pattern")
        self.distDet2sample = self.__ini.get_float_from_ini("Parameters", "distance detector to gr")
        self.phenergy       = self.__ini.get_float_from_ini("Parameters", "photon energy")
        self.sourceDistance = self.__ini.get_float_from_ini("Parameters", "source distance")

    def build_widget(self, **kwargs):
        main_box = plot_tools.widgetBox(self.get_central_widget(), "", width=800, height=400)

        select_file_img_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_img = plot_tools.lineEdit(select_file_img_box, self, "img", label="Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_file_img_box, self, "...", callback=self.selectImgFile)

        self.setFixedWidth(800)
        self.setFixedHeight(400)

        self.update()


    def selectImgFile(self):
        self.le_img.setText(plot_tools.selectFileFromDialog(self, self.img, "Open Image File"))

    def get_accepted_output(self):
        img      = read_tiff(self.img)
        imgRef   = None if (self.mode == 'Relative' or self.imgRef is None) else read_tiff(self.imgRef)
        imgBlank = None if self.imgBlank is None else read_tiff(self.imgBlank)

        # calculate the theoretical position of the hamonics
        period_harm_Vert = np.int(self.pixelsize[0] / self.gratingPeriod * img.shape[0] / (self.sourceDistance + self.distDet2sample) * self.sourceDistance)
        period_harm_Hor  = np.int(self.pixelsize[1] / self.gratingPeriod * img.shape[1] / (self.sourceDistance + self.distDet2sample) * self.sourceDistance)

        return WavePyData(img            = img,
                          imgRef         = imgRef,
                          imgBlank       = imgBlank,
                          mode           = self.mode,
                          pixelsize      = self.pixelsize,
                          gratingPeriod  = self.gratingPeriod,
                          pattern        = self.pattern,
                          distDet2sample = self.distDet2sample,
                          phenergy       = self.phenergy,
                          sourceDistance = self.sourceDistance,
                          period_harm    = [period_harm_Vert, period_harm_Hor],
                          unwrapFlag     = True)

    def get_rejected_output(self):
        raise ValueError("Initialization Canceled, Program exit")
