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
from wavepy2.util.plot.plotter import WavePyWidget, WavePyInteractiveWidget

from wavepy2.tools.common.wavepy_data import WavePyData

from PyQt5.QtWidgets import QWidget

LENS_GEOMETRIES    = ["1Dx Horizontal focusing", "1Dy Vertical focusing", "2D Lens Stigmatic Lens"]

def generate_initialization_parameters_frl(thickness_file_name,
                                           str4title,
                                           nominalRadius,
                                           diameter4fit_str,
                                           lensGeometry,
                                           phenergy,
                                           crop_image,
                                           fit_radius_dpc):


    fname2save   = thickness_file_name.split('.')[0].split('/')[-1] + '_fit'
    residual_dir = thickness_file_name.rsplit('/', 1)[0] + PATH_SEPARATOR + 'residuals'

    saveFileSuf = residual_dir + PATH_SEPARATOR + fname2save

    os.makedirs(residual_dir, exist_ok=True)

    _, file_extension = os.path.splitext(thickness_file_name)

    # %% Load Input File

    if file_extension.lower() == '.sdf':
        thickness, pixelsize, _ = plot_tools.load_sdf_file(thickness_file_name)
        xx, yy = common_tools.realcoordmatrix(thickness.shape[1], pixelsize[1], thickness.shape[0], pixelsize[0])

    elif file_extension.lower() == '.pickle':
        thickness, xx, yy = plot_tools.load_pickle_surf(thickness_file_name, False)

        thickness *= 1e-6
        xx *= 1e-6
        yy *= 1e-6
        pixelsize = [np.mean(np.diff(xx[0, :])),
                     np.mean(np.diff(yy[:, 0]))]
    else:
        get_registered_logger_instance().print_error('Wrong file type!')
        sys.exit(-1)

    thickness -= np.nanmin(thickness)

    diameter4fit_list = [float(a)*1e-6 for a in diameter4fit_str.split(',')]
    
    return WavePyData(thickness_file_name=thickness_file_name,
                      thickness=thickness,
                      xx=xx,
                      yy=yy,
                      pixelsize=pixelsize,
                      str4title=str4title,
                      nominalRadius=nominalRadius,
                      diameter4fit_list=diameter4fit_list,
                      lensGeometry=lensGeometry,
                      phenergy=phenergy,
                      saveFileSuf=saveFileSuf,
                      crop_image=crop_image,
                      fit_radius_dpc=fit_radius_dpc)

