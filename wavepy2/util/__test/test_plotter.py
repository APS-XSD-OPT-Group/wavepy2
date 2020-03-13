from wavepy2.util.plot.plotter import *
import sys
from matplotlib.figure import Figure

from PyQt5.Qt import QApplication, QTextCursor

a = QApplication(sys.argv)

register_plotter_instance(PlotterMode.FULL)

class MyWidget(WavePyWidget):

    def get_plot_tab_name(self): "DIOBESCUL"

    def build_figure(self, **kwargs):
        return Figure(figsize=(2, 2))

plotter = get_registered_plotter_instance()

plotter.push_plot("DIOBOIA", MyWidget)

container=QWidget()

plotter.draw_context_on_widget("DIOBOIA", container=container)

#container.show()

a.exec_()


