from wavepy2.utility import Singleton
import sys
import io
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
    
@Singleton
class Logger():
    def __init__(self, stream=sys.stdout):
        self.__stream = stream

        if stream == sys.stdout:
            self.__color_active = True
        elif isinstance(stream, LogStream):
            self.__color_active = stream.is_color_active()
        else:
            self.__color_active = False

    """Colorize text.
    Example:
        log = Logger.Instance()
    
        log.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])
        log.print_color('Hello, World!', LoggerColor.GREEN)
    """

    def print(self, message):
        self.__stream.write(message + "\n")
        self.__stream.flush()

    def print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        if self.__color_active:
            self.__stream.write(termcolor.colored(message + "\n", color, highlights, attrs=attrs))
            self.__stream.flush()
        else:
            self.print(message)

    def print_red(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.RED, highlights=highlights, attrs=attrs)

    def print_blue(self, message, highlights=LoggerHighlights.ON_WHITE, attrs=''):
        self.print_color(message, color=LoggerColor.BLUE, highlights=highlights, attrs=attrs)

    def close(self):
        Logger.reset()


from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QApplication

import orangewidget.gui as gui

class TestWidget(LogStream):

    class Widget(QWidget):
        text_value = ""

        def __init__(self):
            super(TestWidget.Widget, self).__init__()

            box = gui.widgetBox(self, "Test", orientation="vertical")
            self.__le = gui.lineEdit(box, self, "text_value", "logged text", valueType=str, orientation="horizontal")

        def write(self, text):
            self.__le.setText(text)


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

    log = Logger.Instance(stream=test_widget)
    log.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])
    log.close()

    log = Logger.Instance(stream=open("diobescul.txt", "wt"))

    log.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])

    log.close()

    log = Logger.Instance()
    log.print_color('Hello, World!', LoggerColor.RED, LoggerHighlights.ON_GREEN, [LoggerAttributes.BOLD, LoggerAttributes.BLINK])
    log.close()

    test_widget.show()

    a.exec_()
