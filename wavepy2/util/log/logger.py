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
from wavepy2.util import Singleton, synchronized_method
import sys, io, numpy
import termcolor

DEFAULT_STREAM=sys.stdout

class LogStream(io.TextIOWrapper):
    def close(self, *args, **kwargs): raise NotImplementedError()
    def flush(self, *args, **kwargs): raise NotImplementedError()
    def write(self, *args, **kwargs): raise NotImplementedError()
    def is_color_active(self): return False

class LoggerFacade:
    def print(self, message): raise NotImplementedError()
    def print_message(self, message): raise NotImplementedError()
    def print_warning(self, message): raise NotImplementedError()
    def print_error(self, message): raise NotImplementedError()
    def print_other(self, message, prefix, color): raise NotImplementedError()

class LoggerMode:
    FULL = 0
    WARNING = 1
    ERROR = 2
    NONE = 3
    
    @classmethod
    def get_logger_mode(cls, logger_mode=FULL):
        if logger_mode==cls.FULL: return "Full" 
        if logger_mode==cls.WARNING: return "Warning" 
        if logger_mode==cls.ERROR: return "Error" 
        if logger_mode==cls.NONE: return "None" 

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
    NONE = None
    ON_GREY = "on_grey"
    ON_RED = "on_red"
    ON_GREEN = "on_green"
    ON_YELLOW = "on_yellow"
    ON_BLUE = "on_blue"
    ON_MAGENTA = "on_magenta"
    ON_CYAN = "on_cyan"
    ON_WHITE = "on_white"

class LoggerAttributes:
    NONE = None
    BOLD = "bold"
    DARK = "dark"
    UNDERLINE = "underline"
    BLINK = "blink"
    REVERSE = "reverse"
    CONCEALED = "concealed"

import platform

class __FullLogger(LoggerFacade):
    def __init__(self, stream=DEFAULT_STREAM):
        self.__stream = stream

        if platform.system() == 'Windows':
            self.__color_active = False
        else:
            if stream == DEFAULT_STREAM:
                self.__color_active = True
            elif isinstance(stream, LogStream):
                self.__color_active = stream.is_color_active()
            else:
                self.__color_active = False

    def print(self, message):
        self.__stream.write(message + "\n")
        self.__stream.flush()

    def __print_color(self, message, color=LoggerColor.GREY, highlights=LoggerHighlights.NONE, attrs=LoggerAttributes.NONE):
        self.__stream.write(termcolor.colored(message + "\n", color, highlights, attrs=attrs) if self.__color_active else (message + "\n"))
        self.__stream.flush()

    def print_other(self, message, prefix="", color=LoggerColor.GREY):
        self.__print_color(str(prefix) + str(message), color=color)

    def print_message(self, message):
        self.__print_color("MESSAGE: " + str(message), color=LoggerColor.BLUE)

    def print_warning(self, message):
        self.__print_color("WARNING: " + str(message), color=LoggerColor.MAGENTA)

    def print_error(self, message):
        self.__print_color("ERROR: " + str(message),
                           color=LoggerColor.RED,
                           highlights=LoggerHighlights.ON_GREEN,
                           attrs=[LoggerAttributes.BOLD, LoggerAttributes.BLINK])

class __NullLogger(LoggerFacade):
    def __init__(self, stream=DEFAULT_STREAM): pass
    def print(self, message): pass
    def print_message(self, message): pass
    def print_warning(self, message): pass
    def print_error(self, message): pass

class __ErrorLogger(__FullLogger):
    def __init__(self, stream=DEFAULT_STREAM): super().__init__(stream)
    def print(self, message): pass
    def print_message(self, message): pass
    def print_warning(self, message): pass

class __WarningLogger(__FullLogger):
    def __init__(self, stream=DEFAULT_STREAM): super().__init__(stream)
    def print(self, message): pass
    def print_message(self, message): pass

