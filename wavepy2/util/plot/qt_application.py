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
from wavepy2.tools.common.widgets.close_app_widget import CloseApp

import sys
from PyQt5.Qt import QApplication
from PyQt5.QtWidgets import QStyleFactory

class QtApplicationMode:
    SHOW = 0
    HIDE = 99

class QtApplicationFacade:
    def show_application_closer(self): raise NotImplementedError()
    def run_qt_application(self): raise NotImplementedError()

class __NullQtApplication(QtApplicationFacade):
    def __init__(self): self.__qt_application = QApplication(sys.argv)
    def run_qt_application(self): self.__qt_application.exec_()
    def show_application_closer(self): sys.exit(0)

class __QtApplication(QtApplicationFacade):
    def __init__(self):
        self.__qt_application = QApplication(sys.argv)
        self.__qt_application.setStyle(QStyleFactory.create('Fusion')) # 'Windows'
        self.__application_closer = CloseApp()

    def show_application_closer(self):
        self.__application_closer.show()

    def run_qt_application(self): 
        self.__qt_application.exec_()

@Singleton
class __QtApplicationRegistry:
    def __init__(self):
        self.__qt_application_instance = None

    @synchronized_method
    def register_qt_application(self, qt_application_facade_instance = None):
        if qt_application_facade_instance is None: raise ValueError("QtApplication Instance is None")
        if not isinstance(qt_application_facade_instance, QtApplicationFacade): raise ValueError("QtApplication Instance do not implement QtApplication Facade")

        if self.__qt_application_instance is None: self.__qt_application_instance = qt_application_facade_instance
        else: raise ValueError("QtApplication Instance already initialized")

    @synchronized_method
    def reset(self):
        self.__qt_application_instance = None

    def get_qt_application_instance(self):
        return self.__qt_application_instance

# -----------------------------------------------------
# Factory Methods

def register_qt_application_instance(qt_application_mode=QtApplicationMode.SHOW, reset=False):
    if reset: __QtApplicationRegistry.Instance().reset()
    if qt_application_mode == QtApplicationMode.SHOW:      __QtApplicationRegistry.Instance().register_qt_application(__QtApplication())
    elif qt_application_mode == QtApplicationMode.HIDE:  __QtApplicationRegistry.Instance().register_qt_application(__NullQtApplication())

def get_registered_qt_application_instance():
    return __QtApplicationRegistry.Instance().get_qt_application_instance()

