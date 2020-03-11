from wavepy2.utility import Singleton, synchronized_method
import sys, io, numpy
import termcolor

DEFAULT_STREAM=sys.stdout

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

class __NullLogger(LoggerFacade):
    def print(self, message): pass
    def print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_grey(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_red(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_green(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_yellow(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_blue(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_magenta(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_cyan(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass
    def print_white(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''): pass

class __Logger(LoggerFacade):
    def __init__(self, stream=DEFAULT_STREAM):
        self.__stream = stream

        if stream == DEFAULT_STREAM:
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
class __LoggerSingleton(__Logger):
    def __init__(self, stream=DEFAULT_STREAM):
        super().__init__(stream)

class __LoggerList:
    def __init__(self, logger_list):
        if logger_list is None: raise ValueError("Logger list is None")
        for logger in logger_list:
            if not isinstance(logger, LoggerFacade): raise ValueError("Wrong objects in Logger list")

        self.__logger_list = numpy.array(logger_list)

    def get_logger_items(self):
        return self.__logger_list

@Singleton
class __LoggerPool(LoggerFacade):
    def __init__(self, logger_list):
        self.__logger_list = logger_list

    def print(self, message):
        for logger in self.__logger_list.get_logger_items():
            logger.print(message)

    def print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_color(message, color, highlights, attrs)

    def print_grey(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_grey(message, highlights, attrs)

    def print_red(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_red(message, highlights, attrs)

    def print_green(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_green(message, highlights, attrs)

    def print_yellow(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_yellow(message, highlights, attrs)

    def print_blue(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_blue(message, highlights, attrs)

    def print_magenta(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_magenta(message, highlights, attrs)

    def print_cyan(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_cyan(message, highlights, attrs)

    def print_white(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        for logger in self.__logger_list.get_logger_items():
            logger.print_white(message, highlights, attrs)

@Singleton
class __LoggerRegistry:

    def __init__(self):
        self.__logger_instance = None

    @synchronized_method
    def register_logger(self, logger_facade_instance = None):
        if logger_facade_instance is None: raise ValueError("Logger Instance is None")
        if not isinstance(logger_facade_instance, LoggerFacade): raise ValueError("Logger Instance do not implement Logger Facade")

        if self.__logger_instance is None: self.__logger_instance = logger_facade_instance
        else: raise ValueError("Logger Instance already initialized")

    @synchronized_method
    def reset(self):
        self.__logger_instance = None

    def get_logger_instance(self):
        return self.__logger_instance

# -----------------------------------------------------
# Factory Methods



def register_logger_pool_instance(stream_list=[], reset=False):
    if reset: __LoggerRegistry.Instance().reset()
    __LoggerRegistry.Instance().register_logger(__LoggerPool.Instance(logger_list=__LoggerList([__Logger(stream) for stream in stream_list])))

def register_logger_singleton_instance(stream=DEFAULT_STREAM, reset=False):
    if reset: __LoggerRegistry.Instance().reset()
    __LoggerRegistry.Instance().register_logger(__LoggerSingleton.Instance(stream))

def register_null_logger_instance(reset=False):
    if reset: __LoggerRegistry.Instance().reset()
    __LoggerRegistry.Instance().register_logger(__NullLogger())

def get_registered_logger_instance():
    return __LoggerRegistry.Instance().get_logger_instance()

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

    test_widget = TestWidget()
    test_widget.show()

    register_logger_pool_instance([test_widget, open("../../__TEST/diobescul.txt", "wt"), DEFAULT_STREAM])

    logger = get_registered_logger_instance()

    logger.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])
    logger.print_red('Hello, World!', attrs=[LoggerAttributes.BOLD])
    logger.print_blue('Hello, World!')

    register_null_logger_instance(reset=True)

    logger = get_registered_logger_instance()

    logger.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])
    logger.print_red('Hello, World!', attrs=[LoggerAttributes.BOLD])
    logger.print_blue('Hello, World!')

    a.exec_()
