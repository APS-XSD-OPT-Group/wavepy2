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
from aps.common.widgets.generic_widget import GenericWidget, GenericInteractiveWidget, FigureToSave, pixels_to_inches
from aps.common.plotter import FullPlotter, DisplayOnlyPlotter, SaveOnlyPlotter, NullPlotter, PlotterRegistry, PlotterMode, PlotterFacade

from aps.wavepy2.util.common import common_tools
from aps.wavepy2.util.plot import plot_tools

class WavePyWidget(GenericWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(WavePyWidget, self).__init__(parent, application_name, **kwargs)

    def _check_figure_file_name(self, figure_file_name):
        return figure_file_name if not common_tools.is_empty_string(figure_file_name) else \
               common_tools.get_unique_filename(get_registered_plotter_instance(application_name=self._application_name).get_save_file_prefix(), "png")

class WavePyInteractiveWidget(GenericInteractiveWidget):
    def __init__(self, parent, message, title, application_name=None, **kwargs):
        super(WavePyInteractiveWidget, self).__init__(parent, message, title, application_name, **kwargs)

class WavePyPlotterFacade:
    def save_sdf_file(self, array, pixelsize, file_prefix, file_suffix, extraHeader): raise NotImplementedError()
    def save_csv_file(self, array_list, file_prefix, file_suffix, headerList, comments): raise NotImplementedError()

class PlotterMode:
    FULL         = 0
    DISPLAY_ONLY = 1
    SAVE_ONLY    = 2
    NONE         = 3
    
    @classmethod
    def get_plotter_mode(cls, plotter_mode=FULL):
        if plotter_mode==cls.FULL: return "Full" 
        if plotter_mode==cls.DISPLAY_ONLY: return "Display Only" 
        if plotter_mode==cls.SAVE_ONLY: return "Save Only" 
        if plotter_mode==cls.NONE: return "None" 

class WavePyPlotter(WavePyPlotterFacade):
    def _get_file_name(self, file_prefix=None, file_suffix="", extension=""):
        return common_tools.get_unique_filename(str(self.get_save_file_prefix() if file_prefix is None else file_prefix) + file_suffix, extension)

    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}):
        file_name = self._get_file_name(file_prefix, file_suffix, "sdf")
        plot_tools.save_sdf_file(array, pixelsize, file_name, extraHeader, self._application_name)

        return file_name

    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""):
        file_name = self._get_file_name(file_prefix, file_suffix, "csv")
        plot_tools.save_csv_file(array_list, file_name, headerList, comments, self._application_name)

        return file_name

class __FullPlotter(FullPlotter, WavePyPlotter):
    def __init__(self, application_name=None): FullPlotter.__init__(self, application_name=application_name)

class __DisplayOnlyPlotter(DisplayOnlyPlotter, WavePyPlotter):
    def __init__(self, application_name=None): DisplayOnlyPlotter.__init__(self, application_name=application_name)
    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}): return self._get_file_name(file_prefix, file_suffix, "sdf")
    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""): return self._get_file_name(file_prefix, file_suffix, "csv")

class __SaveOnlyPlotter(SaveOnlyPlotter, WavePyPlotter):
    def __init__(self, application_name=None): SaveOnlyPlotter.__init__(self, application_name=application_name)

class __NullPlotter(NullPlotter, WavePyPlotter):
    def __init__(self, application_name=None): NullPlotter.__init__(self, application_name=application_name)
    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}): return self._get_file_name(file_prefix, file_suffix, "sdf")
    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""): return self._get_file_name(file_prefix, file_suffix, "csv")

# -----------------------------------------------------
# Factory Methods

def register_plotter_instance(plotter_mode=PlotterMode.FULL, reset=False, application_name=None, replace=False):
    if reset: PlotterRegistry.Instance().reset()

    if plotter_mode   == PlotterMode.FULL:         PlotterRegistry.Instance().register_plotter(__FullPlotter(application_name), application_name, replace)
    elif plotter_mode == PlotterMode.DISPLAY_ONLY: PlotterRegistry.Instance().register_plotter(__DisplayOnlyPlotter(application_name), application_name, replace)
    elif plotter_mode == PlotterMode.SAVE_ONLY:    PlotterRegistry.Instance().register_plotter(__SaveOnlyPlotter(application_name), application_name, replace)
    elif plotter_mode == PlotterMode.NONE:         PlotterRegistry.Instance().register_plotter(__NullPlotter(application_name), application_name, replace)

def get_registered_plotter_instance(application_name=None):
    return PlotterRegistry.Instance().get_plotter_instance(application_name)

