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

import os
from configparser import ConfigParser

from wavepy2.util.log.logger import get_registered_logger_instance


class IniMode:
    LOCAL_FILE = 0
    REMOTE_FILE = 1
    DATABASE = 2
    NONE = 99

class IniFacade:
    def load_ini(self): raise NotImplementedError()
    def get_from_ini(self, section, key): raise NotImplementedError()
    def set_at_ini(self, section, key, value): raise NotImplementedError()
    def push(self): raise NotImplementedError()

class __NullIni(IniFacade):
    def load_ini(self): return None
    def get_from_ini(self, section, key): return None
    def set_at_ini(self, section, key, value): pass
    def push(self): pass

class __LocalIniFile(IniFacade):
    def __init__(self, **kwargs):
        self.__ini_file_name = kwargs["ini_file_name"]

        if not os.path.isfile(self.__ini_file_name):
            with open(self.__ini_file_name, "w") as ini_file: ini_file.write('[Files]\n\n\n[Parameters]\n')
            get_registered_logger_instance().print_warning("File " + self.__ini_file_name + " doesn't exist: created empty ini file.")

        self.__config_parser = ConfigParser()
        self.__config_parser.read(self.__ini_file_name)

    def load_ini(self):
        return None

    def get_from_ini(self, section, key):
        return self.__config_parser[section][key]

    def set_at_ini(self, section, key, value):
        self.__config_parser[section][key] = str(value)

    def get_string_from_ini(self, section ,key):
        value = self.get_from_ini(section, key)
        return None if value is None else value.strip()

    def get_int_from_ini(self, section ,key):
        value = self.get_from_ini(section, key)
        return None if value is None else int(value.strip())

    def get_float_from_ini(self, section ,key):
        value = self.get_from_ini(section, key)
        return None if value is None else float(value.strip())

    def get_list_from_ini(self, section,key):
        value = self.get_from_ini(section, key)
        return None if value is None else list(map(int, self.get_from_ini(section, key).split(',')))

    def set_list_at_ini(self, section, key, values_list=[]):
        if not values_list is None:
            values_string = ""
            for value in values_list: values_string += str(value) + ", "
            values_string = values_string[:, -2]
            self.set_at_ini(section, key, values_string)

    def push(self):
        with open(self.__ini_file_name, "w") as ini_file: self.__config_parser.write(ini_file)


@Singleton
class __IniRegistry:
    def __init__(self):
        self.__ini_instance = None

    @synchronized_method
    def register_ini(self, ini_facade_instance = None):
        if ini_facade_instance is None: raise ValueError("Ini Instance is None")
        if not isinstance(ini_facade_instance, IniFacade): raise ValueError("Ini Instance do not implement Ini Facade")

        if self.__ini_instance is None: self.__ini_instance = ini_facade_instance
        else: raise ValueError("Ini Instance already initialized")

    @synchronized_method
    def reset(self):
        self.__ini_instance = None

    def get_ini_instance(self):
        return self.__ini_instance

# -----------------------------------------------------
# Factory Methods

def register_ini_instance(ini_mode=IniMode.LOCAL_FILE, reset=False, **kwargs):
    if reset: __IniRegistry.Instance().reset()
    if ini_mode == IniMode.LOCAL_FILE:      __IniRegistry.Instance().register_ini(__LocalIniFile(**kwargs))
    elif ini_mode == IniMode.NONE:    __IniRegistry.Instance().register_ini(__NullIni())

def get_registered_ini_instance():
    return __IniRegistry.Instance().get_ini_instance()


