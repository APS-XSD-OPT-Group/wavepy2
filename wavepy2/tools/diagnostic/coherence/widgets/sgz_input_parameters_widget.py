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
import glob

from wavepy2.util.common.common_tools import PATH_SEPARATOR
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyInteractiveWidget, WavePyWidget
from wavepy2.util.io.read_write_file import read_tiff

from wavepy2.tools.common.wavepy_data import WavePyData

from PyQt5.QtWidgets import QWidget

ZVEC_FROM = ["Calculated", "Tabled"]
PATTERNS  = ["Diagonal", "Edge"]

def generate_initialization_parameters_sgz(dataFolder,
                                           samplefileName,
                                           zvec_from,
                                           startDist,
                                           step_z_scan,
                                           image_per_point,
                                           strideFile,
                                           zvec_file,
                                           pixelsize,
                                           gratingPeriod,
                                           pattern,
                                           sourceDistanceV,
                                           sourceDistanceH,
                                           unFilterSize,
                                           searchRegion,
                                           logger=None):

    out_dir = dataFolder + PATH_SEPARATOR + "output" + PATH_SEPARATOR
    if not os.path.exists(out_dir): os.mkdir(out_dir)

    file_prefix = samplefileName.rsplit("_", 1)[0].rsplit(PATH_SEPARATOR, 1)[1]

    fname2save = dataFolder + PATH_SEPARATOR + "output" + PATH_SEPARATOR + file_prefix

    logger.print_message("Loading files " + dataFolder + PATH_SEPARATOR + file_prefix + "*.tif")

    listOfDataFiles = glob.glob(dataFolder + PATH_SEPARATOR + file_prefix + "*.tif")
    listOfDataFiles.sort()

    nfiles = len(listOfDataFiles)

    img = read_tiff(samplefileName)

    if zvec_from == ZVEC_FROM[0]: # Calculated
        zvec = np.linspace(startDist,
                           startDist + step_z_scan*(nfiles/image_per_point-1),
                           int(nfiles/image_per_point))
        zvec = zvec.repeat(image_per_point)

        listOfDataFiles = listOfDataFiles[0::strideFile]
        zvec            = zvec[0::strideFile]
    elif zvec_from == ZVEC_FROM[1]:# Tabled
        zvec        = np.loadtxt(zvec_file)*1e-3
        step_z_scan = np.mean(np.diff(zvec))

    if step_z_scan > 0:
        pass
    else:
        listOfDataFiles = listOfDataFiles[::-1]
        zvec = zvec[::-1]

    return WavePyData(img=img,
                      dataFolder=dataFolder,
                      startDist=startDist,
                      step_z_scan=step_z_scan,
                      image_per_point=image_per_point,
                      strideFile=strideFile,
                      listOfDataFiles=listOfDataFiles,
                      nfiles=nfiles,
                      zvec_from=zvec_from,
                      zvec=zvec,
                      pixelsize=pixelsize,
                      gratingPeriod=gratingPeriod,
                      pattern=pattern,
                      sourceDistanceV=sourceDistanceV,
                      sourceDistanceH=sourceDistanceH,
                      unFilterSize=unFilterSize,
                      searchRegion=searchRegion,
                      saveFileSuf=fname2save)

