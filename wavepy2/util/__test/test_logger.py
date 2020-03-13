# #########################################################################
# Copyright (c) 2020, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2020. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################
from wavepy2.util.log.logger import *

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QApplication, QTextCursor

import oasys.widgets.gui as gui

class TestWidget(LogStream):
    class Widget(QWidget):
        def __init__(self):
            super(TestWidget.Widget, self).__init__()

            self.setFixedHeight(200)
            self.setFixedWidth(250)

            text_area_box = gui.__widgetBox(self, "Test", orientation="vertical", height=160, width=200)

            self.__text_area = gui.textArea(height=120, width=160, readOnly=True)
            self.__text_area.setText("")

            text_area_box.layout().addWidget(self.__text_area)

        def write(self, text):
            cursor = self.__text_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            self.__text_area.setTextCursor(cursor)
            self.__text_area.ensureCursorVisible()

    def __init__(self): self.__widget = TestWidget.Widget()
    def close(self): pass
    def write(self, text): self.__widget.write(text)
    def flush(self, *args, **kwargs): pass
    def show(self): self.__widget.show()

def __log():
    logger = get_registered_logger_instance()

    logger.print('Hello, World!')
    logger.print_message('Hello, World!')
    logger.print_warning('Hello, World!')
    logger.print_error('Hello, World!')

def run_test_logger():
    a = QApplication(sys.argv)

    test_widget = TestWidget()
    test_widget.show()

    try:
        register_logger_pool_instance([test_widget, open("__TEST/diobescul.txt", "wt"), DEFAULT_STREAM], LoggerMode.FULL)
        __log()

        register_logger_single_instance(DEFAULT_STREAM, LoggerMode.NONE, reset=True)
        __log()
    except Exception as e:
        print(e)

    a.exec_()

if __name__=="__main__":
    run_test_logger()
