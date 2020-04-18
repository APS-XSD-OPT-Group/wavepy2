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
from wavepy2.util import Singleton, synchronized_method
from wavepy2.util.plot import plot_tools
from wavepy2.util.common import common_tools

from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class WavePyGenericWidget(object):
    def build_widget(self, **kwargs): raise NotImplementedError()

class FigureToSave():
    def __init__(self, figure_file_name=None, figure=None):
        self.__figure_file_name = figure_file_name
        self.__figure           = figure

    def save_figure(self, **kwargs):
        if not self.__figure is None: self.__figure.savefig(self.__figure_file_name, **kwargs)


class WavePyWidget(QWidget, WavePyGenericWidget):
    def __init__(self, parent=None):
        super(WavePyWidget, self).__init__(parent=parent)

        self.__allows_saving = True

    def get_plot_tab_name(self): raise NotImplementedError()

    def build_widget(self, **kwargs):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        try: self.__allows_saving = kwargs["allows_saving"]
        except: pass

        canvas = FigureCanvas(self.build_mpl_figure(**kwargs))
        canvas.setParent(self)

        self.append_mpl_figure_to_save(canvas.figure)

        self.setFixedWidth(canvas.get_width_height()[0]*1.1)
        self.setFixedHeight(canvas.get_width_height()[1]*1.1)
        layout.setStretchFactor(canvas, 1)
        layout.addWidget(canvas)

        self.setLayout(layout)

    def append_mpl_figure_to_save(self, figure, figure_file_name=None):
        if not hasattr(self, "__figures_to_save") or self.__figures_to_save is None: self.__figures_to_save = []
        self.__figures_to_save.append(FigureToSave(figure=figure,
                                                   figure_file_name=figure_file_name if not common_tools.is_empty_string(figure_file_name) else \
                                                       common_tools.get_unique_filename(get_registered_plotter_instance().get_save_file_prefix(), "png")))

    def build_mpl_figure(self, **kwargs): raise NotImplementedError()

    def allows_saving(self): return self.__allows_saving

    def get_figures_to_save(self):
        if self.allows_saving(): return self.__figures_to_save
        else: return None


class WavePyInteractiveWidget(QDialog, WavePyGenericWidget):

    def __init__(self, parent, message, title):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle(message)
        self.setModal(True)

        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        self.__central_widget = plot_tools.widgetBox(self, title, "vertical")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        button_box = QDialogButtonBox(orientation=Qt.Horizontal,
                                      standardButtons=QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.__accepted)
        button_box.rejected.connect(self.__rejected)
        layout.addWidget(self.__central_widget)
        layout.addWidget(button_box)

        self.__output = None

    def __accepted(self):
        self.__output = self.get_accepted_output()
        self.accept()

    def __rejected(self):
        self.__output = self.get_rejected_output()
        self.reject()

    def get_output_object(self):
        return self.__output

    def get_accepted_output(self): raise NotImplementedError()
    def get_rejected_output(self): raise NotImplementedError()

    def get_central_widget(self):
        return self.__central_widget

    @classmethod
    def get_output(cls, dialog):
        dialog.exec_()

        return dialog.get_output_object()

class PlotterFacade:
    def is_active(self): raise NotImplementedError()
    def is_saving(self): raise NotImplementedError()
    def register_context_window(self, context_key, context_window=None): raise NotImplementedError()
    def register_save_file_prefix(self, save_file_prefix): raise NotImplementedError()
    def push_plot_on_context(self, context_key, widget_class, **kwargs): raise NotImplementedError()
    def get_plots_of_context(self, context_key): raise NotImplementedError()
    def get_context_container_widget(self, context_key): raise  NotImplementedError()
    def get_save_file_prefix(self): raise NotImplementedError()
    def draw_context_on_widget(self, context_key, container_widget): raise NotImplementedError()
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): raise NotImplementedError()
    def show_context_window(self, context_key): raise NotImplementedError()
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

