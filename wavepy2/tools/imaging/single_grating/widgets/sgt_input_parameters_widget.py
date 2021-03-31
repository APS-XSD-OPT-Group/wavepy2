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
from wavepy2.util.common.common_tools import PATH_SEPARATOR

from wavepy2.util.common import common_tools
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyInteractiveWidget, WavePyWidget
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.tools.common.wavepy_data import WavePyData

from PyQt5.QtWidgets import QWidget

MODES    = ["Relative", "Absolute"]
PATTERNS = ["Diagonal half pi", "Edge pi"]

def generate_initialization_parameters_sgt(img_file_name,
                                           imgRef_file_name,
                                           imgBlank_file_name,
                                           mode,
                                           pixel,
                                           gratingPeriod,
                                           pattern,
                                           distDet2sample,
                                           phenergy,
                                           sourceDistance,
                                           correct_pi_jump,
                                           remove_mean,
                                           correct_dpc_center,
                                           remove_linear,
                                           do_integration,
                                           calc_thickness,
                                           remove_2nd_order,
                                           material_idx,
                                           widget=None):
    img = read_tiff(img_file_name)
    imgRef = None if (mode == MODES[1] or common_tools.is_empty_file_name(imgRef_file_name)) else read_tiff(imgRef_file_name)
    imgBlank = None if common_tools.is_empty_file_name(imgBlank_file_name) else read_tiff(imgBlank_file_name)

    pixelsize = [pixel, pixel]

    if imgBlank is None:
        defaultBlankV = np.int(np.mean(img[0:100, 0:100]))
        defaultBlankV = plot_tools.ValueDialog.get_value(widget,
                                                         message="No Dark File. Value of Dark [counts]\n(Default is the mean value of the 100x100 pixels top-left corner)",
                                                         title='Experimental Values',
                                                         default=defaultBlankV)
        imgBlank = img * 0.0 + defaultBlankV

    img = img - imgBlank

    if PATH_SEPARATOR in img_file_name:
        saveFileSuf = img_file_name.rsplit(PATH_SEPARATOR, 1)[0] + PATH_SEPARATOR + img_file_name.rsplit(PATH_SEPARATOR, 1)[1].split('.')[0] + '_output' + PATH_SEPARATOR
    else:
        saveFileSuf = img_file_name.rsplit(PATH_SEPARATOR, 1)[1].split('.')[0] + '_output' + PATH_SEPARATOR

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

    # calculate the theoretical position of the hamonics
    period_harm_Vert = np.int(pixelsize[0] / gratingPeriod * img.shape[0] / (sourceDistance + distDet2sample) * sourceDistance)
    period_harm_Hor = np.int(pixelsize[1] / gratingPeriod * img.shape[1] / (sourceDistance + distDet2sample) * sourceDistance)

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
                      saveFileSuf=saveFileSuf,
                      correct_pi_jump =correct_pi_jump,
                      remove_mean=remove_mean,
                      correct_dpc_center=correct_dpc_center,
                      remove_linear=remove_linear,
                      do_integration=do_integration,
                      calc_thickness=calc_thickness,
                      remove_2nd_order=remove_2nd_order,
                      material_idx=material_idx)



