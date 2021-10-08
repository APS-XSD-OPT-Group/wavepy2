import numpy as np
from scipy.optimize import curve_fit

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches

from warnings import filterwarnings
filterwarnings("ignore")

class VisibilityPlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Visibility vs detector distance"

    def build_widget(self, **kwargs):
        zvec             = kwargs["zvec"]
        pattern_period   = kwargs["pattern_period"]
        source_distance  = kwargs["source_distance"]
        contrast         = kwargs["contrast"]
        ls1              = kwargs["ls1"]
        lc2              = kwargs["lc2"]
        direction        = kwargs["direction"]

        wavelength = kwargs["wavelength"]

        try: figure_width = kwargs["figure_width"] * pixels_to_inches
        except: figure_width = 10
        try: figure_height = kwargs["figure_height"] * pixels_to_inches
        except: figure_height = 7

        output_data       = kwargs["output_data"]

        self.__direction = direction

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        def _func_4_fit(z, Amp, z_period, sigma, phase, sourceDist, z0):
            return Amp*np.abs(np.sin((z-z0)/z_period*np.pi/(1 + (z-z0)/sourceDist) +
                                     phase*2*np.pi)) * \
                                     np.exp(-(z-z0)**2/2/sigma**2/(1 + (z-z0)/sourceDist)**2)

        p0 = [1.0, pattern_period**2/wavelength, .96, 0.05, source_distance, 1e-6]

        shift_limit = 0.05*(zvec[-1] - zvec[0])

        bounds_low = [1e-3, p0[1]*0.9999, .01, -.1, source_distance*(0.9999 if source_distance > 0 else 1.0001), -shift_limit]
        bounds_up  = [2.0,  p0[1]*1.0001,  10., .1, source_distance*(1.0001 if source_distance > 0 else 0.9999), shift_limit]

        popt, pcov = curve_fit(_func_4_fit, zvec, contrast, p0=p0, bounds=(bounds_low, bounds_up))

        coherence_length = np.abs(popt[2])*wavelength/(np.sqrt(wavelength*popt[1]))
        source_size = wavelength*np.abs(source_distance)/(2*np.pi*coherence_length)

        fitted_curve = _func_4_fit(zvec, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
        envelope     = _func_4_fit(zvec, popt[0], 1e10,    popt[2], 1/4,     popt[4], popt[5])

        results_Text =  'z_period [m] : ' + str('{:.6g}'.format(popt[1]) + '\n')
        results_Text += 'z shift [mm] : ' + str('{:.3g}'.format(popt[5]*1e3) + '\n')
        results_Text += 'Coherent length: {:.6g} um\n'.format(coherence_length*1e6)
        results_Text += 'Source size: {:.6g} um\n'.format(source_size*1e6)

        # contrast vs z
        figure = Figure(figsize=(figure_width, figure_height))
        figure.gca().plot(zvec * 1e3, contrast * 100, ls1, label='Data')
        figure.gca().plot(zvec * 1e3, fitted_curve * 100, lc2, label='Fit')
        figure.gca().plot(zvec * 1e3, envelope * 100, 'b', label='Envelope')
        figure.gca().set_xlabel(r'Distance $z$  [mm]', fontsize=14)
        figure.gca().set_ylabel(r'Visibility $\times$ 100 [%]', fontsize=14)
        figure.gca().set_title('Visibility vs detector distance, ' + direction, fontsize=14, weight='bold')
        figure.gca().legend(fontsize=14, loc=7)

        figure.gca().text(np.max(zvec)*0.7*1e3, max(np.max(contrast), np.max(fitted_curve))*0.85*100, results_Text,
                          bbox=dict(facecolor=lc2, alpha=0.85))

        self.append_mpl_figure_to_save(figure=figure)

        output_data.set_parameter("coherence_length", coherence_length)
        output_data.set_parameter("source_size", source_size)

        layout.addWidget(FigureCanvas(figure))

        self.setFixedWidth(figure_width/pixels_to_inches)
        self.setFixedHeight(figure_height/pixels_to_inches)