class __AbstractPlotter(PlotterFacade):

    @classmethod
    def _save_images(cls, plot_widget_instance, **kwargs):
        figures_to_save = plot_widget_instance.get_figures_to_save()

        if not figures_to_save is None:
            for figure_to_save in figures_to_save: figure_to_save.save_figure(**kwargs)

    @classmethod
    def _build_plot(cls, widget_class, **kwargs):
        if not issubclass(widget_class, WavePyWidget): raise ValueError("Widget class is not a WavePyWidget")

        try:
            plot_widget_instance = widget_class()
            plot_widget_instance.build_widget(**kwargs)

            return plot_widget_instance
        except Exception as e:
            raise ValueError("Plot Widget can't be created: " + str(e))

    def register_save_file_prefix(self, save_file_prefix): self.__save_file_prefix = save_file_prefix

    def get_save_file_prefix(self): return self.__save_file_prefix

    def _get_file_name(self, file_prefix=None, file_suffix="", extension=""):
        return common_tools.get_unique_filename(str(self.get_save_file_prefix() if file_prefix is None else file_prefix) + file_suffix, extension)

    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}):
        file_name = self._get_file_name(file_prefix, file_suffix, "sdf")
        plot_tools.save_sdf_file(array, pixelsize, file_name, extraHeader)

        return file_name

    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""):
        file_name = self._get_file_name(file_prefix, file_suffix, "csv")
        plot_tools.save_csv_file(array_list, file_name, headerList, comments)

        return file_name

from wavepy2.util.plot.plot_tools import DefaultMainWindow

class __AbstractActivePlotter(__AbstractPlotter):
    def __init__(self):
        self.__plot_registry = {}
        self.__context_window_registry = {}

    def is_active(self): return True

    def _register_plot(self, context_key, plot_widget):
        if context_key in self.__plot_registry and not self.__plot_registry[context_key] is None:
            self.__plot_registry[context_key].append(plot_widget)
        else:
            self.__plot_registry[context_key] = [plot_widget]

    def register_context_window(self, context_key, context_window=None):
        if context_window is None: context_window = DefaultMainWindow(context_key)
        self.__context_window_registry[context_key] = context_window

    def get_plots_of_context(self, context_key):
        if context_key in self.__plot_registry: return self.__plot_registry[context_key]
        else: return None

    def get_context_container_widget(self, context_key):
        if context_key in self.__context_window_registry: return self.__context_window_registry[context_key].get_container_widget()
        else: return None

    def draw_context_on_widget(self, context_key, container_widget):
        main_box = plot_tools.widgetBox(container_widget, context_key, orientation="horizontal")
        main_box.layout().setAlignment(Qt.AlignCenter)
        tab_widget = plot_tools.tabWidget(main_box)

        widths  = []
        heights = []

        if context_key in self.__plot_registry:
            for plot_widget_instance in self.__plot_registry[context_key]:
                tab = plot_tools.createTabPage(tab_widget, plot_widget_instance.get_plot_tab_name())
                tab.layout().setAlignment(Qt.AlignCenter)
                tab.layout().addWidget(plot_widget_instance)
                widths.append(plot_widget_instance.width())
                heights.append(plot_widget_instance.height())
        else:
            label = plot_tools.widgetLabel(tab_widget, "\n\n\n\n\n        Nothing to Display")
            label.setStyleSheet("font: 24pt")
            widths.append(500)
            heights.append(370)

        tab_widget.setFixedWidth(max(widths)+20)
        tab_widget.setFixedHeight(max(heights)+35)
        container_widget.setFixedWidth(tab_widget.width()+25)
        container_widget.setFixedHeight(tab_widget.height()+40)

        container_widget.update()

    def show_interactive_plot(self, widget_class, container_widget, **kwargs):
        if not issubclass(widget_class, WavePyInteractiveWidget): raise ValueError("Widget class is not a WavePyWidget")

        try:
            interactive_widget_instance = widget_class(parent=container_widget)
            interactive_widget_instance.build_widget(**kwargs)
        except Exception as e:
            raise ValueError("Plot Widget can't be created: " + str(e))

        return widget_class.get_output(interactive_widget_instance)

    def show_context_window(self, context_key):
        if context_key in self.__context_window_registry: self.__context_window_registry[context_key].show()
        else: pass

