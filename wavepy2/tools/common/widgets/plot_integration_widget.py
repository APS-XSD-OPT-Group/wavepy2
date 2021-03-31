import numpy as np
import pickle

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
try:
    from mpl_toolkits.mplot3d import Axes3D  # necessario per caricare i plot 3D
except:
    pass

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt


from wavepy2.util.common import common_tools
from wavepy2.util.plot import plot_tools
from wavepy2.util.plot.plotter import WavePyWidget, pixels_to_inches
from wavepy2.tools.common.widgets.plot_profile_widget import PlotProfileWidget

from warnings import filterwarnings
filterwarnings("ignore")

class PlotIntegration(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return self.__title

    def build_widget(self, **kwargs):
        try: self.__title = kwargs["title"]
        except: self.__title = "Frankot-Chellappa Integration Result"

        data              = kwargs["data"]
        pixelsize         = kwargs["pixelsize"]
        titleStr          = kwargs["titleStr"]
        ctitle            = kwargs["ctitle"]
        max3d_grid_points = kwargs["max3d_grid_points"]
        kwarg4surf        = kwargs["kwarg4surf"]

        try:    figure_width = kwargs["figure_width"]*pixels_to_inches
        except: figure_width = 9
        try:    figure_height = kwargs["figure_height"]*pixels_to_inches
        except: figure_height = 7

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

        xxGrid, yyGrid = common_tools.grid_coord(data, pixelsize)

        factor_x, unit_x = common_tools.choose_unit(xxGrid)
        factor_y, unit_y = common_tools.choose_unit(yyGrid)

        # Plot Integration 2

        fig = Figure(figsize=(figure_width, figure_height))
        ax = fig.add_subplot(111, projection='3d')

        rstride = data.shape[0] // max3d_grid_points + 1
        cstride = data.shape[1] // max3d_grid_points + 1

        surf = ax.plot_surface(xxGrid * factor_x, yyGrid * factor_y, data[::-1, :],
                               rstride=rstride, cstride=cstride, cmap='viridis', linewidth=0.1, **kwarg4surf)

        ax_lim = np.max([np.abs(xxGrid * factor_x), np.abs(yyGrid * factor_y)])
        ax.set_xlim3d(-ax_lim, ax_lim)
        ax.set_ylim3d(-ax_lim, ax_lim)
        if 'vmin' in kwarg4surf: ax.set_zlim3d(bottom=kwarg4surf['vmin'])
        if 'vmax' in kwarg4surf: ax.set_zlim3d(top=kwarg4surf['vmax'])
        ax.set_xlabel(r'$x [' + unit_x + ' m]$', fontsize=24)
        ax.set_ylabel(r'$y [' + unit_y + ' m]$', fontsize=24)
        ax.set_title(titleStr, fontsize=24, weight='bold')
        cbar = fig.colorbar(surf, shrink=.8, aspect=20)
        cbar.ax.set_title(ctitle, y=1.01)
        fig.tight_layout(rect=[0, 0, 1, 1])
        ax.text2D(0.05, 0.9, 'strides = {}, {}'.format(rstride, cstride), transform=ax.transAxes)

        figure1 = pickle.loads(pickle.dumps(fig))
        ax.view_init(elev=30, azim=60)
        figure2 = pickle.loads(pickle.dumps(fig))
        ax.view_init(elev=30, azim=-120)
        figure3 = pickle.loads(pickle.dumps(fig))

        figure1.set_figwidth(figure_width)
        figure1.set_figheight(figure_height)

        figure_1_widget = FigureCanvas(figure1)

        self.append_mpl_figure_to_save(figure2)
        self.append_mpl_figure_to_save(figure3)

        plot_profile_widget = PlotProfileWidget(self,
                                                xmatrix=xxGrid * factor_x,
                                                ymatrix=yyGrid * factor_y,
                                                zmatrix=data[::-1, :],
                                                xlabel=r'$x [' + unit_x + ' m]$',
                                                ylabel=r'$y [' + unit_y + ' m]$',
                                                title=titleStr,
                                                xunit='\mu m',
                                                yunit='\mu m',
                                                arg4main={'cmap': 'viridis', 'lw': 3},
                                                figure_width=figure_width,
                                                figure_height=figure_height)

        figure4 = Figure(figsize=(figure_width, figure_height))
        im = figure4.gca().imshow(data[::-1, :], cmap='viridis', extent=common_tools.extent_func(data, pixelsize) * factor_x, **kwarg4surf)
        figure4.gca().set_xlabel(r'$x [' + unit_x + ' m]$', fontsize=24)
        figure4.gca().set_ylabel(r'$y [' + unit_x + ' m]$', fontsize=24)
        figure4.gca().set_title(titleStr, fontsize=18, weight='bold')
        cbar = figure4.colorbar(im)
        cbar.ax.set_title(ctitle, y=1.01)

        self.append_mpl_figure_to_save(figure4)

        figure_4_widget = FigureCanvas(figure4)

        tabs = plot_tools.tabWidget(self)

        plot_tools.createTabPage(tabs, "Integration (3D)", figure_1_widget)
        plot_tools.createTabPage(tabs, "Profile (Animation)", plot_profile_widget)
        plot_tools.createTabPage(tabs, "Profile (Saved)", figure_4_widget)

        self.setFixedWidth(max(plot_profile_widget.get_figure_canvas().get_width_height()[0],
                               figure_1_widget.get_width_height()[0],
                               figure_4_widget.get_width_height()[0])*1.1)
        self.setFixedHeight(max(plot_profile_widget.get_figure_canvas().get_width_height()[1],
                               figure_1_widget.get_width_height()[1],
                               figure_4_widget.get_width_height()[1])*1.1)
