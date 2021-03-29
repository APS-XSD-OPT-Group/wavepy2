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

from wavepy2.tools.diagnostic.coherence.bl.single_grating_coherence_z_scan import create_single_grating_coherence_z_scan_manager, APPLICATION_NAME, \
    SINGLE_THREAD, MULTI_THREAD
from wavepy2.tools.diagnostic.coherence.bl.single_grating_coherence_z_scan import \
    CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY, RUN_CALCULATION_CONTEXT_KEY, SORT_CALCULATION_RESULT_CONTEXT_KEY, FIT_CALCULATION_RESULT_CONTEXT_KEY

from wavepy2.util.ini.initializer import get_registered_ini_instance
from wavepy2.util.log.logger import LoggerMode
from wavepy2.util.plot.qt_application import get_registered_qt_application_instance
from wavepy2.util.plot.plotter import get_registered_plotter_instance

from wavepy2.tools.common.wavepy_script import WavePyScript

from multiprocessing import cpu_count

class MainSingleGratingCoherenceZScan(WavePyScript):
    SCRIPT_ID = "coh-sgz"

    def _get_script_id(self): return MainSingleGratingCoherenceZScan.SCRIPT_ID
    def _get_application_name(self): return APPLICATION_NAME
    def _get_ini_file_name(self): return ".single_grating_coherence_z_scan.ini"

    def _parse_additional_sys_argument(self, sys_argument, args):
        if   "-f" == sys_argument[:2]: args["SHOW_FOURIER"] = int(sys_argument[2:]) > 0
        elif "-t" == sys_argument[:2]: args["THREADING"]    = int(sys_argument[2:])
        elif "-n" == sys_argument[:2]: args["N_CPUS"]       = int(sys_argument[2:])

    def _help_additional_parameters(self):
        available_cpus = cpu_count()
        return "  -f<show fourier images>\n\n" + \
               "   show fourier images:\n" + \
               "     0 False - Default value\n" +\
               "     1 True\n\n" + \
               "  -t<threading mode>\n\n" + \
               "   threading modes:\n" + \
               "     0 Single-Thread\n" + \
               "     1 Multi-Thread - Default Value\n\n" + \
              ("   ** Warning: Multi-Thread not possible: not enough CPUs in this computer\n" if cpu_count() - 2 < 2 else \
               "  -n<nr. of cpus> (Multi-Thread only)\n\n" + \
               "   nr. of cpus:\n" + \
               "     - an positive integer number <= " + str(available_cpus-1) + ", or \n" + \
               "     - skip the option for default: "  + str(available_cpus-2) + "\n")

    def __parse_args(self, **args):
        try: SHOW_FOURIER = args["SHOW_FOURIER"]
        except: SHOW_FOURIER = False

        try: THREADING = args["THREADING"]
        except: THREADING = MULTI_THREAD

        if THREADING == MULTI_THREAD:
            try: N_CPUS    = args["N_CPUS"]
            except: N_CPUS = None
        else: N_CPUS = None

        print("Show Fourier Images: " + str(SHOW_FOURIER))
        print("Threading Mode: " + ("Multi-Thread" if THREADING == MULTI_THREAD else "Single-Thread"))
        print("Nr. of CPUs: " + (str(N_CPUS) if not N_CPUS is None else "Automatic"))

        return SHOW_FOURIER, THREADING, N_CPUS

    def _run_script(self, SCRIPT_LOGGER_MODE=LoggerMode.FULL, **args):
        SHOW_FOURIER, THREADING, N_CPUS = self.__parse_args(**args)

        plotter = get_registered_plotter_instance(application_name=self._get_application_name())

        try:
            single_grating_coherence_z_scan_manager = create_single_grating_coherence_z_scan_manager(THREADING, N_CPUS)

            # ==========================================================================
            # %% Initialization parameters
            # ==========================================================================

            initialization_parameters = single_grating_coherence_z_scan_manager.manager_initialization(single_grating_coherence_z_scan_manager.get_initialization_parameters(),
                                                                                                       SCRIPT_LOGGER_MODE,
                                                                                                       SHOW_FOURIER)

            # ==========================================================================
            # %% CROP Initial Image
            # ==========================================================================

            initial_crop_result = single_grating_coherence_z_scan_manager.crop_dark_image(single_grating_coherence_z_scan_manager.crop_initial_image(initialization_parameters))

            # ==========================================================================

            harm_periods_result = single_grating_coherence_z_scan_manager.calculate_harmonic_periods(initial_crop_result, initialization_parameters)
            plotter.show_context_window(CALCULATE_HARMONIC_PERIODS_CONTEXT_KEY)

            # ==========================================================================

            run_calculation_result = single_grating_coherence_z_scan_manager.run_calculation(harm_periods_result, initialization_parameters)
            plotter.show_context_window(RUN_CALCULATION_CONTEXT_KEY)

            # ==========================================================================

            sort_calculation_result = single_grating_coherence_z_scan_manager.sort_calculation_result(run_calculation_result, initialization_parameters)
            plotter.show_context_window(SORT_CALCULATION_RESULT_CONTEXT_KEY)

            # ==========================================================================

            fit_calculation_result = single_grating_coherence_z_scan_manager.fit_calculation_result(sort_calculation_result, initialization_parameters)
            plotter.show_context_window(FIT_CALCULATION_RESULT_CONTEXT_KEY)

            # ==========================================================================
            # %% Final Operations
            # ==========================================================================

            get_registered_ini_instance(self._get_application_name()).push()
            get_registered_qt_application_instance().show_application_closer()

            # ==========================================================================

            get_registered_qt_application_instance().run_qt_application()
        except Exception as e:
            print("\n*** Program terminated with the following exception: " + str(e))


import os, sys
if __name__=="__main__":
    if os.getenv('WAVEPY_DEBUG', "0") == "1": MainSingleGratingCoherenceZScan(sys_argv=sys.argv).run_script()
    else: MainSingleGratingCoherenceZScan().show_help()