class AbstractSGZInputParametersWidget():
    WIDTH  = 800
    HEIGHT = 520

    def __init__(self, application_name=None):
        self.__ini     = get_registered_ini_instance(application_name=application_name)
        self.__logger  = get_registered_logger_instance(application_name=application_name)

        self.dataDirectory      = self.__ini.get_string_from_ini("Files", "data directory")
        self.samplefileName     = self.__ini.get_string_from_ini("Files", "sample file name")
        self.zvec_from          = ZVEC_FROM.index(self.__ini.get_string_from_ini("Parameters", "z distances from", default="Calculated"))
        self.startDist          = self.__ini.get_float_from_ini("Parameters", "starting distance scan", default=20*1e-3)
        self.step_z_scan        = self.__ini.get_float_from_ini("Parameters", "step size scan", default=5*1e-3)
        self.image_per_point    = self.__ini.get_int_from_ini("Parameters", "number of images per step", default=1)
        self.strideFile         = self.__ini.get_int_from_ini("Parameters", "stride", default=1)
        self.zvec_file          = self.__ini.get_string_from_ini("Parameters", "z distances file")
        self.pixelsize          = self.__ini.get_float_from_ini("Parameters", "pixel size", default=6.5e-07)
        self.gratingPeriod      = self.__ini.get_float_from_ini("Parameters", "checkerboard grating period", default=4.8e-06)
        self.pattern            = PATTERNS.index(self.__ini.get_string_from_ini("Parameters", "pattern", default="Diagonal"))
        self.sourceDistanceV    = self.__ini.get_float_from_ini("Parameters", "source distance v", default=-0.73)
        self.sourceDistanceH    = self.__ini.get_float_from_ini("Parameters", "source distance h", default=34.0)
        self.unFilterSize       = self.__ini.get_int_from_ini("Parameters", "size for uniform filter", default=1)
        self.searchRegion       = self.__ini.get_int_from_ini("Parameters", "size for region for searching", default=1)

    def build_widget(self, **kwargs):
        try:    widget_width = kwargs["widget_width"]
        except: widget_width = self.WIDTH
        try:    widget_height = kwargs["widget_height"]
        except: widget_height = self.HEIGHT

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)

        tabs = plot_tools.tabWidget(self.get_central_widget())

        ini_widget = QWidget()
        ini_widget.setFixedHeight(widget_height-10)
        ini_widget.setFixedWidth(widget_width-10)
        runtime_widget = QWidget()
        runtime_widget.setFixedHeight(widget_height-10)
        runtime_widget.setFixedWidth(widget_width-10)

        plot_tools.createTabPage(tabs, "Initialization Parameter", widgetToAdd=ini_widget)

        main_box = plot_tools.widgetBox(ini_widget, "", width=widget_width-70, height=widget_height-50)

        select_dataDirectory_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_dataDirectory = plot_tools.lineEdit(select_dataDirectory_box, self, "dataDirectory", label="Data Directory", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_dataDirectory_box, self, "...", callback=self.selectDataDirectory)

        select_file_img_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_img = plot_tools.lineEdit(select_file_img_box, self, "samplefileName", label="Image File for Cropping", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_file_img_box, self, "...", callback=self.selectImgFile)

        plot_tools.comboBox(main_box, self, "zvec_from", label="Z distances", items=ZVEC_FROM, callback=self.set_zvec_from, orientation="horizontal")

        self.zvec_box_1 = plot_tools.widgetBox(main_box, orientation="vertical", height=110)
        
        plot_tools.lineEdit(self.zvec_box_1, self, "startDist",       label="Starting distance scan [m]", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(self.zvec_box_1, self, "step_z_scan",     label="Step size scan [m]", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(self.zvec_box_1, self, "image_per_point", label="Number of images per step", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(self.zvec_box_1, self, "strideFile",      label="Stride (Use only every XX files)", labelWidth=400, valueType=float, orientation="horizontal")

        self.zvec_box_2 = plot_tools.widgetBox(main_box, orientation="vertical", height=110)

        select_zvec_file_box = plot_tools.widgetBox(self.zvec_box_2, orientation="horizontal")
        self.le_zvec_file = plot_tools.lineEdit(select_zvec_file_box, self, "zvec_file", label="Table with the z distance values in mm", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_zvec_file_box, self, "...", callback=self.selectZVecFile)

        self.set_zvec_from()

        plot_tools.lineEdit(main_box, self, "pixelsize", label="Pixel Size", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "gratingPeriod", label="CB Grating Period", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.comboBox(main_box, self, "pattern", label="CB Grating Pattern", items=PATTERNS, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "sourceDistanceV", label="Source Distance Vertical Direction [m]", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "sourceDistanceH", label="Source Distance Horizontal Direction [m]", labelWidth=400, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "unFilterSize", label="Size for Uniform Filter [Pixels] (Enter 1 to NOT use the filter)", labelWidth=400, valueType=int, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "searchRegion", label="Size of Region for Searching the Peak [Pixels]", labelWidth=400, valueType=int, orientation="horizontal")

        self.update()

    def set_zvec_from(self):
        self.zvec_box_1.setVisible(self.zvec_from == 0)
        self.zvec_box_2.setVisible(self.zvec_from == 1)

    def selectDataDirectory(self):
        self.le_dataDirectory.setText(plot_tools.selectDirectoryFromDialog(self, self.dataDirectory, "Select Data Directory"))

    def selectImgFile(self):
        self.le_img.setText(plot_tools.selectFileFromDialog(self, self.samplefileName, "Open Image File for Cropping"))

    def selectZVecFile(self):
        self.le_zvec_file.setText(plot_tools.selectFileFromDialog(self, self.zvec_file, "Table with the z distance values"))

    def get_accepted_output(self):
        self.__ini.set_value_at_ini("Files", "data directory", self.dataDirectory)
        self.__ini.set_value_at_ini("Files", "sample file name", self.samplefileName)
        
        self.__ini.set_value_at_ini("Parameters", "z distances from", ZVEC_FROM[self.zvec_from])
        self.__ini.set_value_at_ini("Parameters", "starting distance scan", self.startDist)
        self.__ini.set_value_at_ini("Parameters", "step size scan", self.step_z_scan)
        self.__ini.set_value_at_ini("Parameters", "number of images per step", self.image_per_point)
        self.__ini.set_value_at_ini("Parameters", "stride", self.strideFile)
        self.__ini.set_value_at_ini("Parameters", "z distances file", self.zvec_file)
        self.__ini.set_value_at_ini("Parameters", "pixel size", self.pixelsize)
        self.__ini.set_value_at_ini("Parameters", "checkerboard grating period", self.gratingPeriod)
        self.__ini.set_value_at_ini("Parameters", "Pattern", PATTERNS[self.pattern])
        self.__ini.set_value_at_ini("Parameters", "source distance v", self.sourceDistanceV)
        self.__ini.set_value_at_ini("Parameters", "source distance h", self.sourceDistanceH)
        self.__ini.set_value_at_ini("Parameters", "size for uniform filter", self.unFilterSize)
        self.__ini.set_value_at_ini("Parameters", "size for region for searching", self.searchRegion)

        self.__ini.push()

        return generate_initialization_parameters_sgz(self.dataDirectory,
                                                      self.samplefileName,
                                                      ZVEC_FROM[self.zvec_from],
                                                      self.startDist,
                                                      self.step_z_scan,
                                                      self.image_per_point,
                                                      self.strideFile,
                                                      self.zvec_file,
                                                      self.pixelsize,
                                                      self.gratingPeriod,
                                                      PATTERNS[self.pattern],
                                                      self.sourceDistanceV,
                                                      self.sourceDistanceH,
                                                      self.unFilterSize,
                                                      self.searchRegion,
                                                      logger=self.__logger)

    def get_rejected_output(self):
        self.__logger.print_error("Initialization Canceled, Program exit")
        sys.exit(1)


from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class SGZInputParametersWidget(AbstractSGZInputParametersWidget, WavePyWidget):
    def __init__(self, application_name=None, **kwargs):
        AbstractSGZInputParametersWidget.__init__(self, application_name)
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
        return "Single Grating Z Scan Initialization Parameters"

    def _allows_saving(self):
        return False

class SGZInputParametersDialog(AbstractSGZInputParametersWidget, WavePyInteractiveWidget):
    def __init__(self, parent, application_name=None, **kwargs):
        AbstractSGZInputParametersWidget.__init__(self, application_name)
        WavePyInteractiveWidget.__init__(self, parent, message="Input Parameters", title="Input Parameters", application_name=application_name)
