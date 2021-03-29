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
from scipy.ndimage.filters import uniform_filter
from skimage.restoration import unwrap_phase

from wavepy2.tools.common.widgets.extract_harmonic_plot_widget import ExtractHarmonicPlot
from wavepy2.tools.common.widgets.harmonic_grid_plot_widget import HarmonicGridPlot
from wavepy2.tools.common.widgets.single_grating_harmonic_images_widget import SingleGratingHarmonicImages
from wavepy2.util.log.logger   import LoggerFacade
from wavepy2.util.plot.plotter import PlotterFacade
from wavepy2.util.common.common_tools import FourierTransform, get_idxPeak_ij, get_idxPeak_ij_exp, crop_matrix_at_indexes, mean_plus_n_sigma


class MockLogger(LoggerFacade):
    def print(self, message): pass
    def print_message(self, message): pass
    def print_warning(self, message): pass
    def print_error(self, message): pass
    def print_other(self, message, prefix, color): pass

class MockPlotter(PlotterFacade):
    def push_plot_on_context(self, context_key, widget_class, unique_id=None, **kwargs): pass

def exp_harm_period(img, harmonicPeriod, harmonic_ij='00', searchRegion=10, isFFT=False, logger=MockLogger()):
    """
    Function to obtain the position (in pixels) in the reciprocal space
    of the first harmonic ().
    """

    (nRows, nColumns) = img.shape # this is important in the case of FFT = false it takes the direct space

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

    if isFFT: imgFFT = img
    else: imgFFT = FourierTransform.fft2d(img)

    del_i, del_j = __error_harmonic_peak(imgFFT, harV, harH,
                                         periodVert, periodHor,
                                         searchRegion)

    logger.print_message("Error experimental harmonics vertical: {:d}".format(del_i))
    logger.print_message("Error experimental harmonics horizontal: {:d}".format(del_j))

    return periodVert + del_i, periodHor + del_j

def single_2Dgrating_analyses(img, img_ref=None, harmonicPeriod=None, unwrapFlag=True, context_key="single_2Dgrating_analyses", unique_id=None, logger=MockLogger(), plotter=MockPlotter(), **kwargs):
    """
    Function to process the data of single 2D grating Talbot imaging. It
    wraps other functions in order to make all the process transparent

    """

    # Obtain Harmonic images
    h_img = __single_grating_harmonic_images(img, harmonicPeriod, context_key=context_key, unique_id=unique_id, logger=logger, plotter=plotter, **kwargs)

    if img_ref is not None:  # relative wavefront
        h_img_ref = __single_grating_harmonic_images(img_ref, harmonicPeriod, context_key=context_key, image_name="Ref", unique_id=unique_id, logger=logger, plotter=plotter, **kwargs)

        int00 = np.abs(h_img[0])/np.abs(h_img_ref[0])
        int01 = np.abs(h_img[1])/np.abs(h_img_ref[1])
        int10 = np.abs(h_img[2])/np.abs(h_img_ref[2])

        if unwrapFlag is True:
            arg01 = (unwrap_phase(np.angle(h_img[1]), seed=72673) -
                     unwrap_phase(np.angle(h_img_ref[1]), seed=72673))
            arg10 = (unwrap_phase(np.angle(h_img[2]), seed=72673) -
                     unwrap_phase(np.angle(h_img_ref[2]), seed=72673))
        else:
            arg01 = np.angle(h_img[1]) - np.angle(h_img_ref[1])
            arg10 = np.angle(h_img[2]) - np.angle(h_img_ref[2])

    else:  # absolute wavefront
        int00 = np.abs(h_img[0])
        int01 = np.abs(h_img[1])
        int10 = np.abs(h_img[2])

        if unwrapFlag is True:
            arg01 = unwrap_phase(np.angle(h_img[1]), seed=72673)
            arg10 = unwrap_phase(np.angle(h_img[2]), seed=72673)
        else:
            arg01 = np.angle(h_img[1])
            arg10 = np.angle(h_img[2])

    if unwrapFlag is True:  # remove pi jump
        arg01 -= int(np.round(np.mean(arg01/np.pi)))*np.pi
        arg10 -= int(np.round(np.mean(arg10/np.pi)))*np.pi

    darkField01 = int01/int00
    darkField10 = int10/int00

    return [int00, int01, int10,
            darkField01, darkField10,
            arg01, arg10]

