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
from wavepy2.util.common import common_tools
from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyInteractiveWidget
from wavepy2.tools.common.widgets.graphical_roi_idx import GraphicalRoiIdx

FIXED_WIDTH=800

class CropDialogPlot(WavePyInteractiveWidget):
    __initialized = False

    def __init__(self, parent):
        super(CropDialogPlot, self).__init__(parent, message="New Crop?", title="Crop Image")
        self.__logger  = get_registered_logger_instance()

    def build_widget(self, **kwargs):
        img = kwargs["img"]

        try: self.setWindowTitle(kwargs["message"])
        except: pass

        try:    default_idx4crop = kwargs["default_idx4crop"]
        except: default_idx4crop = [0, -1, 0, -1]

        self.__initialize(img, default_idx4crop)

        try:    crop_image = GraphicalRoiIdx(self, image=img, set_crop_output_listener=self.create_cropped_output, kwargs4graph=kwargs["kwargs4graph"])
        except: crop_image = GraphicalRoiIdx(self, image=img, set_crop_output_listener=self.create_cropped_output)

        tab_widget = plot_tools.tabWidget(self.get_central_widget())

        plot_tools.createTabPage(tab_widget, "Crop Image", crop_image)

        self.setFixedWidth(FIXED_WIDTH)

        self.update()

    def get_accepted_output(self):
        return self.__img, self.__idx4crop

    def get_rejected_output(self):
        return self.__initial_img , self.__initial_idx4crop

    def create_cropped_output(self, idx4crop):
        self.__img      = common_tools.crop_matrix_at_indexes(self.__initial_img, idx4crop)
        self.__idx4crop = idx4crop

    def __initialize(self, img, default_idx4crop):
        self.__initial_img      = img
        self.__initial_idx4crop = default_idx4crop
        self.__img      = self.__initial_img
        self.__idx4crop = self.__initial_idx4crop