class AbstractFRLInputParametersWidget():
    WIDTH  = 800
    HEIGHT = 430

    def __init__(self, application_name=None):
        self.__ini     = get_registered_ini_instance(application_name=application_name)
        self.__logger  = get_registered_logger_instance(application_name=application_name)

        self.thickness_file_name  = self.__ini.get_string_from_ini("Files", "file with thickness")

        self.str4title            = self.__ini.get_string_from_ini("Parameters", "String for Titles", default="Be Lens")
        self.nominalRadius        = self.__ini.get_float_from_ini("Parameters", "nominal radius for fitting", default=1e-4)
        self.diameter4fit_str     = self.__ini.get_string_from_ini("Parameters", "diameter of active area for fitting", default="800")
        self.lensGeometry         = LENS_GEOMETRIES.index(self.__ini.get_string_from_ini("Parameters", "lens geometry", default=LENS_GEOMETRIES[2]))
        self.phenergy             = self.__ini.get_float_from_ini("Parameters", "photon energy", default=14000.0)

        self.crop_image         = self.__ini.get_boolean_from_ini("Runtime", "crop image", default=False)
        self.fit_radius_dpc     = self.__ini.get_boolean_from_ini("Runtime", "fit radius dpc", default=False)

    def build_widget(self, **kwargs):
        try:    show_runtime_options = kwargs["show_runtime_options"]
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

        select_file_thickness_box = plot_tools.widgetBox(main_box, orientation="horizontal")
        self.le_thickness = plot_tools.lineEdit(select_file_thickness_box, self, "thickness_file_name", label="Thickness File to Plot\n(Pickle or sdf)", labelWidth=150, valueType=str, orientation="horizontal")
        plot_tools.button(select_file_thickness_box, self, "...", callback=self.selectThicknessFile)

        plot_tools.lineEdit(main_box, self, "str4title", label="String for Titles", labelWidth=250, valueType=str, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "nominalRadius", label="Nominal Radius For Fitting", labelWidth=350, valueType=float, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "diameter4fit_str", label="Diameter of active area for fitting\n(comma separated list)", labelWidth=250, valueType=str, orientation="horizontal")
        plot_tools.comboBox(main_box, self, "lensGeometry", label="Lens Geometry", items=LENS_GEOMETRIES, orientation="horizontal")
        plot_tools.lineEdit(main_box, self, "phenergy", label="Photon Energy", labelWidth=250, valueType=float, orientation="horizontal")

        if show_runtime_options:
            runtime_widget = QWidget()
            runtime_widget.setFixedHeight(widget_height-10)
            runtime_widget.setFixedWidth(widget_width-10)

            plot_tools.createTabPage(tabs, "Runtime Parameter", widgetToAdd=runtime_widget)

            main_box = plot_tools.widgetBox(runtime_widget, "", width=widget_width-70, height=widget_height-50)

            plot_tools.checkBox(main_box, self, "crop_image", "Crop Thickness Image")
            plot_tools.checkBox(main_box, self, "fit_radius_dpc", "Fit Radius DPC")

        self.update()

    def selectThicknessFile(self):
        self.le_thickness.setText(plot_tools.selectFileFromDialog(self, self.thickness_file_name, "Open Thickness File", file_extension_filter="Thickness Files (*.sdf *.pickle)"))

    def get_accepted_output(self):
        self.__ini.set_value_at_ini("Files", "file with thickness", self.thickness_file_name)
        self.__ini.set_value_at_ini("Parameters", "String for Titles", self.str4title)
        self.__ini.set_value_at_ini("Parameters", "nominal radius for fitting", self.nominalRadius)
        self.__ini.set_value_at_ini("Parameters", "diameter of active area for fitting", self.diameter4fit_str)
        self.__ini.set_value_at_ini("Parameters", "lens geometry", LENS_GEOMETRIES[self.lensGeometry])
        self.__ini.set_value_at_ini('Parameters', 'Photon Energy', self.phenergy)
        self.__ini.set_value_at_ini("Runtime", "crop image", self.crop_image)
        self.__ini.set_value_at_ini("Runtime", "fit radius dpc", self.fit_radius_dpc)

        self.__ini.push()

        return generate_initialization_parameters_frl(self.thickness_file_name,
                                                      self.str4title,
                                                      self.nominalRadius,
                                                      self.diameter4fit_str,
                                                      LENS_GEOMETRIES[self.lensGeometry],
                                                      self.phenergy,
                                                      self.crop_image,
                                                      self.fit_radius_dpc)

    def get_rejected_output(self):
        self.__logger.print_error("Initialization Canceled, Program exit")
        sys.exit(1)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class FRLInputParametersWidget(AbstractFRLInputParametersWidget, WavePyWidget):
    def __init__(self, application_name=None, **kwargs):
        AbstractFRLInputParametersWidget.__init__(self, application_name)
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
        return "Fit Residual Lenses Initialization Parameters"

    def _allows_saving(self):
        return False

class FRLInputParametersDialog(AbstractFRLInputParametersWidget, WavePyInteractiveWidget):
    def __init__(self, parent, application_name=None, **kwargs):
        AbstractFRLInputParametersWidget.__init__(self, application_name)
        WavePyInteractiveWidget.__init__(self, parent, message="Input Parameters", title="Input Parameters", application_name=application_name)
