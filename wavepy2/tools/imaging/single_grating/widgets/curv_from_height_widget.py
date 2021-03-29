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

class CurvFromHeight(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        super(CurvFromHeight, self).__init__(parent=parent, application_name=application_name)

        self.__plotter = get_registered_plotter_instance(application_name=application_name)

    def get_plot_tab_name(self): return "Curvature From Height " + self.__title

    def build_widget(self, **kwargs):
        height            = kwargs["height"]
        virtual_pixelsize = kwargs["virtual_pixelsize"]
        grazing_angle     = kwargs["grazing_angle"]
        projectionFromDiv = kwargs["projectionFromDiv"]
        labels            = kwargs["labels"]
        xlabel            = kwargs["xlabel"]
        ylabel            = kwargs["ylabel"]
        titleStr          = kwargs["titleStr"]
        saveFileSuf       = kwargs["saveFileSuf"]
        direction         = kwargs["direction"]

        output_data       = kwargs["output_data"]

        self.__title = direction

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        figure1 = Figure(figsize=(12, 12*9/16))

        ls_cycle, lc_cycle = plot_tools.line_style_cycle(['-'], ['o', 's', 'd', '^'], ncurves=height.shape[1] - 1, cmap_str='gist_rainbow_r')

        if grazing_angle // .00001 > 0: projection = 1 / np.sin(grazing_angle) * projectionFromDiv
        else: projection = projectionFromDiv

        projected_pixel = virtual_pixelsize * projection
        xvec = common_tools.realcoordvec(height.shape[0] - 2, projected_pixel)

        list_curv = [xvec]
        header = [xlabel + ' [m]']

        for j_line in range(1, height.shape[1]):
            curv = np.diff(np.diff(height[:, j_line])) / projected_pixel ** 2

            if j_line == 1: factor_x, unit_x = common_tools.choose_unit(xvec)

            list_curv.append(curv)
            header.append(labels[j_line - 1])

            figure1.gca().plot(xvec * factor_x, curv, next(ls_cycle), c=next(lc_cycle), label=labels[j_line - 1])

        marginx = 0.1 * np.ptp(xvec * factor_x)
        figure1.gca().set_xlim([np.min(xvec * factor_x) - marginx, np.max(xvec * factor_x) + marginx])
        figure1.gca().set_xlabel(xlabel + r' [$' + unit_x + ' m$]')
        figure1.gca().set_ylabel(ylabel + r'[$m^{-1}$]')
        figure1.legend(loc=7, fontsize=12)

        if grazing_angle // .00001 > 0:
            figure1.gca().set_title(titleStr + 'Mirror Curvature,\n' +
                                    'grazing angle {:.2f} mrad,\n'.format(grazing_angle * 1e3) +
                                    'projection due divergence = ' +
                                    r'$ \times $ {:.2f}'.format(projectionFromDiv))
        else:
            figure1.gca().set_title(titleStr + 'Curvature')

        figure1.tight_layout()

        self.append_mpl_figure_to_save(figure=figure1, figure_file_name=common_tools.get_unique_filename(saveFileSuf, "png"))

        data2saveV = np.asarray(list_curv).T

        header.append(ylabel + ' [1/m]')

        if grazing_angle // .00001 > 0: header.append(', grazing_angle = {:.4g}'.format(grazing_angle))
        if projectionFromDiv // 1 != 1: header.append('projection due divergence = {:.2f}x'.format(projectionFromDiv))

        self.__plotter.save_csv_file(data2saveV, file_prefix=saveFileSuf, file_suffix='_curv_' + xlabel, headerList=header)

        output_data.set_parameter("curvature", np.asarray(list_curv).T)

        layout.addWidget(FigureCanvas(figure1))

        self.setFixedWidth(plot_tools.WIDGET_FIXED_WIDTH * 1.4)
        self.setFixedHeight(700)
