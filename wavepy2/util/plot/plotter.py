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
from matplotlib.pyplot import rcParams

pixels_to_inches = 1/rcParams['figure.dpi']

class WavePyGenericWidget(object):
    def __init__(self, application_name=None): self._application_name = application_name
    def build_widget(self, **kwargs): raise NotImplementedError()

class FigureToSave():
    def __init__(self, figure_file_name=None, figure=None):
        self.__figure_file_name = figure_file_name
        self.__figure           = figure

    def save_figure(self, **kwargs):
        if not self.__figure is None: self.__figure.savefig(self.__figure_file_name, **kwargs)


class WavePyWidget(QWidget, WavePyGenericWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        QWidget.__init__(self, parent=parent)
        WavePyGenericWidget.__init__(self, application_name=application_name)

        self.__allows_saving = True
        self.__ignores_figure_dimensions = False

    def get_plot_tab_name(self): raise NotImplementedError()

    def build_widget(self, **kwargs):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        try: self.__allows_saving = kwargs["allows_saving"]
        except: self.__allows_saving = True

        try: self.__ignores_figure_dimensions = kwargs["ignores_figure_dimensions"]
        except: self.__ignores_figure_dimensions = False

        figure = self.build_mpl_figure(**kwargs)

        if not self._ignores_figure_dimensions():
            try:    figure_width = kwargs["figure_width"]*pixels_to_inches
            except: figure_width = figure.get_figwidth()
            try:    figure_height = kwargs["figure_height"]*pixels_to_inches
            except: figure_height = figure.get_figheight()

            figure.set_figwidth(figure_width)
            figure.set_figheight(figure_height)

        canvas = FigureCanvas(figure)
        canvas.setParent(self)

        self.append_mpl_figure_to_save(canvas.figure)

        try:    widget_width = kwargs["widget_width"]
        except: widget_width = canvas.get_width_height()[0]*1.1
        try:    widget_height = kwargs["widget_height"]
        except: widget_height = canvas.get_width_height()[1]*1.1

        self.setFixedWidth(widget_width)
        self.setFixedHeight(widget_height)

        layout.setStretchFactor(canvas, 1)
        layout.addWidget(canvas)

        self.setLayout(layout)

    def append_mpl_figure_to_save(self, figure, figure_file_name=None):
        if not hasattr(self, "__figures_to_save") or self.__figures_to_save is None: self.__figures_to_save = []
        self.__figures_to_save.append(FigureToSave(figure=figure,
                                                   figure_file_name=figure_file_name if not common_tools.is_empty_string(figure_file_name) else \
                                                       common_tools.get_unique_filename(get_registered_plotter_instance(application_name=self._application_name).get_save_file_prefix(), "png")))

    def build_mpl_figure(self, **kwargs): raise NotImplementedError()

    def _allows_saving(self): return self.__allows_saving
    def _ignores_figure_dimensions(self): return self.__ignores_figure_dimensions

    def get_figures_to_save(self):
        if self._allows_saving(): return self.__figures_to_save
        else: return None


class WavePyInteractiveWidget(QDialog, WavePyGenericWidget):

    def __init__(self, parent, message, title, application_name=None, **kwargs):
        QDialog.__init__(self, parent)
        WavePyGenericWidget.__init__(self, application_name=application_name)

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
    def register_context_window(self, context_key, context_window=None, use_unique_id=False): raise NotImplementedError()
    def register_save_file_prefix(self, save_file_prefix): raise NotImplementedError()
    def push_plot_on_context(self, context_key, widget_class, unique_id=None, **kwargs): raise NotImplementedError()
    def get_plots_of_context(self, context_key, unique_id=None): raise NotImplementedError()
    def get_context_container_widget(self, context_key, unique_id=None): raise  NotImplementedError()
    def get_save_file_prefix(self): raise NotImplementedError()
    def draw_context_on_widget(self, context_key, container_widget, add_context_label=True, unique_id=None, **kwargs): raise NotImplementedError()
    def draw_context(self, context_key, add_context_label=True, unique_id=None, **kwargs): raise NotImplementedError
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): raise NotImplementedError()
    def show_context_window(self, context_key, unique_id=None): raise NotImplementedError()
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

class _AbstractPlotter(PlotterFacade):

    def __init__(self, application_name=None):
        self._application_name = application_name

    @classmethod
    def _save_images(cls, plot_widget_instance, **kwargs):
        figures_to_save = plot_widget_instance.get_figures_to_save()

        if not figures_to_save is None:
            for figure_to_save in figures_to_save: figure_to_save.save_figure(**kwargs)

    @classmethod
    def _build_plot(cls, widget_class, application_name, **kwargs):
        if not issubclass(widget_class, WavePyWidget): raise ValueError("Widget class is not a WavePyWidget")

        try:
            plot_widget_instance = widget_class(parent=None, application_name=application_name, **kwargs)
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
        plot_tools.save_sdf_file(array, pixelsize, file_name, extraHeader, self._application_name)

        return file_name

    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""):
        file_name = self._get_file_name(file_prefix, file_suffix, "csv")
        plot_tools.save_csv_file(array_list, file_name, headerList, comments, self._application_name)

        return file_name

    def draw_context(self, context_key, add_context_label=True, unique_id=None, **kwargs):
        self.draw_context_on_widget(context_key, self.get_context_container_widget(context_key, unique_id), add_context_label, unique_id, **kwargs)

