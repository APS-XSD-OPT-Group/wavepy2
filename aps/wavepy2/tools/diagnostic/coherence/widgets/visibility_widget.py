import numpy as np
from scipy.optimize import curve_fit

from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from aps.wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches
from aps.util.plot.gui import widgetBox, separator, button, checkBox, lineEdit

from warnings import filterwarnings
filterwarnings("ignore")

epsilon = 1e-9

class VisibilityPlot(WavePyWidget):
    zvec_min = 0.0
    zvec_max = 0.0

    z_period = 0.0
    z_period_min = 0.0
    z_period_max = 0.0
    z_period_fixed = 1

    source_distance = 0.0
    source_distance_min = 0.0
    source_distance_max = 0.0
    source_distance_fixed = 1

    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Visibility vs detector distance"

    def build_widget(self, **kwargs):
        self.__zvec             = kwargs["zvec"]
        self.zvec_min           = np.round(np.min(self.__zvec)*1e3, 2) # mm
        self.zvec_max           = np.round(np.max(self.__zvec)*1e3, 2)
        self.__wavelength       = kwargs["wavelength"]
        self.z_period           = np.round(kwargs["pattern_period"]**2/self.__wavelength, 6)
        self.source_distance    = np.round(kwargs["source_distance"], 3)
        self.__contrast         = kwargs["contrast"]
        self.__ls1              = kwargs["ls1"]
        self.__lc2              = kwargs["lc2"]
        self.__direction        = kwargs["direction"]


        try: figure_width = kwargs["figure_width"] * pixels_to_inches
        except: figure_width = 10
        try: figure_height = kwargs["figure_height"] * pixels_to_inches
        except: figure_height = 7

        output_data       = kwargs["output_data"]

        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        fit_params_container = QWidget()
        fit_params_container.setFixedWidth(280)
        fit_params_container.setFixedHeight(figure_width/pixels_to_inches)

        fit_params_box = widgetBox(fit_params_container, "Fit Parameters", orientation="vertical", width=260)

        lineEdit(fit_params_box, self, "zvec_min", "Z min [mm]", labelWidth=120, orientation="horizontal", valueType=float)
        lineEdit(fit_params_box, self, "zvec_max", "Z max [mm]", labelWidth=120, orientation="horizontal", valueType=float)
        separator(fit_params_box)
        z_period_box = widgetBox(fit_params_box, "", orientation="horizontal", width=240)
        self.__le_z_period = lineEdit(z_period_box, self, "z_period", "Z period [m]", labelWidth=100, orientation="horizontal", valueType=float)

        def set_z_period():
            self.__le_z_period_min.setEnabled(not self.z_period_fixed)
            self.__le_z_period_max.setEnabled(not self.z_period_fixed)

        checkBox(z_period_box, self, "z_period_fixed", "fix", callback=set_z_period)
        z_period_box_2 = widgetBox(fit_params_box, "", orientation="horizontal", width=240)
        self.__le_z_period_min = lineEdit(z_period_box_2, self, "z_period_min", "min", orientation="horizontal", valueType=float)
        self.__le_z_period_max = lineEdit(z_period_box_2, self, "z_period_max", "max", orientation="horizontal", valueType=float)
        set_z_period()

        separator(fit_params_box)
        source_distance_box = widgetBox(fit_params_box, "", orientation="horizontal", width=240)
        self.__le_source_distance = lineEdit(source_distance_box, self, "source_distance", "Source distance [m]", labelWidth=120, orientation="horizontal", valueType=float)

        def set_source_distance():
            self.__le_source_distance_min.setEnabled(not self.source_distance_fixed)
            self.__le_source_distance_max.setEnabled(not self.source_distance_fixed)

        checkBox(source_distance_box, self, "source_distance_fixed", "fix", callback=set_source_distance)
        source_distance_box_2 = widgetBox(fit_params_box, "", orientation="horizontal", width=240)
        self.__le_source_distance_min = lineEdit(source_distance_box_2, self, "source_distance_min", "min", orientation="horizontal", valueType=float)
        self.__le_source_distance_max = lineEdit(source_distance_box_2, self, "source_distance_max", "max", orientation="horizontal", valueType=float)
        set_source_distance()

        separator(fit_params_box)

        button(fit_params_box, self, "Fit", callback=self.__do_fit, width=240, height=45)

        # contrast vs z
        self.__figure = Figure(figsize=(figure_width, figure_height))
        self.__figure_canvas = FigureCanvas(self.__figure)

        self.__do_fit()
        
        self.append_mpl_figure_to_save(figure=self.__figure)

        output_data.set_parameter("coherence_length", self.__coherence_length)
        output_data.set_parameter("source_size", self.__source_size)

        layout.addWidget(fit_params_container, 0, 0)
        layout.addWidget(self.__figure_canvas, 0, 1)

        self.setFixedWidth(fit_params_container.width() + figure_width/pixels_to_inches)
        self.setFixedHeight(figure_height/pixels_to_inches)

    def __do_fit(self):
        cursor = np.where(np.logical_and(self.__zvec >= self.zvec_min*1e-3, self.__zvec <= self.zvec_max*1e-3))
        zvec            = self.__zvec[cursor]
        contrast        = self.__contrast[cursor]
        source_distance = self.source_distance
        shift_limit     = 0.05 * (zvec[-1] - zvec[0])

        p0 = [1.0, self.z_period, .96, 0.05, self.source_distance, 1e-6]

        if self.z_period_fixed == 1:
            z_period_low = self.z_period * (1-epsilon)
            z_period_up = self.z_period * (1+epsilon)
        else:
            z_period_low = self.z_period_min
            z_period_up = self.z_period_max

        if self.source_distance_fixed == 1:
            source_distance_low = source_distance * ((1-epsilon) if source_distance > 0 else (1+epsilon))
            source_distance_up = source_distance * ((1+epsilon) if source_distance > 0 else (1-epsilon))
        else:
            source_distance_low = self.source_distance_min
            source_distance_up = self.source_distance_max

        bounds_low = [1e-3, z_period_low, .01, -.1, source_distance_low, -shift_limit]
        bounds_up  = [2.0,  z_period_up,  10.,  .1, source_distance_up,   shift_limit]

        def _func_4_fit(z, Amp, z_period, sigma, phase, sourceDist, z0):
            return Amp * np.abs(np.sin((z - z0) / z_period * np.pi / (1 + (z - z0) / sourceDist) +
                                       phase * 2 * np.pi)) * \
                   np.exp(-(z - z0) ** 2 / 2 / sigma ** 2 / (1 + (z - z0) / sourceDist) ** 2)

        popt, pcov = curve_fit(_func_4_fit, zvec, contrast, p0=p0, bounds=(bounds_low, bounds_up))

        self.__coherence_length = np.abs(popt[2]) * self.__wavelength / (np.sqrt(self.__wavelength * popt[1]))
        self.__source_size = self.__wavelength * np.abs(source_distance) / (2 * np.pi * self.__coherence_length)

        fitted_curve = _func_4_fit(zvec, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
        envelope = _func_4_fit(zvec, popt[0], 1e10, popt[2], 1 / 4, popt[4], popt[5])

        self.z_period        = np.round(popt[1], 6)
        self.source_distance = np.round(popt[4], 3)
        self.__le_z_period.setText(str(self.z_period))
        self.__le_source_distance.setText(str(self.source_distance))

        results_Text =  'z_period [m] : ' + str('{:.6g}'.format(popt[1]) + '\n')
        results_Text += 'z shift [mm] : ' + str('{:.3g}'.format(popt[5]*1e3) + '\n')
        results_Text += 'Coherent length: {:.6g} um\n'.format(self.__coherence_length*1e6)
        results_Text += 'Source size: {:.6g} um\n'.format(self.__source_size*1e6)

        self.__figure.clear()
        self.__figure.gca().plot(self.__zvec * 1e3, self.__contrast * 100, self.__ls1, label='Data')
        self.__figure.gca().plot(zvec * 1e3, fitted_curve * 100, self.__lc2, label='Fit')
        self.__figure.gca().plot(zvec * 1e3, envelope * 100, 'b', label='Envelope')
        self.__figure.gca().set_xlabel(r'Distance $z$  [mm]', fontsize=14)
        self.__figure.gca().set_ylabel(r'Visibility $\times$ 100 [%]', fontsize=14)
        self.__figure.gca().set_title('Visibility vs detector distance, ' + self.__direction, fontsize=14, weight='bold')
        self.__figure.gca().legend(fontsize=14, loc=7)
        self.__figure.gca().text(np.max(self.__zvec)*0.7*1e3, max(np.max(self.__contrast), np.max(fitted_curve))*0.85*100, results_Text,
                                 bbox=dict(facecolor=self.__lc2, alpha=0.85))

        self.__figure_canvas.draw()