class __FullPlotter(__AbstractActivePlotter):
    def is_saving(self): return True
    def push_plot_on_context(self, context_key, widget_class, **kwargs):
        plot_widget_instance = self._build_plot(widget_class, **kwargs)
        self._register_plot(context_key, plot_widget_instance)
        self._save_images(plot_widget_instance, **kwargs)

class __DisplayOnlyPlotter(__AbstractActivePlotter):
    def is_saving(self): return False
    def push_plot_on_context(self, context_key, widget_class, **kwargs): self._register_plot(context_key, self._build_plot(widget_class, **kwargs))
    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}): return self._get_file_name(file_prefix, file_suffix, "sdf")
    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""): return self._get_file_name(file_prefix, file_suffix, "csv")

class __SaveOnlyPlotter(__AbstractActivePlotter):
    def is_active(self): return False
    def is_saving(self): return True
    def register_context_window(self, context_key, context_window=None): pass
    def push_plot_on_context(self, context_key, widget_class, **kwargs): self._save_images(self._build_plot(widget_class, **kwargs))
    def get_context_container_widget(self, context_key): return None
    def get_plots_of_context(self, context_key): pass
    def draw_context_on_widget(self, context_key, container_widget): pass
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): pass
    def show_context_window(self, context_key): pass

class __NullPlotter(__AbstractPlotter):
    def is_active(self): return False
    def is_saving(self): return False
    def register_context_window(self, context_key, context_window=None): pass
    def push_plot_on_context(self, context_key, widget_class, **kwargs): self._build_plot(widget_class, **kwargs) # necessary for some operations
    def get_context_container_widget(self, context_key): return None
    def get_plots_of_context(self, context_key): pass
    def draw_context_on_widget(self, context_key, container_widget): pass
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): pass
    def show_context_window(self, context_key): pass
    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}): return self._get_file_name(file_prefix, file_suffix, "sdf")
    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""): return self._get_file_name(file_prefix, file_suffix, "csv")

@Singleton
class __PlotterRegistry:

    def __init__(self):
        self.__plotter_instance = None

    @synchronized_method
    def register_plotter(self, plotter_facade_instance = None):
        if plotter_facade_instance is None: raise ValueError("Plotter Instance is None")
        if not isinstance(plotter_facade_instance, PlotterFacade): raise ValueError("Plotter Instance do not implement Plotter Facade")

        if self.__plotter_instance is None: self.__plotter_instance = plotter_facade_instance
        else: raise ValueError("Plotter Instance already initialized")

    @synchronized_method
    def reset(self):
        self.__plotter_instance = None

    def get_plotter_instance(self):
        return self.__plotter_instance

# -----------------------------------------------------
# Factory Methods

def register_plotter_instance(plotter_mode=PlotterMode.FULL, reset=False):
    if reset: __PlotterRegistry.Instance().reset()

    if plotter_mode   == PlotterMode.FULL:         __PlotterRegistry.Instance().register_plotter(__FullPlotter())
    elif plotter_mode == PlotterMode.DISPLAY_ONLY: __PlotterRegistry.Instance().register_plotter(__DisplayOnlyPlotter())
    elif plotter_mode == PlotterMode.SAVE_ONLY:    __PlotterRegistry.Instance().register_plotter(__SaveOnlyPlotter())
    elif plotter_mode == PlotterMode.NONE:         __PlotterRegistry.Instance().register_plotter(__NullPlotter())

def get_registered_plotter_instance():
    return __PlotterRegistry.Instance().get_plotter_instance()

