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
import sys, os

from wavepy2.util.common import common_tools
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyInteractiveWidget, get_registered_plotter_instance
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.tools.common.wavepy_data import WavePyData

MODES    = ["Relative", "Absolute"]
PATTERNS = ["Diagonal half pi", "Edge pi"]

def generate_initialization_parameters(img_file_name,
                                       imgRef_file_name,
                                       imgBlank_file_name,
                                       mode,
                                       pixel,
                                       gratingPeriod,
                                       pattern,
                                       distDet2sample,
                                       phenergy,
                                       sourceDistance,
                                       widget=None):
    img = read_tiff(img_file_name)
    imgRef = None if (mode == MODES[1] or common_tools.is_empty_file_name(imgRef_file_name)) else read_tiff(imgRef_file_name)
    imgBlank = None if common_tools.is_empty_file_name(imgBlank_file_name) else read_tiff(imgBlank_file_name)

    pixelsize = [pixel, pixel]

    # calculate the theoretical position of the hamonics
    period_harm_Vert = np.int(pixelsize[0] / gratingPeriod * img.shape[0] / (sourceDistance + distDet2sample) * sourceDistance)
    period_harm_Hor = np.int(pixelsize[1] / gratingPeriod * img.shape[1] / (sourceDistance + distDet2sample) * sourceDistance)

    if imgBlank is None:
        defaultBlankV = np.int(np.mean(img[0:100, 0:100]))
        defaultBlankV = plot_tools.ValueDialog.get_value(widget,
                                                         message="No Dark File. Value of Dark [counts]\n(Default is the mean value of the 100x100 pixels top-left corner)",
                                                         title='Experimental Values',
                                                         default=defaultBlankV)
        imgBlank = img * 0.0 + defaultBlankV

    img = img - imgBlank

    if '/' in img_file_name:
        saveFileSuf = img_file_name.rsplit('/', 1)[0] + '/' + img_file_name.rsplit('/', 1)[1].split('.')[0] + '_output/'
    else:
        saveFileSuf = img_file_name.rsplit('/', 1)[1].split('.')[0] + '_output/'

    if os.path.isdir(saveFileSuf): saveFileSuf = common_tools.get_unique_filename(saveFileSuf, isFolder=True)

    os.makedirs(saveFileSuf, exist_ok=True)

    if imgRef is None:
        saveFileSuf += 'WF_'
    else:
        imgRef = imgRef - imgBlank
        saveFileSuf += 'TalbotImaging_'

    if pattern == PATTERNS[0]:  # 'Diagonal half pi':
        gratingPeriod *= 1.0 / np.sqrt(2.0)
        phaseShift = 'halfPi'
    elif pattern == PATTERNS[1]:  # 'Edge pi':
        gratingPeriod *= 1.0 / 2.0
        phaseShift = 'Pi'

    saveFileSuf += 'cb{:.2f}um_'.format(gratingPeriod * 1e6)
    saveFileSuf += phaseShift
    saveFileSuf += '_d{:.0f}mm_'.format(distDet2sample * 1e3)
    saveFileSuf += '{:.1f}KeV'.format(phenergy * 1e-3)
    saveFileSuf = saveFileSuf.replace('.', 'p')

    get_registered_plotter_instance().register_save_file_prefix(saveFileSuf)

    return WavePyData(img=img,
                      imgRef=imgRef,
                      imgBlank=imgBlank,
                      mode=mode,
                      pixelsize=pixelsize,
                      gratingPeriod=gratingPeriod,
                      pattern=pattern,
                      distDet2sample=distDet2sample,
                      phenergy=phenergy,
                      sourceDistance=sourceDistance,
                      period_harm=[period_harm_Vert, period_harm_Hor],
                      saveFileSuf=saveFileSuf)

