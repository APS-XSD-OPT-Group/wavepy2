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

from wavepy2.tools.imaging.single_grating.scripts.main_single_grating_talbot import MainSingleGratingTalbot
from wavepy2.tools.diagnostic.coherence.scripts.main_single_grating_coherence_z_scan import MainSingleGratingCoherenceZScan
from wavepy2.tools.metrology.lenses.scripts.main_fit_residual_lenses import MainFitResidualLenses

if __name__ == "__main__":
    def show_help(error=False):
        print("")
        if error:
            print("*************************************************************")
            print("********              Command not valid!             ********")
            print("*************************************************************\n")
        else:
            print("=============================================================")
            print("           WELCOME TO WavePy 2 - command line mode")
            print("=============================================================\n")
        print("To launch a script:       python -m wavepy2.tools <script id> <options>\n")
        print("To show help of a script: python -m wavepy2.tools <script id> --h\n")
        print("To show this help:        python -m wavepy2.tools --h\n")
        print("* Available scripts:\n" +
              "    1) Imaging   - Single Grating Talbot, id: " + MainSingleGratingTalbot.SCRIPT_ID + "\n" +
              "    2) Coherence - Single Grating Z Scan, id: " + MainSingleGratingCoherenceZScan.SCRIPT_ID + "\n" +
              "    3) Metrology - Fit Residual Lenses,   id: " + MainFitResidualLenses.SCRIPT_ID + "\n")

    if len(sys.argv) == 1 or sys.argv[1] == "--h":
        show_help()
    else:
        if sys.argv[1]   == MainSingleGratingTalbot.SCRIPT_ID:         MainSingleGratingTalbot(sys_argv=sys.argv).run_script()
        elif sys.argv[1] == MainSingleGratingCoherenceZScan.SCRIPT_ID: MainSingleGratingCoherenceZScan(sys_argv=sys.argv).run_script()
        elif sys.argv[1] == MainFitResidualLenses.SCRIPT_ID:           MainFitResidualLenses(sys_argv=sys.argv).run_script()
        else: show_help(error=True)
