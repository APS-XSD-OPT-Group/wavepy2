from wavepy2.util.plot.plotter import *
import sys
from matplotlib.figure import Figure

from PyQt5.Qt import QApplication, QTextCursor

a = QApplication(sys.argv)

register_plotter_instance(PlotterMode.FULL)

class MyWidget(WavePyWidget):

    def get_plot_tab_name(self): "TEST"

    def build_figure(self, **kwargs):
        return Figure(figsize=(2, 2))

plotter = get_registered_plotter_instance()

plotter.push_plot("CONTEXT1", MyWidget)

container=QWidget()

class MyInteractiveWidget(WavePyInteractiveWidget):
    def __init__(self, parent):
        super(MyInteractiveWidget, self).__init__(parent, message="MSG", title="TIT")

    def build_widget(self, **kwargs):
        pass

    def get_user_selection(self):
        return "TEST2"

plotter.draw_context_on_widget("CONTEXT1", container_widget=container)

container.show()

print(plotter.show_interactive_plot(MyInteractiveWidget, container_widget=container))

a.exec_()