class InputParametersWidget(WavePyInteractiveWidget):
    def __init__(self, parent):
        super(InputParametersWidget, self).__init__(parent, message="Input Parameters", title="Input Parameters")
        self.__ini     = get_registered_ini_instance()
        self.__logger  = get_registered_logger_instance()

        self.img            = self.__ini.get_string_from_ini("Files", "sample")
        self.imgRef         = self.__ini.get_string_from_ini("Files", "reference")
        self.imgBlank       = self.__ini.get_string_from_ini("Files", "blank")
        self.mode           = MODES.index(self.__ini.get_string_from_ini("Parameters", "Mode"))
        self.pixel          = self.__ini.get_float_from_ini("Parameters", "pixel size")
        self.gratingPeriod  = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period")
        self.pattern        = PATTERNS.index(self.__ini.get_string_from_ini("Parameters", "pattern"))
        self.distDet2sample = self.__ini.get_float_from_ini("Parameters", "distance detector to gr")
        self.phenergy       = self.__ini.get_float_from_ini("Parameters", "photon energy")
        self.sourceDistance = self.__ini.get_float_from_ini("Parameters", "source distance")

    def build_widget(self, **kwargs):
        main_box = plot_tools.widgetBox(self.get_central_widget(), "")

        plot_tools.comboBox(main_box, self, "mode", label="Mode", items=MODES, callback=self.set_mode, orientation="horizontal")

        select_file_img_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_img = plot_tools.lineEdit(select_file_img_box, self, "img", label="Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_file_img_box, self, "...", callback=self.selectImgFile)

        self.select_file_imgRef_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_imgRef = plot_tools.lineEdit(self.select_file_imgRef_box, self, "imgRef", label="Reference Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(self.select_file_imgRef_box, self, "...", callback=self.selectImgRefFile)

        self.select_file_imgBlank_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_imgBlank = plot_tools.lineEdit(self.select_file_imgBlank_box, self, "img", label="Blank Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(self.select_file_imgBlank_box, self, "...", callback=self.selectImgBlankFile)

        self.set_mode()

        plot_tools.lineEdit(main_box, self, "pixel", label="Pixel Size", labelWidth=150, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "gratingPeriod", label="Grating Period", labelWidth=150, valueType=float, orientation="horizontal")

        plot_tools.comboBox(main_box, self, "pattern", label="Pattern", items=PATTERNS, orientation="horizontal")

        plot_tools.lineEdit(main_box, self, "distDet2sample", label="Distance Detector to Grating", labelWidth=150, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "phenergy", label="Photon Energy", labelWidth=150, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "sourceDistance", label="Source Distance", labelWidth=150, valueType=float, orientation="horizontal")

        self.setFixedWidth(800)
        self.setFixedHeight(400)

        self.update()

    def set_mode(self):
        self.select_file_imgRef_box.setEnabled(self.mode == 0)

    def selectImgFile(self):
        self.le_img.setText(plot_tools.selectFileFromDialog(self, self.img, "Open Image File"))

    def selectImgRefFile(self):
        self.le_imgRef.setText(plot_tools.selectFileFromDialog(self, self.imgRef, "Open Reference Image File"))

    def selectImgBlankFile(self):
        self.le_imgBlank.setText(plot_tools.selectFileFromDialog(self, self.imgBlank, "Open Blank Image File"))

    def get_accepted_output(self):
        self.__ini.set_at_ini('Files',      'sample',                      self.img)
        self.__ini.set_at_ini('Files',      'reference',                   self.imgRef)
        self.__ini.set_at_ini('Files',      'blank',                       self.imgBlank)
        self.__ini.set_at_ini('Parameters', 'Mode',                        MODES[self.mode])
        self.__ini.set_at_ini('Parameters', 'Pixel Size',                  self.pixel)
        self.__ini.set_at_ini('Parameters', 'Checkerboard Grating Period', self.gratingPeriod)
        self.__ini.set_at_ini('Parameters', 'Pattern',                     PATTERNS[self.pattern])
        self.__ini.set_at_ini('Parameters', 'Distance Detector to Gr',     self.distDet2sample)
        self.__ini.set_at_ini('Parameters', 'Photon Energy',               self.phenergy)
        self.__ini.set_at_ini('Parameters', 'Source Distance',             self.sourceDistance)
        self.__ini.push()

        return generate_initialization_parameters(self.img,
                                                  self.imgRef,
                                                  self.imgBlank,
                                                  MODES[self.mode],
                                                  self.pixel,
                                                  self.gratingPeriod,
                                                  PATTERNS[self.pattern],
                                                  self.distDet2sample,
                                                  self.pattern,
                                                  self.sourceDistance,
                                                  widget=self)

    def get_rejected_output(self):
        self.__logger.print_error("Initialization Canceled, Program exit")
        sys.exit(1)