class __LoggerPool(LoggerFacade):
    def __init__(self, logger_list):
        if logger_list is None: raise ValueError("Logger list is None")
        for logger in logger_list:
            if not isinstance(logger, LoggerFacade): raise ValueError("Wrong objects in Logger list")

        self.__logger_list = numpy.array(logger_list)

    def print(self, message):
        for logger in self.__logger_list:
            logger.print(message)

    def print_message(self, message):
        for logger in self.__logger_list:
            logger.print_message(message)

    def print_warning(self, message):
        for logger in self.__logger_list:
            logger.print_warning(message)

    def print_error(self, message):
        for logger in self.__logger_list:
            logger.print_error(message)


class __AbstractLoggerRegistry:
    def register_logger(self, logger_facade_instance = None): raise NotImplementedError()
    def reset(self): NotImplementedError()
    def get_logger_instance(self): NotImplementedError()
        
@Singleton
class __LoggerRegistry(__AbstractLoggerRegistry):

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

SECONDARY_LOGGER = "Secondary_Logger"

@Singleton
class __SecondaryLoggerRegistry(__AbstractLoggerRegistry):
    def __init__(self):
        self.__logger_instances = {}

    @synchronized_method
    def register_logger(self, logger_facade_instance = None, logger_name=SECONDARY_LOGGER):
        if logger_facade_instance is None: raise ValueError("Logger Instance is None")
        if not isinstance(logger_facade_instance, LoggerFacade): raise ValueError("Logger Instance do not implement Logger Facade")

        if self.__logger_instances is None: self.__logger_instances = {logger_name : logger_facade_instance}
        else: self.__logger_instances[logger_name] = logger_facade_instance

    @synchronized_method
    def reset(self):
        self.__logger_instances = {}

    def get_logger_instance(self, logger_name=SECONDARY_LOGGER):
        return self.__logger_instances[logger_name]



# -----------------------------------------------------
# Factory Methods

def register_logger_pool_instance(stream_list=[], logger_mode=LoggerMode.FULL, reset=False):
    if reset: __LoggerRegistry.Instance().reset()
    if logger_mode==LoggerMode.FULL:      logger_list = [__FullLogger(stream) for stream in stream_list]
    elif logger_mode==LoggerMode.NONE:    logger_list = [__NullLogger(stream) for stream in stream_list]
    elif logger_mode==LoggerMode.WARNING: logger_list = [__WarningLogger(stream) for stream in stream_list]
    elif logger_mode==LoggerMode.ERROR:   logger_list = [__ErrorLogger(stream) for stream in stream_list]

    __LoggerRegistry.Instance().register_logger(__LoggerPool(logger_list=logger_list))

def register_logger_single_instance(stream=DEFAULT_STREAM, logger_mode=LoggerMode.FULL, reset=False):
    if reset: __LoggerRegistry.Instance().reset()
    if logger_mode==LoggerMode.FULL:      __LoggerRegistry.Instance().register_logger(__FullLogger(stream))
    elif logger_mode==LoggerMode.NONE:    __LoggerRegistry.Instance().register_logger(__NullLogger(stream))
    elif logger_mode==LoggerMode.WARNING: __LoggerRegistry.Instance().register_logger(__WarningLogger(stream))
    elif logger_mode==LoggerMode.ERROR:   __LoggerRegistry.Instance().register_logger(__ErrorLogger(stream))

def get_registered_logger_instance():
    return __LoggerRegistry.Instance().get_logger_instance()

def register_secondary_logger(stream=DEFAULT_STREAM, logger_mode=LoggerMode.FULL, logger_name=SECONDARY_LOGGER):
    if logger_mode==LoggerMode.FULL:      __SecondaryLoggerRegistry.Instance().register_logger(__FullLogger(stream), logger_name)
    elif logger_mode==LoggerMode.NONE:    __SecondaryLoggerRegistry.Instance().register_logger(__NullLogger(stream), logger_name)
    elif logger_mode==LoggerMode.WARNING: __SecondaryLoggerRegistry.Instance().register_logger(__WarningLogger(stream), logger_name)
    elif logger_mode==LoggerMode.ERROR:   __SecondaryLoggerRegistry.Instance().register_logger(__ErrorLogger(stream), logger_name)
    
def get_registered_secondary_logger(logger_name=SECONDARY_LOGGER):
    return __SecondaryLoggerRegistry.Instance().get_logger_instance(logger_name)
    
