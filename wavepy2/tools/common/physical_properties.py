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

import xraylib

MATERIALS = ['Diamond, 3.525g/cm^3', 'Beryllium, 1.848 g/cm^3']

def get_delta(phenergy, material_idx=None, material=None, density=None):
    """
    Get value of delta (refractive index `n = 1 - delta + i*beta`) for few
    common materials. It also wors as an interface to `xraylib`, using the same
    syntax for materials names.
    This function can be expanded by including more materials
    to the (internal) list.


    Parameters
    ----------
    phenergy : float
        Photon energy in eV to obtain delta

    choice_idx : int
        - 0 : 'Diamond, 3.525g/cm^3'\n
        - 1 : 'Beryllium, 1.848 g/cm^3'

    material : string
        Material string as used by xraylib.

    density : float
        Material density. optional.

    Returns
    -------
    float, str, float
        delta value, material string, density


    Example
    -------

        >>> get_delta(8000)

        will start the dialogs to input the required paremeters.

        Alternativally

        >>> get_delta(8000, material='Be')

        returns the value of delta with default density.

    """

    if not material_idx is None:
        if material_idx == 0:
            density = density if not density is None else 3.525
            delta = 1 - xraylib.Refractive_Index_Re("C", phenergy/1e3, 3.525)
            material = 'Diamond'
        elif material_idx == 1:
            density = density if not density is None else xraylib.ElementDensity(4)
            delta = 1 - xraylib.Refractive_Index_Re("Be", phenergy/1e3, density)
            material = 'Beryllium'
    elif not material is None:
        elementZnumber = xraylib.SymbolToAtomicNumber(material)
        density = density if not density is None else xraylib.ElementDensity(elementZnumber)
        delta = 1 - xraylib.Refractive_Index_Re(material, phenergy/1e3, density)
    else:
        raise ValueError("Delta calculation is not possibile: specify material idx or material name and density (optional)")

    return delta, material, density
