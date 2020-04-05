import sys

from wavepy2.tools.imaging.single_grating.scripts.main_single_grating_talbot import run_single_grating_talbot, arguments_single_grating_talbot

if __name__ == "__main__":
    def show_help():
        print("")
        print("=============================================================")
        print("           WELCOME TO WavePy 2 - command line mode")
        print("=============================================================\n")
        print("To launch a script:       python -m wavepy2.tools <script id>\n")
        print("To show help of a script: python -m wavepy2.tools <script id> --h\n")
        print("To show this help:        python -m wavepy2.tools --h\n")
        print("* Available scripts:\n" +
              "    1) Imaging   - Single Grating Talbot, id: img-sgt\n" +
              "    2) Coherence - Single Grating Z Scan, id: coh-sgz\n" +
              "    3) Metrology - Fit Residual Lenses,   id: met-frl\n")

    if len(sys.argv) == 1 or sys.argv[1] == "--h":
        show_help()
    else:
        if sys.argv[1]   == "img-sgt": run_single_grating_talbot(**arguments_single_grating_talbot(sys.argv))
        elif sys.argv[1] == "coh-sgz": print("Currently not implemented")
        elif sys.argv[1] == "met-frl": print("Currently not implemented")
        else: print("Script not recognized")