class AbstractSGTInputParametersWidget():
    WIDTH  = 800
    HEIGHT = 430

    def __init__(self, application_name=None):
        self.__ini     = get_registered_ini_instance(application_name=application_name)
        self.__logger  = get_registered_logger_instance(application_name=application_name)

        self.img                = self.__ini.get_string_from_ini("Files", "sample")
        self.imgRef             = self.__ini.get_string_from_ini("Files", "reference")
        self.imgBlank           = self.__ini.get_string_from_ini("Files", "blank")
        self.mode               = MODES.index(self.__ini.get_string_from_ini("Parameters", "Mode", default=MODES[0]))
        self.pixel              = self.__ini.get_float_from_ini("Parameters", "pixel size", default=6.5e-07)
        self.gratingPeriod      = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period", default=4.8e-06)
        self.pattern            = PATTERNS.index(self.__ini.get_string_from_ini("Parameters", "pattern", default=PATTERNS[0]))
        self.distDet2sample     = self.__ini.get_float_from_ini("Parameters", "distance detector to gr", default=0.33)
        self.phenergy           = self.__ini.get_float_from_ini("Parameters", "photon energy", default=14000.0)
        self.sourceDistance     = self.__ini.get_float_from_ini("Parameters", "source distance", default=32.0)

        self.correct_pi_jump    = self.__ini.get_boolean_from_ini("Runtime", "correct pi jump", default=False)
        self.remove_mean        = self.__ini.get_boolean_from_ini("Runtime", "remove mean", default=False)
        self.correct_dpc_center = self.__ini.get_boolean_from_ini("Runtime", "correct dpc center", default=False)
        self.remove_linear      = self.__ini.get_boolean_from_ini("Runtime", "remove linear", default=False)
        self.do_integration     = self.__ini.get_boolean_from_ini("Runtime", "do integration", default=False)
        self.calc_thickness     = self.__ini.get_boolean_from_ini("Runtime", "calc thickness", default=False)
        self.remove_2nd_order   = self.__ini.get_boolean_from_ini("Runtime", "remove 2nd order", default=False)
        self.material_idx       = self.__ini.get_int_from_ini("Runtime", "material idx", default=0)

    def build_widget(self, **kwargs):
        try: show_runtime_options = kwargs["show_runtime_options"]
        except: show_runtime_options = True

        try:    widget_width = kwargs["widget_width"]
        except: widget_width = self.WIDTH
        try:    widget_height = kwargs["widget_height"]
        except: widget_height = self.HEIGHT

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)

        if show_runtime_options: tabs = plot_tools.tabWidget(self.get_central_widget())

        ini_widget = QWidget()
        ini_widget.setFixedHeight(widget_height-10)
        ini_widget.setFixedWidth(widget_width-10)

        if show_runtime_options: plot_tools.createTabPage(tabs, "Initialization Parameter", widgetToAdd=ini_widget)
        else: self.get_central_widget().layout().addWidget(ini_widget)

        main_box = plot_tools.widgetBox(ini_widget, "", width=widget_width-70, height=widget_height-50)

        plot_tools.comboBox(main_box, self, "mode", label="Mode", items=MODES, callback=self.set_mode, orientation="horizontal")

        select_file_img_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_img = plot_tools.lineEdit(select_file_img_box, self, "img", label="Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_file_img_box, self, "...", callback=self.selectImgFile)

        self.select_file_imgRef_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_imgRef = plot_tools.lineEdit(self.select_file_imgRef_box, self, "imgRef", label="Reference Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(self.select_file_imgRef_box, self, "...", callback=self.selectImgRefFile)

        self.select_file_imgBlank_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_imgBlank = plot_tools.lineEdit(self.select_file_imgBlank_box, self, "imgBlank", label="Blank Image File", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(self.select_file_imgBlank_box, self, "...", callback=self.selectImgBlankFile)

        self.set_mode()

        plot_tools.lineEdit(main_box, self, "pixel", label="Pixel Size", labelWidth=250, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "gratingPeriod", label="Grating Period", labelWidth=250, valueType=float, orientation="horizontal")

        plot_tools.comboBox(main_box, self, "pattern", label="Pattern", items=PATTERNS, orientation="horizontal")

        plot_tools.lineEdit(main_box, self, "distDet2sample", label="Distance Detector to Grating", labelWidth=250, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "phenergy", label="Photon Energy", labelWidth=250, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "sourceDistance", label="Source Distance", labelWidth=250, valueType=float, orientation="horizontal")

        #--------------------------------------------------

        if show_runtime_options:
            runtime_widget = QWidget()
            runtime_widget.setFixedHeight(widget_height-10)
            runtime_widget.setFixedWidth(widget_width-10)

            plot_tools.createTabPage(tabs, "Runtime Parameter", widgetToAdd=runtime_widget)

            main_box = plot_tools.widgetBox(runtime_widget, "", width=widget_width-70, height=widget_height-50)

            plot_tools.checkBox(main_box, self, "correct_pi_jump", "Correct pi jump in DPC signal")
            plot_tools.checkBox(main_box, self, "remove_mean", "Remove mean DPC")
            plot_tools.checkBox(main_box, self, "correct_dpc_center", "Correct DPC center")
            plot_tools.checkBox(main_box, self, "remove_linear", "Remove 2D linear fit from DPC")
            plot_tools.checkBox(main_box, self, "do_integration", "Calculate Frankot-Chellappa integration")
            plot_tools.checkBox(main_box, self, "calc_thickness", "Convert phase to thickness")
            plot_tools.checkBox(main_box, self, "remove_2nd_order", "Remove 2nd order polynomial from integrated Phase")
            plot_tools.comboBox(main_box, self, "material_idx", items=["Diamond", "Beryllium"], label="Material", labelWidth=200, orientation="horizontal")

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
        self.__ini.set_value_at_ini('Files', 'sample', self.img)
        self.__ini.set_value_at_ini('Files', 'reference', self.imgRef)
        self.__ini.set_value_at_ini('Files', 'blank', self.imgBlank)
        self.__ini.set_value_at_ini('Parameters', 'Mode', MODES[self.mode])
        self.__ini.set_value_at_ini('Parameters', 'Pixel Size', self.pixel)
        self.__ini.set_value_at_ini('Parameters', 'Checkerboard Grating Period', self.gratingPeriod)
        self.__ini.set_value_at_ini('Parameters', 'Pattern', PATTERNS[self.pattern])
        self.__ini.set_value_at_ini('Parameters', 'Distance Detector to Gr', self.distDet2sample)
        self.__ini.set_value_at_ini('Parameters', 'Photon Energy', self.phenergy)
        self.__ini.set_value_at_ini('Parameters', 'Source Distance', self.sourceDistance)
        self.__ini.set_value_at_ini("Runtime", "correct pi jump", self.correct_pi_jump)
        self.__ini.set_value_at_ini("Runtime", "remove mean", self.remove_mean)
        self.__ini.set_value_at_ini("Runtime", "correct dpc center", self.correct_dpc_center)
        self.__ini.set_value_at_ini("Runtime", "remove linear", self.remove_linear)
        self.__ini.set_value_at_ini("Runtime", "do integration", self.do_integration)
        self.__ini.set_value_at_ini("Runtime", "calc thickness", self.calc_thickness)
        self.__ini.set_value_at_ini("Runtime", "remove 2nd order", self.remove_2nd_order)
        self.__ini.set_value_at_ini("Runtime", "material idx", self.material_idx)

        self.__ini.push()

        return generate_initialization_parameters_sgt(self.img,
                                                      self.imgRef,
                                                      self.imgBlank,
                                                      MODES[self.mode],
                                                      self.pixel,
                                                      self.gratingPeriod,
                                                      PATTERNS[self.pattern],
                                                      self.distDet2sample,
                                                      self.phenergy,
                                                      self.sourceDistance,
                                                      self.correct_pi_jump,
                                                      self.remove_mean,
                                                      self.correct_dpc_center,
                                                      self.remove_linear,
                                                      self.do_integration,
                                                      self.calc_thickness,
                                                      self.remove_2nd_order,
                                                      self.material_idx,
                                                      widget=self)

    def get_rejected_output(self):
        self.__logger.print_error("Initialization Canceled, Program exit")
        sys.exit(1)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class SGTInputParametersWidget(AbstractSGTInputParametersWidget, WavePyWidget):
    def __init__(self, application_name=None, **kwargs):
        AbstractSGTInputParametersWidget.__init__(self, application_name)
        WavePyWidget.__init__(self, parent=None, application_name=application_name)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.__central_widget = QWidget()
        self.__central_widget.setLayout(QVBoxLayout())

        layout.addWidget(self.__central_widget)

    def get_central_widget(self):
        return self.__central_widget

    def get_plot_tab_name(self):
        return "Single Grating Talbot Initialization Parameters"

    def _allows_saving(self):
        return False

class SGTInputParametersDialog(AbstractSGTInputParametersWidget, WavePyInteractiveWidget):
    def __init__(self, parent, application_name=None, **kwargs):
        AbstractSGTInputParametersWidget.__init__(self, application_name)
        WavePyInteractiveWidget.__init__(self, parent, message="Input Parameters", title="Input Parameters")
