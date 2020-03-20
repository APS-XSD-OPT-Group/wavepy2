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

from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QMessageBox, QDialogButtonBox
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class WavePyGenericWidget(object):
    def build_widget(self, **kwargs): raise NotImplementedError()

class WavePyWidget(QWidget, WavePyGenericWidget):

    def get_plot_tab_name(self): raise NotImplementedError()

    def build_widget(self, **kwargs):
        layout = QVBoxLayout()
        figure = self.build_figure(**kwargs)
        dpi = figure.get_dpi()
        figure.set_size_inches(w=(350/float(dpi)), h=(250/float(dpi)))
        canvas = FigureCanvas(figure)
        canvas.setParent(self)
        layout.addWidget(canvas)
        layout.setStretchFactor(canvas, 1)

        self.setLayout(layout)

    def build_figure(self, **kwargs): raise NotImplementedError()

class WavePyInteractiveWidget(QDialog, WavePyGenericWidget):

    def __init__(self, parent, message, title, width=800, height=600):
        super(QDialog, self).__init__(parent)

        self.setWindowTitle(message)
        self.setModal(True)

        self.central_widget = plot_tools.widgetBox(self, title, "vertical")

        layout = QVBoxLayout(self)

        button_box = QDialogButtonBox(orientation=Qt.Horizontal,
                                      standardButtons=QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        button_box.accepted.connect(self.__accepted)
        button_box.rejected.connect(self.__rejected)
        layout.addWidget(self.central_widget)
        layout.addWidget(button_box)

        self.output = None

    def __accepted(self):
        self.output = self.get_user_selection()
        self.accept()

    def __rejected(self):
        self.output = None
        self.reject()

    def get_user_selection(self): raise NotImplementedError(0)

    def get_central_widget(self):
        return self.central_widget

    @classmethod
    def get_output(cls, dialog):
        dialog.exec_()
        return dialog.output

class PlotterFacade:
    def push_plot(self, context_key, widget_class, **kwargs): raise NotImplementedError()
    def get_context_plots(self, context_key): raise NotImplementedError()
    def draw_context_on_widget(self, context_key, container_widget): raise NotImplementedError()
    def show_interactive_plot(self, widget_class, **kwargs): raise NotImplementedError()

class PlotterMode:
    FULL = 0
    NONE = 1

class __FullPlotter(PlotterFacade):
    def __init__(self):
        self.__plot_dictionary = {}

    def push_plot(self, context_key, widget_class, **kwargs):
        if not issubclass(widget_class, WavePyWidget): raise ValueError("Widget class is not a WavePyWidget")

        try:
            plot_widget_instance = widget_class()
            plot_widget_instance.build_widget(**kwargs)
        except Exception as e:
            raise ValueError("Plot Widget can't be created: " + str(e))

        if context_key in self.__plot_dictionary and not self.__plot_dictionary[context_key] is None:
            self.__plot_dictionary[context_key].append(plot_widget_instance)
        else:
            self.__plot_dictionary[context_key] = [plot_widget_instance]

    def get_context_plots(self, context_key):
        if context_key in self.__plot_dictionary: return self.__plot_dictionary[context_key]
        else: return None

    def draw_context_on_widget(self, context_key, container_widget, width=800, height=600):
        container_widget.setMinimumWidth(width)
        container_widget.setMinimumHeight(height)

        main_box = plot_tools.widgetBox(container_widget, context_key, orientation="vertical")
        tab_widget = plot_tools.tabWidget(main_box)

        if context_key in self.__plot_dictionary:
            for plot_widget_instance in self.__plot_dictionary[context_key]:
                plot_tools.createTabPage(tab_widget,
                                         plot_widget_instance.get_plot_tab_name(),
                                         plot_widget_instance)

        container_widget.update()

    def show_interactive_plot(self, widget_class, container_widget, **kwargs):
        if not issubclass(widget_class, WavePyInteractiveWidget): raise ValueError("Widget class is not a WavePyWidget")

        try:
            interactive_widget_instance = widget_class(parent=container_widget)
            interactive_widget_instance.build_widget(**kwargs)
        except Exception as e:
            raise ValueError("Plot Widget can't be created: " + str(e))

        return widget_class.get_output(interactive_widget_instance)


class __NullPlotter(PlotterFacade):
    def push_plot(self, context_key, widget_class, **kwargs): pass
    def get_context_plots(self, context_key): pass
    def draw_context_on_widget(self, context_key, container_widget): pass
    def show_interactive_plot(self, widget_class, container_widget, **kwargs): pass


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
    if plotter_mode == PlotterMode.FULL:      __PlotterRegistry.Instance().register_plotter(__FullPlotter())
    elif plotter_mode == PlotterMode.NONE:    __PlotterRegistry.Instance().register_plotter(__NullPlotter())

def get_registered_plotter_instance():
    return __PlotterRegistry.Instance().get_plotter_instance()

