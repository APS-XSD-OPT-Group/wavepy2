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

class AlreadyInitializedError(ValueError):
    def __init__(self, message=None):
        super(AlreadyInitializedError, self).__init__(message)

class GenericRegistry(object):
    _NO_APPLICATION = "<NO APPLICATION>"

    def __init__(self, registry_name):
        self.__registry_name = registry_name
        self.__registry = {self._NO_APPLICATION: None}

    def register_instance(self, instance, application_name=None, replace=False):
        if instance is None: raise ValueError(self.__registry_name + " Instance is None")

        application_name = self.__get_application_name(application_name)

        if application_name in self.__registry.keys():
            if self.__registry[application_name] is None or replace==True:
                self.__registry[application_name] = instance
            else:
                raise AlreadyInitializedError(self.__registry_name + " Instance already initialized")
        else:
            self.__registry[application_name] = instance

    def reset(self, application_name=None):
        application_name = self.__get_application_name(application_name)

        if application_name in self.__registry.keys():
            self.__registry[self.__get_application_name(application_name)] = None
        else:
            raise ValueError(self.__registry_name + " Instance not existing")

    def get_instance(self, application_name=None):
        application_name = self.__get_application_name(application_name)

        if application_name in self.__registry.keys():
            return self.__registry[self.__get_application_name(application_name)]
        else:
            raise ValueError(self.__registry_name + " Instance not existing")

    def __get_application_name(self, application_name):
        return self._NO_APPLICATION if application_name is None else application_name

# ---------------------------------------------------------------------------
# Fourier Transform

try:
    from  pyfftw.interfaces.numpy_fft import fft, ifft, fft2, ifft2
except ImportError:
    from  numpy.fft import fft, ifft, fft2, ifft2

class FourierTransform:
    @classmethod
    def fft1d(cls, array):
        return np.fft.fftshift(fft(array))

    @classmethod
    def ifft1d(cls, arrayFFT):
        return ifft(np.fft.ifftshift(arrayFFT))

    @classmethod
    def fft_2d1d(cls, array2d, axis):
        return np.fft.fftshift(fft(array2d, axis=axis), axes=axis)

    @classmethod
    def ifft_2d1d(cls, array2dFFT, axis):
        return ifft(np.fft.ifftshift(array2dFFT, axes=axis), axis=axis)

    @classmethod
    def fft2d(cls, img):
        return np.fft.fftshift(fft2(img, norm='ortho'))

    @classmethod
    def ifft2d(cls, imgFFT):
        return ifft2(np.fft.ifftshift(imgFFT), norm='ortho')

# ---------------------------------------------------------------------------
# MISCELLANEA (FROM WAVEPY)

PATH_SEPARATOR = "/" # Windows works in Anaconda Prompt...

from scipy import constants

hc = constants.value('inverse meter-electron volt relationship')  # hc


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
        extension = PATH_SEPARATOR
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


def lsq_fit_parabola(zz, pixelsize):
    xx, yy = grid_coord(zz, pixelsize)
    f = zz.flatten()
    x = xx.flatten()
    y = yy.flatten()
    X_matrix = np.vstack([x**2, y**2, x, y, x*0.0 + 1]).T
    beta_matrix = np.linalg.lstsq(X_matrix, f)[0]
    fit = (beta_matrix[0]*(xx**2) +
           beta_matrix[1]*(yy**2) +
           beta_matrix[2]*xx +
           beta_matrix[3]*yy +
           beta_matrix[4])
    R_x = 1/2/beta_matrix[0]
    R_y = 1/2/beta_matrix[1]
    x_o = -beta_matrix[2]/beta_matrix[0]/2
    y_o = -beta_matrix[3]/beta_matrix[1]/2
    offset = beta_matrix[3]
    popt = [R_x, R_y, x_o, y_o, offset]

    return fit, popt

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

from time import strftime

# time functions
def datetime_now_str():
    return strftime("%Y%m%d_%H%M%S")

def time_now_str():
    return strftime("%H%M%S")

