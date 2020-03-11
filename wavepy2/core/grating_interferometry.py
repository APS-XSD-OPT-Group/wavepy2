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

from wavepy2.utility.logger import get_registered_logger_instance

try:
    from  pyfftw.interfaces.numpy_fft import fft2, ifft2
except ImportError:
    from  numpy.fft import fft2, ifft2

def __idxPeak_ij(harV, harH, nRows, nColumns, periodVert, periodHor):
    """
    Calculates the theoretical indexes of the harmonic peak
    [`harV`, `harH`] in the main FFT image
    """
    return [nRows // 2 + harV * periodVert, nColumns // 2 + harH * periodHor]

def __idxPeak_ij_exp(imgFFT, harV, harH, periodVert, periodHor, searchRegion):
    """
    Returns the index of the maximum intensity in a harmonic sub image.
    """

    intensity = (np.abs(imgFFT))

    (nRows, nColumns) = imgFFT.shape

    idxPeak_ij = __idxPeak_ij(harV, harH, nRows, nColumns,
                             periodVert, periodHor)

    maskSearchRegion = np.zeros((nRows, nColumns))

    maskSearchRegion[idxPeak_ij[0] - searchRegion:
                     idxPeak_ij[0] + searchRegion,
                     idxPeak_ij[1] - searchRegion:
                     idxPeak_ij[1] + searchRegion] = 1.0

    idxPeak_ij_exp = np.where(intensity * maskSearchRegion ==
                              np.max(intensity * maskSearchRegion))

    return [idxPeak_ij_exp[0][0], idxPeak_ij_exp[1][0]]


def __check_harmonic_inside_image(harV, harH, nRows, nColumns, periodVert, periodHor):
    """
    Check if full harmonic image is within the main image
    """
    logger = get_registered_logger_instance()

    errFlag = False

    if (harV + .5)*periodVert > nRows / 2:
        logger.print_error("Harmonic Peak {:d}{:d}".format(harV, harH) + " is out of image vertical range.")
        errFlag = True

    if (harH + .5)*periodHor > nColumns / 2:
        logger.print_error("Harmonic Peak {:d}{:d}".format(harV, harH) + " is out of image horizontal range.")
        errFlag = True

    if errFlag:
        raise ValueError("ERROR: Harmonic Peak " +
                         "{:d}{:d} is ".format(harV, harH) +
                         "out of image frequency range.")


def __error_harmonic_peak(imgFFT, harV, harH, periodVert, periodHor, searchRegion=10):
    """
    Error in pixels (in the reciprocal space) between the harmonic peak and
    the provided theoretical value
    """

    #  Estimate harmonic positions

    idxPeak_ij     = __idxPeak_ij(harV, harH, imgFFT.shape[0], imgFFT.shape[1], periodVert, periodHor)
    idxPeak_ij_exp = __idxPeak_ij_exp(imgFFT, harV, harH, periodVert, periodHor, searchRegion)

    del_i = idxPeak_ij_exp[0] - idxPeak_ij[0]
    del_j = idxPeak_ij_exp[1] - idxPeak_ij[1]

    return del_i, del_j

def exp_harm_period(img, harmonicPeriod, harmonic_ij='00', searchRegion=10, isFFT=False):
    """
    Function to obtain the position (in pixels) in the reciprocal space
    of the first harmonic ().
    """
    logger = get_registered_logger_instance()

    (nRows, nColumns) = img.shape

    harV = int(harmonic_ij[0])
    harH = int(harmonic_ij[1])

    periodVert = harmonicPeriod[0]
    periodHor = harmonicPeriod[1]

    # adjusts for 1D grating
    if periodVert <= 0 or periodVert is None:
        periodVert = nRows
        logger.print_message("Assuming Horizontal 1D Grating")

    if periodHor <= 0 or periodHor is None:
        periodHor = nColumns
        logger.print_message("Assuming Vertical 1D Grating")

    if isFFT:
        imgFFT = img
    else:
        imgFFT = np.fft.fftshift(fft2(img, norm='ortho'))

    del_i, del_j = __error_harmonic_peak(imgFFT, harV, harH,
                                        periodVert, periodHor,
                                        searchRegion)

    logger.print_message("Error experimental harmonics vertical: {:d}".format(del_i))
    logger.print_message("Error experimental harmonics horizontal: {:d}".format(del_j))

    return periodVert + del_i, periodHor + del_j


def extract_harmonic(imgFFT, harmonicPeriod, harmonic_ij='00', searchRegion=10):

    """
    Function to extract one harmonic image of the FFT of single grating
    Talbot imaging.


    The function use the provided value of period to search for the harmonics
    peak. The search is done in a rectangle of size
    ``periodVert*periodHor/searchRegion**2``. The final result is a rectagle of
    size ``periodVert x periodHor`` centered at
    ``(harmonic_Vertical*periodVert x harmonic_Horizontal*periodHor)``


    Parameters
    ----------

    img : 	ndarray – Data (data_exchange format)
        Experimental image, whith proper blank image, crop and rotation already
        applied.

    harmonicPeriod : list of integers in the format [periodVert, periodHor]
        ``periodVert`` and ``periodVert`` are the period of the harmonics in
        the reciprocal space in pixels. For the checked board grating,
        periodVert = sqrt(2) * pixel Size / grating Period * number of
        rows in the image. For 1D grating, set one of the values to negative or
        zero (it will set the period to number of rows or colunms).

    harmonic_ij : string or list of string
        string with the harmonic to extract, for instance '00', '01', '10'
        or '11'. In this notation negative harmonics are not allowed.

        Alternativelly, it accepts a list of string
        ``harmonic_ij=[harmonic_Vertical, harmonic_Horizontal]``, for instance
        ``harmonic_ij=['0', '-1']``

        Note that since the original image contain only real numbers (not
        complex), then negative and positive harmonics are symetric
        related to zero.
    isFFT : Boolean
        Flag that tells if the input image ``img`` is in the reciprocal
        (``isFFT=True``) or in the real space (``isFFT=False``)

    searchRegion: int
        search for the peak will be in a region of harmonicPeriod/searchRegion
        around the theoretical peak position

    plotFlag: Boolean
        Flag to plot the image in the reciprocal space and to show the position
        of the found peaked and the limits of the harmonic image

    verbose: Boolean
        verbose flag.


    Returns
    -------
    2D ndarray
        Copped Images of the harmonics ij


    This functions crops a rectagle of size ``periodVert x periodHor`` centered
    at ``(harmonic_Vertical*periodVert x harmonic_Horizontal*periodHor)`` from
    the provided FFT image.


    Note
    ----
        * Note that it is the FFT of the image that is required.
        * The search for the peak is only used to print warning messages.

    **Q: Why not the real image??**

    **A:** Because FFT can be time consuming. If we use the real image, it will
    be necessary to run FFT for each harmonic. It is encourage to wrap this
    function within a function that do the FFT, extract the harmonics, and
    return the real space harmonic image.


    See Also
    --------
    :py:func:`wavepy.grating_interferometry.plot_harmonic_grid`

    """
    logger = get_registered_logger_instance()

    (nRows, nColumns) = imgFFT.shape

    harV = int(harmonic_ij[0])
    harH = int(harmonic_ij[1])

    periodVert = harmonicPeriod[0]
    periodHor = harmonicPeriod[1]

    logger.print_message("Extracting harmonic " + harmonic_ij[0] + harmonic_ij[1])
    logger.print_message("Harmonic period Horizontal: {:d} pixels".format(periodHor))
    logger.print_message("Harmonic period Vertical: {:d} pixels".format(periodVert))

    # adjusts for 1D grating
    if periodVert <= 0 or periodVert is None:
        periodVert = nRows
        logger.print_message("Assuming Horizontal 1D Grating")

    if periodHor <= 0 or periodHor is None:
        periodHor = nColumns
        logger.print_message("Assuming Vertical 1D Grating")

    __check_harmonic_inside_image(harV, harH, nRows, nColumns, periodVert, periodHor)

    intensity = (np.abs(imgFFT))

    #  Estimate harmonic positions
    idxPeak_ij = __idxPeak_ij(harV, harH, nRows, nColumns, periodVert, periodHor)

    del_i, del_j = __error_harmonic_peak(imgFFT, harV, harH, periodVert, periodHor, searchRegion)

    logger.print_message("extract_harmonic: harmonic peak " + harmonic_ij[0] + harmonic_ij[1] + " is misplaced by:")
    logger.print_message("{:d} pixels in vertical, {:d} pixels in hor".format(del_i, del_j))
    logger.print_message("Theoretical peak index: {:d},{:d} [VxH]".format(idxPeak_ij[0], idxPeak_ij[1]))

    if ((np.abs(del_i) > searchRegion // 2) or (np.abs(del_j) > searchRegion // 2)):
        logger.print_warning("Harmonic Peak " + harmonic_ij[0] + harmonic_ij[1] + " is too far from theoretical value.")
        logger.print_warning("{:d} pixels in vertical,".format(del_i) + "{:d} pixels in hor".format(del_j))

    if False:

        from matplotlib.patches import Rectangle
        plt.figure(figsize=(8, 7))
        plt.imshow(np.log10(intensity), cmap='inferno', extent=wpu.extent_func(intensity))

        plt.xlabel('Pixels')
        plt.ylabel('Pixels')

        xo = idxPeak_ij[1] - nColumns//2 - periodHor//2
        yo = nRows//2 - idxPeak_ij[0] - periodVert//2
        # xo yo are the lower left position of the reangle

        plt.gca().add_patch(Rectangle((xo, yo),
                                      periodHor, periodVert,
                                      lw=2, ls='--', color='red',
                                      fill=None, alpha=1))

        plt.title('Selected Region ' + harmonic_ij[0] + harmonic_ij[1],
                  fontsize=18, weight='bold')
        plt.show(block=False)

    return imgFFT[idxPeak_ij[0] - periodVert//2:
                  idxPeak_ij[0] + periodVert//2,
                  idxPeak_ij[1] - periodHor//2:
                  idxPeak_ij[1] + periodHor//2]
