import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt

from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, get_registered_plotter_instance

from warnings import filterwarnings
filterwarnings("ignore")

class VisibilityPlot(WavePyWidget):
    def get_plot_tab_name(self): return "Visibility vs detector distance"

    def build_mpl_figure(self, **kwargs):
        zvec      = kwargs["zvec"]
        contrastV = kwargs["contrastV"]
        contrastH = kwargs["contrastH"]

        # contrast vs z
        figure = Figure(figsize=(10, 7))
        figure.gca().plot(zvec * 1e3, contrastV * 100, '-ko', label='Vert')
        figure.gca().plot(zvec * 1e3, contrastH * 100, '-ro', label='Hor')
        figure.gca().set_xlabel(r'Distance $z$  [mm]', fontsize=14)
        figure.gca().set_ylabel(r'Visibility $\times$ 100 [%]', fontsize=14)
        figure.gca().set_title('Visibility vs detector distance', fontsize=14, weight='bold')
        figure.gca().legend(fontsize=14, loc=7)

        return figure
