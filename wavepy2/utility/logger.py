from wavepy2.utility import Singleton, synchronized_method
import sys, io, numpy
import termcolor

class LogStream(io.TextIOWrapper):

    def close(self, *args, **kwargs):  # real signature unknown
        raise NotImplementedError()

    def flush(self, *args, **kwargs):  # real signature unknown
        raise NotImplementedError()

    def write(self, *args, **kwargs):  # real signature unknown
        raise NotImplementedError()

    def is_color_active(self):
        return False

class LoggerColor:
    GREY = "grey"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"

class LoggerHighlights:
    ON_GREY = "on_grey"
    ON_RED = "on_red"
    ON_GREEN = "on_green"
    ON_YELLOW = "on_yellow"
    ON_BLUE = "on_blue"
    ON_MAGENTA = "on_magenta"
    ON_CYAN = "on_cyan"
    ON_WHITE = "on_white"

class LoggerAttributes:
    BOLD = "bold"
    DARK = "dark"
    UNDERLINE = "underline"
    BLINK = "blink"
    REVERSE = "reverse"
    CONCEALED = "concealed"

class LoggerFacade:
        def print(self, message): raise NotImplementedError()
        def print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_grey(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_red(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_green(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_yellow(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_blue(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_magenta(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_cyan(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()
        def print_white(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): raise NotImplementedError()

class Logger(LoggerFacade):
    def __init__(self, stream=sys.stdout):
        self.__stream = stream

        if stream == sys.stdout:
            self.__color_active = True
        elif isinstance(stream, LogStream):
            self.__color_active = stream.is_color_active()
        else:
            self.__color_active = False

    def print(self, message):
        self.__stream.write(message + "\n")
        self.__stream.flush()

    def print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        if self.__color_active:
            self.__stream.write(termcolor.colored(message + "\n", color, highlights, attrs=attrs))
            self.__stream.flush()
        else:
            self.print(message)

    def print_grey(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.GREY, highlights=highlights, attrs=attrs)

    def print_red(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.RED, highlights=highlights, attrs=attrs)

    def print_green(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.GREEN, highlights=highlights, attrs=attrs)

    def print_yellow(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.YELLOW, highlights=highlights, attrs=attrs)

    def print_blue(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.BLUE, highlights=highlights, attrs=attrs)

    def print_magenta(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.MAGENTA, highlights=highlights, attrs=attrs)

    def print_cyan(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.CYAN, highlights=highlights, attrs=attrs)

    def print_white(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.WHITE, highlights=highlights, attrs=attrs)

@Singleton
class LoggerSingleton(Logger):
    def __init__(self, stream=sys.stdout):
        super(LoggerSingleton, self).__init__(stream)


@Singleton
class LoggerPool(LoggerFacade):
    def __init__(self):
        self.__logger_list = None

    @synchronized_method
    def add_logger(self, logger):
        if self.__logger_list is None:
            self.__logger_list = numpy.array([logger])
        else:
            self.__logger_list = numpy.append(self.__logger_list, logger)

    def print(self, message):
        for logger in self.__logger_list:
            logger.print(message)

    def print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_color(message, color, highlights, attrs)

    def print_grey(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_grey(message, highlights, attrs)

    def print_red(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_red(message, highlights, attrs)

    def print_green(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_green(message, highlights, attrs)

    def print_yellow(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_yellow(message, highlights, attrs)

    def print_blue(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_blue(message, highlights, attrs)

    def print_magenta(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_magenta(message, highlights, attrs)

    def print_cyan(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_cyan(message, highlights, attrs)

    def print_white(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list:
            logger.print_white(message, highlights, attrs)


def get_logger_pool():
    return LoggerPool.Instance()

def get_logger_singleton(stream=sys.stdout):
    return LoggerSingleton.Instance(stream)

# --------------------------------------------------------------------------------

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QApplication, QTextCursor

import oasys.widgets.gui as gui

class TestWidget(LogStream):

    class Widget(QWidget):

        def __init__(self):
            super(TestWidget.Widget, self).__init__()

            self.setFixedHeight(200)
            self.setFixedWidth(250)

            text_area_box = gui.widgetBox(self, "Test", orientation="vertical", height=160, width=200)

            self.__text_area = gui.textArea(height=120, width=160, readOnly=True)
            self.__text_area.setText("")

            text_area_box.layout().addWidget(self.__text_area)

        def write(self, text):
            cursor = self.__text_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            self.__text_area.setTextCursor(cursor)
            self.__text_area.ensureCursorVisible()


    def __init__(self):
        self.__widget = TestWidget.Widget()

    def close(self):
        pass

    def write(self, text):
        self.__widget.write(text)

    def flush(self, *args, **kwargs):
        pass

    def show(self):
        self.__widget.show()


if __name__=="__main__":
    a = QApplication(sys.argv)

    logger_pool = get_logger_pool()

    test_widget = TestWidget()

    logger_pool.add_logger(Logger(stream=test_widget))
    logger_pool.add_logger(Logger(stream=open("diobescul.txt", "wt")))
    logger_pool.add_logger(Logger())

    logger_pool.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])
    logger_pool.print_red('Hello, World!', attrs=[LoggerAttributes.BOLD])
    logger_pool.print_blue('Hello, World!')

    test_widget.show()

    a.exec_()
