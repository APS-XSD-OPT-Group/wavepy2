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
from wavepy2.util.ini.initializer import get_registered_ini_instance, register_ini_instance, IniMode
from wavepy2.util.log.logger import register_logger_single_instance, LoggerMode
from wavepy2.util.plot.qt_application import get_registered_qt_application_instance, register_qt_application_instance, QtApplicationMode
from wavepy2.util.plot.plotter import get_registered_plotter_instance, register_plotter_instance, PlotterMode

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
import sys

class WavePyScript():
    SCRIPT_LOGGER_MODE = LoggerMode.FULL
    INI_MODE      = IniMode.LOCAL_FILE
    INI_FILE_NAME = ".single_grating_talbot.ini"

    def __init__(self, sys_argv, **kwargs):
        self.__args = self._parse_sys_arguments(sys_argv)
        self.__args = {**self.__args, **self._parse_additional_parameters(**kwargs)}

    def run_script(self):
        self.__initialize_utils(**self.__args)
        self._run_script(**self.__args)

    def show_help(self):
        print("\nTo run this script:  python -m wavepy2.tools " + self.get_script_id() + " <options>\n")
        print("Options:")
        print("  -l<logger mode>\n")
        print("   logger modes:\n" +
              "     0 Full (Message, Warning, Error) - Default value\n" +
              "     1 Warning (Warning, Error)\n" +
              "     2 Error\n" +
              "     3 None\n")
        print("  -p<plotter mode>\n")
        print("   plotter modes:\n" +
              "     0 Full (Display, Save Images) - Default value\n" +
              "     1 Display Only\n" +
              "     2 Save Images Only\n" +
              "     3 None\n")
        sys.exit(0)

    def get_script_id(self): raise NotImplementedError
    def get_ini_file_name(self): raise NotImplementedError

    ######################################################################
    # PROTECTED

    def _parse_additional_parameters(self, **kwargs): return {}

    def _run_script(self, **args): raise NotImplementedError()

    def _parse_sys_arguments(self, sys_argv):
        args = {}
        if len(sys_argv) > 2:
            if sys_argv[2] == "--h":
                self.show_help()
            else:
                for i in range(2, len(sys_argv)):
                    if   "-l" == sys_argv[i][:-1]: args["LOGGER_MODE"] = int(sys_argv[i][-1])
                    elif "-p" == sys_argv[i][:-1]: args["PLOTTER_MODE"] = int(sys_argv[i][-1])
                    elif "-i" == sys_argv[i][:-1]: args["INI_MODE"] = int(sys_argv[i][-1])
                    else: self.__parse_additional_sys_argument(sys_argv[i], args)

        return args

    ######################################################################
    # PRIVATE

    def __parse_additional_sys_argument(self, sys_argument, args): pass

    def __initialize_utils(self, LOGGER_MODE=LoggerMode.FULL, PLOTTER_MODE=PlotterMode.FULL, INI_MODE=IniMode.LOCAL_FILE):
        print("Logger Mode : " + LoggerMode.get_logger_mode(LOGGER_MODE))
        print("Plotter Mode: " + PlotterMode.get_plotter_mode(PLOTTER_MODE))

        # ==========================================================================
        # %% Script initialization
        # ==========================================================================

        register_logger_single_instance(logger_mode=LOGGER_MODE)
        register_ini_instance(INI_MODE, ini_file_name=self.get_ini_file_name() if INI_MODE == IniMode.LOCAL_FILE else None)
        register_plotter_instance(plotter_mode=PLOTTER_MODE)
        register_qt_application_instance(QtApplicationMode.SHOW if PLOTTER_MODE in [PlotterMode.FULL, PlotterMode.DISPLAY_ONLY] else QtApplicationMode.HIDE)



