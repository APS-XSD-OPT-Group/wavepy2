import time

import numpy as np
from scipy.optimize import curve_fit

from PyQt5.QtWidgets import QWidget, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from aps.wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches, FigureToSave
from aps.wavepy2.util.common import common_tools
from aps.common.plot.gui import widgetBox, separator, button, checkBox, lineEdit

from warnings import filterwarnings
filterwarnings("ignore")

epsilon = 1e-9

class VisibilityPlot(WavePyWidget):
    zvec_min = 0.0
    zvec_max = 0.0

    pattern_period = 0.0
    pattern_period_min = 0.0
    pattern_period_max = 0.0
    pattern_period_fixed = 1

    source_distance = 0.0
    source_distance_min = 0.0
    source_distance_max = 0.0
    source_distance_fixed = 1

    shift_limit = 0.0
    shift_limit_min = 0.0
    shift_limit_max = 0.0
    shift_limit_fixed = 1

    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Visibility vs detector distance"

    def build_widget(self, **kwargs):
        self.__zvec             = kwargs["zvec"]
        self.zvec_min           = np.round(np.min(self.__zvec)*1e3, 2) # mm
        self.zvec_max           = np.round(np.max(self.__zvec)*1e3, 2)
        self.__wavelength       = kwargs["wavelength"]
        self.pattern_period     = np.round(kwargs["pattern_period"], 6)
        self.source_distance    = np.round(kwargs["source_distance"], 3)

        self.__contrast         = kwargs["contrast"]
        self.__ls1              = kwargs["ls1"]
        self.__lc2              = kwargs["lc2"]
        self.__direction        = kwargs["direction"]


        #self.z_period           = np.round(kwargs["pattern_period"]**2/self.__wavelength, 6)


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
        fit_params_container.setFixedHeight(int(figure_width/pixels_to_inches))

        fit_params_box = widgetBox(fit_params_container, "Fit Parameters", orientation="vertical", width=260)

        lineEdit(fit_params_box, self, "zvec_min", "Z min [mm]", labelWidth=120, orientation="horizontal", valueType=float)
        lineEdit(fit_params_box, self, "zvec_max", "Z max [mm]", labelWidth=120, orientation="horizontal", valueType=float)

        separator(fit_params_box)

        period_box = widgetBox(fit_params_box, "", orientation="horizontal", width=240)
        self.__le_pattern_period = lineEdit(period_box, self, "pattern_period", "Pattern period [m]", labelWidth=100, orientation="horizontal", valueType=float)

        def set_pattern_period():
            self.__le_pattern_period_min.setEnabled(not self.pattern_period_fixed)
            self.__le_pattern_period_max.setEnabled(not self.pattern_period_fixed)

        checkBox(period_box, self, "pattern_period_fixed", "fix", callback=set_pattern_period)
        pattern_period_box_2 = widgetBox(fit_params_box, "", orientation="horizontal", width=240)
        self.__le_pattern_period_min = lineEdit(pattern_period_box_2, self, "pattern_period_min", "min", orientation="horizontal", valueType=float)
        self.__le_pattern_period_max = lineEdit(pattern_period_box_2, self, "pattern_period_max", "max", orientation="horizontal", valueType=float)
        set_pattern_period()

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

        self.__do_fit(True)

        self.append_mpl_figure_to_save(figure=self.__figure,
                                       figure_file_name=common_tools.get_unique_filename(f"visibility_vs_detector_distance_{self.__direction}", "png"))

        output_data.set_parameter("coherence_length", self.__coherence_length)
        output_data.set_parameter("source_size", self.__source_size)

        layout.addWidget(fit_params_container, 0, 0)
        layout.addWidget(self.__figure_canvas, 0, 1)

        self.setFixedWidth(int(fit_params_container.width() + figure_width/pixels_to_inches))
        self.setFixedHeight(int(figure_height/pixels_to_inches))

    def __do_fit(self, is_init=False):
        cursor = np.where(np.logical_and(self.__zvec >= self.zvec_min*1e-3, self.__zvec <= self.zvec_max*1e-3))
        zvec            = self.__zvec[cursor]
        contrast        = self.__contrast[cursor]
        source_distance = self.source_distance
        shift_limit     = 0.05 * (zvec[-1] - zvec[0])

        initial_guess = [1.0, self.pattern_period, 1e-5, self.source_distance, 1e-6]

        if self.pattern_period_fixed == 1:
            pattern_period_low = self.pattern_period * (1-epsilon)
            pattern_period_up  = self.pattern_period * (1+epsilon)
        else:
            if self.pattern_period_min >= self.pattern_period_max:
                QMessageBox.critical(self, "Error", " Pattern period min >= pattern period max")
                return

            pattern_period_low = self.pattern_period_min
            pattern_period_up  = self.pattern_period_max

        if self.source_distance_fixed == 1:
            source_distance_low = source_distance * ((1-epsilon) if source_distance > 0 else (1+epsilon))
            source_distance_up  = source_distance * ((1+epsilon) if source_distance > 0 else (1-epsilon))
        else:
            if self.source_distance_min >= self.source_distance_max:
                QMessageBox.critical(self, "Error", " Source distance min >= Source distance max")
                return

            source_distance_low = self.source_distance_min
            source_distance_up = self.source_distance_max

        bounds_low = [1e-3, pattern_period_low, 1e-7, source_distance_low, -shift_limit]
        bounds_up  = [2.0,  pattern_period_up,  1e-3, source_distance_up,   shift_limit]

        def _csi(source_sigma, source_distance):
            return self.__wavelength * source_distance / (2 * np.pi * source_sigma)

        def _pz(z, p0, source_distance, z0):
            return p0 * (1 + (z - z0) / source_distance)

        def _envelope(z, Amp, p0, source_sigma, source_distance, z0):
            csi = _csi(source_sigma, source_distance)
            pz = _pz(z, p0, source_distance, z0)

            return Amp * np.exp(-((self.__wavelength * (z - z0)) ** 2) / ((csi * pz) ** 2))

        def _fitting_function(z, Amp, p0, source_sigma, source_distance, z0):
            pz = _pz(z, p0, source_distance, z0)

            return _envelope(z, Amp, p0, source_sigma, source_distance, z0) * \
                   np.abs(np.sin(np.pi * self.__wavelength * (z - z0) / (p0 * pz)))

        try:
            popt, pcov = curve_fit(_fitting_function, zvec, contrast, p0=initial_guess, bounds=(bounds_low, bounds_up))
        except Exception as e:
            QMessageBox.critical(self, "Exception Occurred", str(e))
            return

        self.__source_size      = popt[2]
        self.__coherence_length = _csi(source_sigma=popt[2], source_distance=popt[3])

        fitted_curve = _fitting_function(zvec, Amp=popt[0], p0=popt[1], source_sigma=popt[2], source_distance=popt[3], z0=popt[4])
        envelope     = _envelope(        zvec, Amp=popt[0], p0=popt[1], source_sigma=popt[2], source_distance=popt[3], z0=popt[4])

        self.pattern_period  = np.round(popt[1], 6)
        self.source_distance = np.round(popt[4], 3)
        self.__le_pattern_period.setText(str(self.pattern_period))
        self.__le_source_distance.setText(str(self.source_distance))

        results_Text =  'pattern_period [m] : ' + str('{:.6g}'.format(popt[1]) + '\n')
        results_Text += 'z shift [mm] : ' + str('{:.3g}'.format(popt[4]*1e3) + '\n')
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

        # in this case we will save an image at every fit
        if not is_init and self._allows_saving():
            figure_to_save = FigureToSave(figure=self.__figure,
                                          figure_file_name=common_tools.get_unique_filename(f"visibility_vs_detector_distance_{self.__direction}", "png"))
            figure_to_save.save_figure()