def visib_1st_harmonics(img, harmonicPeriod, searchRegion=20, unFilterSize=1):
    """
    This function obtain the visibility in a grating imaging experiment by the
    ratio of the amplitudes of the first and zero harmonics. See
    https://doi.org/10.1364/OE.22.014041 .

    Note
    ----
    Note that the absolute visibility also depends on the higher harmonics, and
    for a absolute value of visibility all of them must be considered.


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

    searchRegion: int
        search for the peak will be in a region of harmonicPeriod/searchRegion
        around the theoretical peak position. See also
        `:py:func:`wavepy.grating_interferometry.plot_harmonic_grid`

    verbose: Boolean
        verbose flag.


    Returns
    -------
    (float, float)
        horizontal and vertical visibilities respectivelly from
        harmonics 01 and 10


    """

    imgFFT = FourierTransform.fft2d(img)

    _idxPeak_ij_exp00 = get_idxPeak_ij_exp(imgFFT, 0, 0, harmonicPeriod[0], harmonicPeriod[1], searchRegion)
    _idxPeak_ij_exp10 = get_idxPeak_ij_exp(imgFFT, 1, 0, harmonicPeriod[0], harmonicPeriod[1], searchRegion)
    _idxPeak_ij_exp01 = get_idxPeak_ij_exp(imgFFT, 0, 1, harmonicPeriod[0], harmonicPeriod[1], searchRegion)

    arg_imgFFT = np.abs(imgFFT)

    if unFilterSize > 1: arg_imgFFT = uniform_filter(arg_imgFFT, unFilterSize)

    peak00 = arg_imgFFT[_idxPeak_ij_exp00[0], _idxPeak_ij_exp00[1]]
    peak10 = arg_imgFFT[_idxPeak_ij_exp10[0], _idxPeak_ij_exp10[1]]
    peak01 = arg_imgFFT[_idxPeak_ij_exp01[0], _idxPeak_ij_exp01[1]]

    return 2*peak10/peak00, 2*peak01/peak00, _idxPeak_ij_exp00, _idxPeak_ij_exp10, _idxPeak_ij_exp01

####################################
# PRIVATE METHODS

def __check_harmonic_inside_image(harV, harH, nRows, nColumns, periodVert, periodHor, logger):
    """
    Check if full harmonic image is within the main image
    """
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

    idxPeak_ij     = get_idxPeak_ij(harV, harH, imgFFT.shape[0], imgFFT.shape[1], periodVert, periodHor)
    idxPeak_ij_exp = get_idxPeak_ij_exp(imgFFT, harV, harH, periodVert, periodHor, searchRegion)

    del_i = idxPeak_ij_exp[0] - idxPeak_ij[0]
    del_j = idxPeak_ij_exp[1] - idxPeak_ij[1]

    return del_i, del_j

