from wavepy2.tools.plot.plotter import *
import sys

from PyQt5.Qt import QApplication, QTextCursor

a = QApplication(sys.argv)

widget = WavePyWidget()
widget.show()

a.exec_()