from wavepy2.util.plot.plot_tools import DefaultMainWindow

class _AbstractActivePlotter(_AbstractPlotter):
    def __init__(self, application_name=None):
        _AbstractPlotter.__init__(self, application_name=application_name)
        self.__plot_registry = {}
        self.__context_window_registry = {}

    def is_active(self): return True

    def _register_plot(self, context_key, plot_widget, unique_id=None):
        if not unique_id is None: context_key += "_" + unique_id

        if context_key in self.__plot_registry and not self.__plot_registry[context_key] is None:
            self.__plot_registry[context_key].append(plot_widget)
        else:
            self.__plot_registry[context_key] = [plot_widget]

    def register_context_window(self, context_key, context_window=None, use_unique_id=False):
        if context_window is None: context_window = DefaultMainWindow(context_key)
        if use_unique_id:
            unique_id = str(id(context_window))
            self.__context_window_registry[context_key + "_" + unique_id] = context_window
            return unique_id
        else:
            self.__context_window_registry[context_key] = context_window
            return None

    def get_plots_of_context(self, context_key, unique_id=None):
        if not unique_id is None: context_key += "_" + unique_id
        if context_key in self.__plot_registry: return self.__plot_registry[context_key]
        else: return None

    def get_context_container_widget(self, context_key, unique_id=None):
        if not unique_id is None: context_key += "_" + unique_id

        if context_key in self.__context_window_registry: return self.__context_window_registry[context_key].get_container_widget()
        else: return None

    def draw_context_on_widget(self, context_key, container_widget, add_context_label=True, unique_id=None, **kwargs):
        context_label = context_key
        if not unique_id is None: context_key += "_" + unique_id
        container_widget.setStyleSheet(plot_tools.stylesheet_string)

        main_box = plot_tools.widgetBox(container_widget, context_label if add_context_label else "", orientation="horizontal")
        main_box.layout().setAlignment(Qt.AlignCenter)
        tab_widget = plot_tools.tabWidget(main_box)

        widths  = []
        heights = []

        if context_key in self.__plot_registry:
            plot_widget_instances = self.__plot_registry[context_key]

            for plot_widget_instance in plot_widget_instances:
                tab = plot_tools.createTabPage(tab_widget, plot_widget_instance.get_plot_tab_name())
                tab.layout().setAlignment(Qt.AlignCenter)
                tab.layout().addWidget(plot_widget_instance)
                widths.append(plot_widget_instance.width())
                heights.append(plot_widget_instance.height())
        else:
            tab = plot_tools.createTabPage(tab_widget, context_label)

            label = plot_tools.widgetLabel(tab, "\n\n\n\n\n        Nothing to Display")
            label.setStyleSheet("font: 24pt")

            widths.append(500)
            heights.append(370)

        try:    tab_widget_width = kwargs["tab_widget_width"]
        except: tab_widget_width = max(widths) + 20
        try:    tab_widget_height = kwargs["tab_widget_height"]
        except: tab_widget_height = max(heights) + 35

        try:    main_box_width  = kwargs["main_box_width"]
        except: main_box_width  = tab_widget_width + 20
        try:    main_box_height = kwargs["main_box_height"]
        except: main_box_height = tab_widget_height + 40

        try:    container_widget_width  = kwargs["container_widget_width"]
        except: container_widget_width  = tab_widget_width + 25
        try:    container_widget_height = kwargs["container_widget_height"]
        except: container_widget_height = tab_widget_height + 55

        tab_widget.setFixedWidth(tab_widget_width)
        tab_widget.setFixedHeight(tab_widget_height)
        main_box.setFixedHeight(main_box_height)
        main_box.setFixedWidth(main_box_width)
        container_widget.setFixedWidth(container_widget_width)
        container_widget.setFixedHeight(container_widget_height)

        container_widget.update()

    def show_interactive_plot(self, widget_class, container_widget, **kwargs):
        if not issubclass(widget_class, WavePyInteractiveWidget): raise ValueError("Widget class is not a WavePyWidget")

        try:
            interactive_widget_instance = widget_class(parent=container_widget, application_name=self._application_name, **kwargs)
            interactive_widget_instance.build_widget(**kwargs)
        except Exception as e:
            raise ValueError("Plot Widget can't be created: " + str(e))

        return widget_class.get_output(interactive_widget_instance)

    def show_context_window(self, context_key, unique_id=None):
        if not unique_id is None: context_key += "_" + unique_id
        if context_key in self.__context_window_registry: self.__context_window_registry[context_key].show()
        else: pass

