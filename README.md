# WavePy 2.0

Wavepy2 is a refactored and enhanced version of [wavepy](https://github.com/APS-XSD-OPT-Group/wavepy) and [wavepytools](https://github.com/APS-XSD-OPT-Group/wavepytools).

Authors
-------------
[Luca Rebuffi](mailto:lrebuffi@anl.gov), [Xianbo Shi](mailto:xshi@anl.gov) and [Zhi Qiao](mailto:zqiao@anl.gov)

Instructions
-------------

Prerequisites: `xraylib 3.3.0` - see: https://github.com/tschoonj/xraylib/wiki/Installation-instructions

To install:               `python3 -m pip install wavepy2`
  
To show help:             `python3 -m aps.wavepy2.tools --h`

To run a script:          `python3 -m aps.wavepy2.tools <script id> <options>`
  
To show help of a script: `python -m aps.wavepy2.tools <script id> --h`
  

Available scripts:
1) Imaging   - Single Grating Talbot, id: `img-sgt`
2) Coherence - Single Grating Z Scan, id: `coh-sgz`
3) Metrology - Fit Residual Lenses,   id: `met-frl`

Copyright
----------
Copyright (c) 2020, UChicago Argonne, LLC. All rights reserved.         
                                                                         
 Copyright 2020. UChicago Argonne, LLC. This software was produced under U.S. Government contract DE-AC02-06CH11357 for Argonne National Laboratory (ANL), which is operated by UChicago Argonne, LLC for the U.S. Department of Energy. The U.S. Government has rights to use,       
 reproduce, and distribute this software. NEITHER THE GOVERNMENT NOR UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  
 If software is modified to produce derivative works, such modified software should be clearly marked, so as not to confuse it with the version available from ANL.                                                               
                                                                         
 Additionally, redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:                                                     
                                                                         
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.     
                                                                         
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.                                                     
                                                                         
 * Neither the name of UChicago Argonne, LLC, Argonne National Laboratory, ANL, the U.S. Government, nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.     
                                                                         
 THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                             
