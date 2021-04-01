import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt

from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches

from warnings import filterwarnings
filterwarnings("ignore")

class FitPeriodVsZPlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Pattern Period vs Detector distance " + self.__direction

    def build_widget(self, **kwargs):
        zvec             = kwargs["zvec"]
        args_for_NOfit   = kwargs["args_for_NOfit"]
        args_for_fit     = kwargs["args_for_fit"]
        pattern_period_z = kwargs["pattern_period_z"]
        lx               = kwargs["lx"]
        ls1              = kwargs["ls1"]
        lc2              = kwargs["lc2"]
        direction        = kwargs["direction"]

        try: figure_width = kwargs["figure_width"] * pixels_to_inches
        except: figure_width = 10
        try: figure_height = kwargs["figure_height"] * pixels_to_inches
        except: figure_height = 7

        output_data       = kwargs["output_data"]

        self.__direction = direction

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        figure = Figure(figsize=(figure_width, figure_height))
        figure.gca().plot(zvec[args_for_NOfit]*1e3, pattern_period_z[args_for_NOfit]*1e6, 'o', mec=lx, mfc='none', ms=8, label='not used for fit')
        figure.gca().plot(zvec[args_for_fit]*1e3, pattern_period_z[args_for_fit]*1e6, ls1, label=direction)

        fit1d                 = np.polyfit(zvec[args_for_fit], pattern_period_z[args_for_fit], 1)
        sourceDistance        = fit1d[1]/fit1d[0]
        patternPeriodFromData = fit1d[1]

        figure.gca().plot(zvec[args_for_fit]*1e3, (fit1d[0]*zvec[args_for_fit] + fit1d[1])*1e6, '-', c=lc2, lw=2, label='Fit ' + direction)
        figure.gca().text(np.min(zvec[args_for_fit])*1e3, np.min(pattern_period_z)*1e6, 'source dist = {:.2f}m, '.format(fit1d[1]/fit1d[0]) + r'$p_o$ = {:.3f}um'.format(fit1d[1]*1e6),
                          bbox=dict(facecolor=lc2, alpha=0.85))

        figure.gca().set_xlabel(r'Distance $z$  [mm]', fontsize=14)
        figure.gca().set_ylabel(r'Pattern Period [$\mu$m]', fontsize=14)
        figure.gca().set_title('Pattern Period vs Detector distance, ' + direction, fontsize=14, weight='bold')

        figure.gca().legend(fontsize=14, loc=1)

        self.append_mpl_figure_to_save(figure=figure)

        output_data.set_parameter("sourceDistance", sourceDistance)
        output_data.set_parameter("patternPeriodFromData", patternPeriodFromData)

        layout.addWidget(FigureCanvas(figure))

        self.setFixedWidth(figure_width/pixels_to_inches)
        self.setFixedHeight(figure_height/pixels_to_inches)