class __FullPlotter(_AbstractActivePlotter):
    def __init__(self, application_name=None): _AbstractActivePlotter.__init__(self, application_name=application_name)
    def is_saving(self): return True
    def push_plot_on_context(self, context_key, widget_class, unique_id=None, **kwargs):
        plot_widget_instance = self._build_plot(widget_class=widget_class, application_name=self._application_name, **kwargs)
        self._register_plot(context_key, plot_widget_instance, unique_id)
        self._save_images(plot_widget_instance, **kwargs)

class __DisplayOnlyPlotter(_AbstractActivePlotter):
    def __init__(self, application_name=None): _AbstractActivePlotter.__init__(self, application_name=application_name)
    def is_saving(self): return False
    def push_plot_on_context(self, context_key, widget_class, unique_id=None, **kwargs): self._register_plot(context_key, self._build_plot(widget_class=widget_class, application_name=self._application_name, **kwargs), unique_id)
    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}): return self._get_file_name(file_prefix, file_suffix, "sdf")
    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""): return self._get_file_name(file_prefix, file_suffix, "csv")

class __SaveOnlyPlotter(_AbstractActivePlotter):
    def __init__(self, application_name=None): _AbstractActivePlotter.__init__(self, application_name=application_name)
    def is_active(self): return False
    def is_saving(self): return True
    def register_context_window(self, context_key, context_window=None, use_unique_id=False): pass
    def push_plot_on_context(self, context_key, widget_class, unique_id=None, **kwargs): self._save_images(self._build_plot(widget_class=widget_class, application_name=self._application_name, **kwargs))
    def get_context_container_widget(self, context_key, unique_id=None): return None
    def get_plots_of_context(self, context_key, unique_id=None): pass
    def draw_context_on_widget(self, context_key, container_widget, add_context_label=True, unique_id=None, **kwargs): pass
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): pass
    def show_context_window(self, context_key, unique_id=None): pass

class __NullPlotter(_AbstractPlotter):
    def __init__(self, application_name=None): _AbstractActivePlotter.__init__(self, application_name=application_name)
    def is_active(self): return False
    def is_saving(self): return False
    def register_context_window(self, context_key, context_window=None, use_unique_id=False): pass
    def push_plot_on_context(self, context_key, widget_class, unique_id=None, **kwargs): self._build_plot(widget_class=widget_class, application_name=self._application_name, **kwargs) # necessary for some operations
    def get_context_container_widget(self, context_key, unique_id=None): return None
    def get_plots_of_context(self, context_key, unique_id=None): pass
    def draw_context_on_widget(self, context_key, container_widget, add_context_label=True, unique_id=None, **kwargs): pass
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): pass
    def show_context_window(self, context_key, unique_id=None): pass
    def save_sdf_file(self, array, pixelsize=[1, 1], file_prefix=None, file_suffix="", extraHeader={}): return self._get_file_name(file_prefix, file_suffix, "sdf")
    def save_csv_file(self, array_list, file_prefix=None, file_suffix="", headerList=[], comments=""): return self._get_file_name(file_prefix, file_suffix, "csv")

from wavepy2.util.common.common_tools import GenericRegistry

@Singleton
class __PlotterRegistry(GenericRegistry):

    def __init__(self):
        GenericRegistry.__init__(self, registry_name="Plotter")

    @synchronized_method
    def register_plotter(self, plotter_facade_instance, application_name=None, replace=False):
        super().register_instance(plotter_facade_instance, application_name, replace)

    @synchronized_method
    def reset(self, application_name=None):
        super().reset(application_name)

    def get_plotter_instance(self, application_name=None):
        return super().get_instance(application_name)

# -----------------------------------------------------
# Factory Methods

def register_plotter_instance(plotter_mode=PlotterMode.FULL, reset=False, application_name=None, replace=False):
    if reset: __PlotterRegistry.Instance().reset()

    if plotter_mode   == PlotterMode.FULL:         __PlotterRegistry.Instance().register_plotter(__FullPlotter(application_name), application_name, replace)
    elif plotter_mode == PlotterMode.DISPLAY_ONLY: __PlotterRegistry.Instance().register_plotter(__DisplayOnlyPlotter(application_name), application_name, replace)
    elif plotter_mode == PlotterMode.SAVE_ONLY:    __PlotterRegistry.Instance().register_plotter(__SaveOnlyPlotter(application_name), application_name, replace)
    elif plotter_mode == PlotterMode.NONE:         __PlotterRegistry.Instance().register_plotter(__NullPlotter(application_name), application_name, replace)

def get_registered_plotter_instance(application_name=None):
    return __PlotterRegistry.Instance().get_plotter_instance(application_name)