def __extract_harmonic(imgFFT, harmonicPeriod, harmonic_ij='00', searchRegion=10, context_key="extract_harmonic", image_name="Image", unique_id=None, logger=MockLogger(), plotter=MockPlotter(), **kwargs):
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

    __check_harmonic_inside_image(harV, harH, nRows, nColumns, periodVert, periodHor, logger)

    intensity = (np.abs(imgFFT))

    #  Estimate harmonic positions
    idxPeak_ij   = get_idxPeak_ij(harV, harH, nRows, nColumns, periodVert, periodHor)
    del_i, del_j = __error_harmonic_peak(imgFFT, harV, harH, periodVert, periodHor, searchRegion)

    logger.print_message("extract_harmonic: harmonic peak " + harmonic_ij[0] + harmonic_ij[1] + " is misplaced by:")
    logger.print_message("{:d} pixels in vertical, {:d} pixels in hor".format(del_i, del_j))
    logger.print_message("Theoretical peak index: {:d},{:d} [VxH]".format(idxPeak_ij[0], idxPeak_ij[1]))

    if ((np.abs(del_i) > searchRegion // 2) or (np.abs(del_j) > searchRegion // 2)):
        logger.print_warning("Harmonic Peak " + harmonic_ij[0] + harmonic_ij[1] + " is too far from theoretical value.")
        logger.print_warning("{:d} pixels in vertical, {:d} pixels in hor".format(del_i, del_j))

    plotter.push_plot_on_context(context_key, ExtractHarmonicPlot, unique_id,
                                 intensity=intensity,
                                 idxPeak_ij=idxPeak_ij,
                                 harmonic_ij=harmonic_ij,
                                 nColumns=nColumns,
                                 nRows=nRows,
                                 periodVert=periodVert,
                                 periodHor=periodHor,
                                 image_name=image_name, **kwargs)

    return imgFFT[idxPeak_ij[0] - periodVert // 2:
                  idxPeak_ij[0] + periodVert//2,
                  idxPeak_ij[1] - periodHor//2:
                  idxPeak_ij[1] + periodHor//2]

def __single_grating_harmonic_images(img, harmonicPeriod, searchRegion=10, context_key="single_grating_harmonic", image_name="", unique_id=None, logger=MockLogger(), plotter=MockPlotter(), **kwargs):
    """
    Auxiliary function to process the data of single 2D grating Talbot imaging.
    It obtain the (real space) harmonic images  00, 01 and 10.

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

    searchRegion: int
        search for the peak will be in a region of harmonicPeriod/searchRegion
        around the theoretical peak position. See also
        `:py:func:`wavepy.grating_interferometry.plot_harmonic_grid`

    Returns
    -------
    three 2D ndarray data
        Images obtained from the harmonics 00, 01 and 10.

    """

    imgFFT = FourierTransform.fft2d(img)

    plotter.push_plot_on_context(context_key, HarmonicGridPlot, unique_id, imgFFT=imgFFT, harmonicPeriod=harmonicPeriod, image_name=image_name, **kwargs)

    imgFFT00 = __extract_harmonic(imgFFT,
                                  harmonicPeriod=harmonicPeriod,
                                  harmonic_ij='00',
                                  searchRegion=searchRegion,
                                  context_key=context_key,
                                  image_name=image_name, unique_id=unique_id,
                                  logger=logger, plotter=plotter,
                                  **kwargs)

    imgFFT01 = __extract_harmonic(imgFFT,
                                  harmonicPeriod=harmonicPeriod,
                                  harmonic_ij=['0', '1'],
                                  searchRegion=searchRegion,
                                  context_key=context_key,
                                  image_name=image_name, unique_id=unique_id,
                                  logger=logger, plotter=plotter,
                                  **kwargs)

    imgFFT10 = __extract_harmonic(imgFFT,
                                  harmonicPeriod=harmonicPeriod,
                                  harmonic_ij=['1', '0'],
                                  searchRegion=searchRegion,
                                  context_key=context_key,
                                  image_name=image_name, unique_id=unique_id,
                                  logger=logger, plotter=plotter,
                                  **kwargs)

    plotter.push_plot_on_context(context_key, SingleGratingHarmonicImages, unique_id,
                                 imgFFT00=imgFFT00, imgFFT01=imgFFT01, imgFFT10=imgFFT10,
                                 image_name=image_name, **kwargs)

    img00 = FourierTransform.ifft2d(imgFFT00)

    # non existing harmonics will return NAN, so here we check NAN
    if np.all(np.isfinite(imgFFT01)): img01 = FourierTransform.ifft2d(imgFFT01)
    else: img01 = imgFFT01

    if np.all(np.isfinite(imgFFT10)): img10 = FourierTransform.ifft2d(imgFFT10)
    else: img10 = imgFFT10

    return (img00, img01, img10)