def date_now_str():
    return strftime("%Y%m%d")

def is_empty_string(string):
    return string is None or string.strip() == ""

def is_empty_file_name(file_name):
    return is_empty_string(file_name) or file_name.strip().lower() == "none"

# COORDINATES

def realcoordvec(npoints, delta):
    return (np.linspace(1, npoints, npoints) - npoints//2 - 1) * delta

def realcoordmatrix_fromvec(xvec, yvec):
    return np.meshgrid(xvec, yvec)

def realcoordmatrix(npointsx, deltax, npointsy, deltay):
    return realcoordmatrix_fromvec(realcoordvec(npointsx, deltax), realcoordvec(npointsy, deltay))

def grid_coord(array2D, pixelsize):
    if isinstance(pixelsize, float): pixelsize = [pixelsize, pixelsize]
    return realcoordmatrix(array2D.shape[1], pixelsize[1], array2D.shape[0], pixelsize[0])

def reciprocalcoordvec(npoints, delta):
    return (np.linspace(0, 1, npoints, endpoint=False) - .5)/delta

def reciprocalcoordmatrix(npointsx, deltax, npointsy, deltay):
    return np.meshgrid(reciprocalcoordvec(npointsx, deltax), reciprocalcoordvec(npointsy, deltay))

def fouriercoordvec(npoints, delta):
    return reciprocalcoordvec(npoints, delta)

def fouriercoordmatrix(npointsx, deltax, npointsy, deltay):
    return reciprocalcoordmatrix(npointsx, deltax, npointsy, deltay)

# SHIFTS

def fourier_spline_1d(vec1d, n=2):
    # reflec pad to avoid discontinuity at the edges
    fftvec = FourierTransform.fft1d(np.pad(vec1d, (0, vec1d.shape[0]), 'reflect'))
    res = FourierTransform.ifft1d(np.pad(fftvec, pad_width=fftvec.shape[0] * (n - 1) // 2, mode='constant', constant_values=0.0)) * n

    return res[0:res.shape[0]//2]

def fourier_spline_2d_axis(array, n=2, axis=0):
    # reflec pad to avoid discontinuity at the edges
    if axis == 0:   padwidth = ((0, array.shape[0]), (0, 0))
    elif axis == 1: padwidth = ((0, 0), (0, array.shape[1]))

    fftvec = FourierTransform.fft_2d1d(np.pad(array, pad_width=padwidth, mode='reflect'), axis=axis)

    listpad = [(0, 0), (0, 0)]
    if fftvec.shape[axis]*(n-1) % 2 == 0: listpad[axis] = (fftvec.shape[axis]*(n-1)//2, fftvec.shape[axis]*(n-1)//2)
    else: listpad[axis] = (fftvec.shape[axis]*(n-1)//2, fftvec.shape[axis]*(n-1)//2 + 1)

    fftvec = np.pad(fftvec, pad_width=listpad, mode='constant', constant_values=0.0)
    res = np.real(FourierTransform.ifft_2d1d(fftvec, axis)*n)

    if axis == 0:   return res[0:res.shape[0]//2, :]
    elif axis == 1: return res[:, 0:res.shape[1]//2]

def fourier_spline_2d(array2d, n=2):
    return fourier_spline_2d_axis(fourier_spline_2d_axis(array2d, n=n, axis=0), n=n, axis=1)

def shift_subpixel_1d(array, frac_of_pixel, axis=0):
    if array.ndim == 1: return fourier_spline_1d(array, frac_of_pixel)[1::frac_of_pixel]
    elif array.ndim == 2:
        if axis == 0:   return fourier_spline_2d_axis(array, frac_of_pixel, axis=0)[1::frac_of_pixel, :]
        elif axis == 1: return fourier_spline_2d_axis(array, frac_of_pixel, axis=0)[:, 1::frac_of_pixel]

def shift_subpixel_2d(array2d, frac_of_pixel):
    return fourier_spline_2d(array2d, frac_of_pixel)[1::frac_of_pixel, 1::frac_of_pixel]

