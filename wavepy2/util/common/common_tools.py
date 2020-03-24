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
import numpy as np
from scipy.interpolate import UnivariateSpline

# ---------------------------------------------------------------------------
# Fourier Transform

try:
    from  pyfftw.interfaces.numpy_fft import fft2, ifft2
except ImportError:
    from  numpy.fft import fft2, ifft2

class FourierTransform:
    @classmethod
    def fft(cls, img):
        return np.fft.fftshift(fft2(img, norm='ortho'))

    @classmethod
    def ifft(cls, imgFFT):
        return ifft2(np.fft.ifftshift(imgFFT), norm='ortho')

# ---------------------------------------------------------------------------
# MISCELLANEA (FROM WAVEPY)

import os
from itertools import count

def get_unique_filename(patternforname, extension='txt', width=2, isFolder=False):
    '''
    Produce a string in the format `patternforname_XX.extension`, where XX is
    the smalest number in order that the string is a unique filename.

    Parameters
    ----------

    patternforname: str
        Main part of the filename. Accept directories path.

    extension: str
        Sufix for file name.


    Notes
    -----

    This will just return the filename, it will not create any file.

    '''

    if isFolder:
        extension = os.sep
        if os.sep in patternforname[-1]: patternforname = patternforname[:-1]
    else:
        if '.' not in extension: extension = '.' + extension

    _Count_fname = count()
    next(_Count_fname)

    tmp_str = '{:s}_{:0' + str(width) + 'd}'
    fname = str(tmp_str.format(patternforname, next(_Count_fname)) + extension)

    while os.path.isfile(fname) or os.path.isdir(fname):
        fname = str(tmp_str.format(patternforname, next(_Count_fname)) + extension)

    return fname


def choose_unit(array):
    """

    Script to choose good(best) units in engineering notation
    for a ``ndarray``.

    For a given input array, the function returns ``factor`` and ``unit``
    according to

    .. math:: 10^{n} < \max(array) < 10^{n + 3}

    +------------+----------------------+------------------------+
    |     n      |    factor (float)    |        unit(str)       |
    +============+======================+========================+
    |     0      |    1.0               |   ``''`` empty string  |
    +------------+----------------------+------------------------+
    |     -12     |    10^-12           |        ``p``           |
    +------------+----------------------+------------------------+
    |     -9     |    10^-9             |        ``n``           |
    +------------+----------------------+------------------------+
    |     -6     |    10^-6             |     ``r'\mu'``         |
    +------------+----------------------+------------------------+
    |     -3     |    10^-3             |        ``m``           |
    +------------+----------------------+------------------------+
    |     +3     |    10^-6             |        ``k``           |
    +------------+----------------------+------------------------+
    |     +6     |    10^-9             |        ``M``           |
    +------------+----------------------+------------------------+
    |     +9     |    10^-6             |        ``G``           |
    +------------+----------------------+------------------------+

    ``n=-6`` returns ``\mu`` since this is the latex syntax for micro.
    See Example.


    Parameters
    ----------
    array : ndarray
        array from where to choose proper unit.

    Returns
    -------
    float, unit :
        Multiplication Factor and strig for unit

    Example
    -------

    >>> array1 = np.linspace(0,100e-6,101)
    >>> array2 = array1*1e10
    >>> factor1, unit1 = choose_unit(array1)
    >>> factor2, unit2 = choose_unit(array2)
    >>> plt.plot(array1*factor1,array2*factor2)
    >>> plt.xlabel(r'${0} m$'.format(unit1))
    >>> plt.ylabel(r'${0} m$'.format(unit2))

    The syntax ``r'$ string $ '`` is necessary to use latex commands in the
    :py:mod:`matplotlib` labels.

    """

    max_abs = np.max(np.abs(array))

    if 2e0 < max_abs <= 2e3:
        factor = 1.0
        unit = ''
    elif 2e-12 < max_abs <= 2e-9:
        factor = 1.0e12
        unit = 'p'
    elif 2e-9 < max_abs <= 2e-6:
        factor = 1.0e9
        unit = 'n'
    elif 2e-6 < max_abs <= 2e-3:
        factor = 1.0e6
        unit = r'\mu'
    elif 2e-3 < max_abs <= 2e0:
        factor = 1.0e3
        unit = 'm'
    elif 2e3 < max_abs <= 2e6:
        factor = 1.0e-3
        unit = 'k'
    elif 2e6 < max_abs <= 2e9:
        factor = 1.0e-6
        unit = 'M'
    elif 2e9 < max_abs <= 2e12:
        factor = 1.0e-6
        unit = 'G'
    else:
        factor = 1.0
        unit = ' '

    return factor, unit

def crop_matrix_at_indexes(input_matrix, list_of_indexes):
    if list_of_indexes == [0, -1, 0, -1]:
        return input_matrix

    return np.copy(input_matrix[list_of_indexes[0]:list_of_indexes[1],
                   list_of_indexes[2]:list_of_indexes[3]])

def fwhm_xy(xvalues, yvalues):
    spline = UnivariateSpline(xvalues,
                              yvalues-np.min(yvalues)/2-np.max(yvalues)/2,
                              s=0)

    xvalues = spline.roots().tolist()
    yvalues = (spline(spline.roots()) + np.min(yvalues)/2 +
               np.max(yvalues)/2).tolist()

    if len(xvalues) == 2:
        return [xvalues, yvalues]

    else:
        return[[], []]

def mean_plus_n_sigma(array, n_sigma=5):
    return np.nanmean(array) + n_sigma*np.nanstd(array)

def extent_func(img, pixelsize=[1, 1]):
    if isinstance(pixelsize, float): pixelsize = [pixelsize, pixelsize]

    return np.array((-img.shape[1] // 2 * pixelsize[1],
                     (img.shape[1] - img.shape[1] // 2) * pixelsize[1],
                     -img.shape[0] // 2 * pixelsize[0],
                     (img.shape[0] - img.shape[0] // 2) * pixelsize[0]))


def get_idxPeak_ij(harV, harH, nRows, nColumns, periodVert, periodHor):
    return [nRows // 2 + harV * periodVert, nColumns // 2 + harH * periodHor]

def get_idxPeak_ij_exp(imgFFT, harV, harH, periodVert, periodHor, searchRegion):
    (nRows, nColumns) = imgFFT.shape

    idxPeak_ij = get_idxPeak_ij(harV, harH, nRows, nColumns, periodVert, periodHor)

    maskSearchRegion = np.zeros((nRows, nColumns))
    maskSearchRegion[idxPeak_ij[0] - searchRegion:
                     idxPeak_ij[0] + searchRegion,
                     idxPeak_ij[1] - searchRegion:
                     idxPeak_ij[1] + searchRegion] = 1.0

    intensity = (np.abs(imgFFT))
    idxPeak_ij_exp = np.where(intensity * maskSearchRegion == np.max(intensity * maskSearchRegion))

    return [idxPeak_ij_exp[0][0], idxPeak_ij_exp[1][0]]


def is_empty_file_name(file_name):
    return file_name is None or \
            file_name.strip() == "" or \
            file_name.strip().lower() == "none"
