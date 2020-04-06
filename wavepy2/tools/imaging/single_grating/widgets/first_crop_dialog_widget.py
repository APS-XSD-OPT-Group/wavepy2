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
from wavepy2.util.plot.widgets.figure_slide_colorbar import FigureSlideColorbar
from wavepy2.util.plot.widgets.graphical_roi_idx import GraphicalRoiIdx
from wavepy2.util.plot.widgets.simple_plot import SimplePlot
from wavepy2.util.common import common_tools
from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import get_registered_logger_instance, LoggerColor
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyInteractiveWidget


class FirstCropDialogPlot(WavePyInteractiveWidget):
    __initialized = False

    def __init__(self, parent):
        super(FirstCropDialogPlot, self).__init__(parent, message="New Crop?", title="Crop Image")
        self.__ini     = get_registered_ini_instance()
        self.__logger  = get_registered_logger_instance()

    def build_widget(self, **kwargs):
        img         = kwargs["img"]
        pixelsize   = kwargs["pixelsize"]

        idx4crop = self.__ini.get_list_from_ini("Parameters", "Crop", default=[0, -1, 0, -1])

        self.__initialize(img, idx4crop)
        self.__logger.print_other(idx4crop, "Stored Crop Indexes: ", color=LoggerColor.RED)

        original_cropped_image = SimplePlot(self,
                                            image=self.__cropped_img,
                                            title="Raw Image with initial Crop",
                                            xlabel=r'$[\mu m]$',
                                            ylabel=r'$[\mu m]$',
                                            extent=common_tools.extent_func(self.__cropped_img, pixelsize) * 1e6)

        crop_image = GraphicalRoiIdx(self,
                                     image=img,
                                     set_crop_output_listener=self.create_cropped_output)

        figure_slide_colorbar = FigureSlideColorbar(self,
                                                    image=img,
                                                    title='SELECT COLOR SCALE,\nRaw Image, No Crop',
                                                    xlabel=r'x [$\mu m$ ]',
                                                    ylabel=r'y [$\mu m$ ]',
                                                    extent=common_tools.extent_func(img, pixelsize)*1e6)

        figure_slide_colorbar.set_images_to_change([crop_image.get_image_to_change()])

        tab_widget = plot_tools.tabWidget(self.get_central_widget())

        plot_tools.createTabPage(tab_widget, "Raw Image",  original_cropped_image)
        plot_tools.createTabPage(tab_widget, "Colormap",   figure_slide_colorbar)
        plot_tools.createTabPage(tab_widget, "Crop Image", crop_image)

        self.setFixedWidth(max(original_cropped_image.width(), figure_slide_colorbar.width(), crop_image.width())*1.1)

        self.update()

    def get_accepted_output(self):
        if self.__initialized: self.__ini.set_list_at_ini('Parameters', 'Crop', self.__idx4crop)

        return self.__cropped_img, self.__idx4crop

    def get_rejected_output(self):
        if self.__initialized: self.__ini.set_list_at_ini('Parameters', 'Crop', self.__initial_idx4crop)

        cropped_img = common_tools.crop_matrix_at_indexes(self.__uncropped_img, self.__initial_idx4crop)

        return  cropped_img, self.__initial_idx4crop

    def create_cropped_output(self, idx4crop):
        self.__cropped_img = common_tools.crop_matrix_at_indexes(self.__uncropped_img, idx4crop)
        self.__idx4crop    = idx4crop

    def __initialize(self, img, idx4crop):
        self.__uncropped_img    = img
        self.__initial_idx4crop = idx4crop

        self.create_cropped_output(idx4crop)

        self.__initialized = True
