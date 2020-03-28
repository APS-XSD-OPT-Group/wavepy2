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

from wavepy2.util.common import common_tools
from wavepy2.util.log.logger import get_registered_logger_instance, get_registered_secondary_logger
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.wavepy_data import WavePyData

from wavepy2.core import grating_interferometry
from wavepy2.core.widgets.plot_intensities_harms import PlotIntensitiesHarms
from wavepy2.core.widgets.plot_dark_field import PlotDarkField
from wavepy2.tools.imaging.single_grating.widgets.plot_DPC import PlotDPC

from wavepy2.tools.imaging.single_grating.widgets.input_parameters_widget import InputParametersWidget, generate_initialization_parameters
from wavepy2.tools.imaging.single_grating.widgets.crop_dialog_widget import CropDialogPlot
from wavepy2.tools.imaging.single_grating.widgets.second_crop_dialog_widget import SecondCropDialogPlot
from wavepy2.tools.imaging.single_grating.widgets.show_cropped_figure_widget import ShowCroppedFigure
from wavepy2.tools.imaging.single_grating.widgets.correct_DPC import CorrectDPC, CorrectDPCHistos, CorrectDPCCenter


from scipy import constants

hc = constants.value('inverse meter-electron volt relationship')  # hc

CALCULATE_DPC_CONTEXT_KEY = "Calculate DPC"
RECROP_DPC_CONTEXT_KEY = "Recrop DPC"
CORRECT_ZERO_DPC = "Correct Zero DPC"
REMOVE_LINEAR_FIT = "Remove Linear Fit"

def get_initialization_parameters():
    plotter = get_registered_plotter_instance()

    if plotter.is_active():
        return plotter.show_interactive_plot(InputParametersWidget, container_widget=None)
    else:
        ini = get_registered_ini_instance()

        return generate_initialization_parameters(img_file_name      = ini.get_string_from_ini("Files", "sample"),
                                                  imgRef_file_name   = ini.get_string_from_ini("Files", "reference"),
                                                  imgBlank_file_name = ini.get_string_from_ini("Files", "blank"),
                                                  mode               = ini.get_string_from_ini("Parameters", "mode"),
                                                  pixel              = ini.get_float_from_ini("Parameters", "pixel size"),
                                                  gratingPeriod      = ini.get_float_from_ini("Parameters", "checkerboard grating period"),
                                                  pattern            = ini.get_string_from_ini("Parameters", "pattern"),
                                                  distDet2sample     = ini.get_float_from_ini("Parameters", "distance detector to gr"),
                                                  phenergy           = ini.get_float_from_ini("Parameters", "photon energy"),
                                                  sourceDistance     = ini.get_float_from_ini("Parameters", "source distance"),
                                                  correct_pi_jump    = ini.get_boolean_from_ini("Runtime", "correct pi jump"),
                                                  remove_mean        = ini.get_boolean_from_ini("Runtime", "remove mean"),
                                                  correct_dpc_center = ini.get_boolean_from_ini("Runtime", "correct dpc center"),
                                                  remove_linear      = ini.get_boolean_from_ini("Runtime", "remove linear"),
                                                  do_integration     = ini.get_boolean_from_ini("Runtime", "do integration"),
                                                  calc_thickness     = ini.get_boolean_from_ini("Runtime", "calc thickness"),
                                                  remove_2nd_order   = ini.get_boolean_from_ini("Runtime", "remove 2nd order"),
                                                  material_idx       = ini.get_int_from_ini("Runtime", "material idx"))

#--------------------------------------------------------------------------------

def calculate_dpc(initialization_parameters):
    img             = initialization_parameters.get_parameter("img")
    imgRef          = initialization_parameters.get_parameter("imgRef")
    phenergy        = initialization_parameters.get_parameter("phenergy")
    pixelsize       = initialization_parameters.get_parameter("pixelsize")
    distDet2sample  = initialization_parameters.get_parameter("distDet2sample")
    period_harm     = initialization_parameters.get_parameter("period_harm")
    unwrapFlag      = True

    plotter = get_registered_plotter_instance()
    main_logger   = get_registered_logger_instance()
    script_logger = get_registered_secondary_logger()
    ini = get_registered_ini_instance()

    plotter.register_context_window(CALCULATE_DPC_CONTEXT_KEY)

    img_size_o = np.shape(img)

    if plotter.is_active():
        img, idx4crop = plotter.show_interactive_plot(CropDialogPlot, container_widget=None, img=img, pixelsize=pixelsize)
    else:
        idx4crop = ini.get_list_from_ini("Parameters", "Crop")
        img = common_tools.crop_matrix_at_indexes(img, idx4crop)

    # Plot Real Image AFTER crop
    plotter.push_plot_on_context(CALCULATE_DPC_CONTEXT_KEY, ShowCroppedFigure, img=img, pixelsize=pixelsize)

    if not imgRef is None: imgRef = common_tools.crop_matrix_at_indexes(imgRef, idx4crop)

    period_harm_Vert_o = int(period_harm[0]*img.shape[0]/img_size_o[0]) + 1
    period_harm_Hor_o = int(period_harm[1]*img.shape[1]/img_size_o[1]) + 1

    # Obtain harmonic periods from images

    if imgRef is None:
        harmPeriod = [period_harm_Vert_o, period_harm_Hor_o]
    else:
        main_logger.print_message('Obtain harmonic 01 experimentally')

        (_, period_harm_Hor) = grating_interferometry.exp_harm_period(imgRef, [period_harm_Vert_o, period_harm_Hor_o],
                                                                      harmonic_ij=['0', '1'],
                                                                      searchRegion=30,
                                                                      isFFT=False)

        main_logger.print_message('MESSAGE: Obtain harmonic 10 experimentally')

        (period_harm_Vert, _) = grating_interferometry.exp_harm_period(imgRef, [period_harm_Vert_o, period_harm_Hor_o],
                                                                       harmonic_ij=['1', '0'],
                                                                       searchRegion=30,
                                                                       isFFT=False)

        harmPeriod = [period_harm_Vert, period_harm_Hor]

    # Calculate everything

    [int00, int01, int10,
     darkField01, darkField10,
     phaseFFT_01,
     phaseFFT_10] = grating_interferometry.single_2Dgrating_analyses(img,
                                                                     img_ref=imgRef,
                                                                     harmonicPeriod=harmPeriod,
                                                                     unwrapFlag=unwrapFlag,
                                                                     context_key=CALCULATE_DPC_CONTEXT_KEY)

    virtual_pixelsize = [0, 0]
    virtual_pixelsize[0] = pixelsize[0]*img.shape[0]/int00.shape[0]
    virtual_pixelsize[1] = pixelsize[1]*img.shape[1]/int00.shape[1]

    diffPhase01 = -phaseFFT_01*virtual_pixelsize[1]/distDet2sample/hc*phenergy
    diffPhase10 = -phaseFFT_10*virtual_pixelsize[0]/distDet2sample/hc*phenergy
    # Note: the signals above were defined base in experimental data

    plotter.draw_context_on_widget(CALCULATE_DPC_CONTEXT_KEY, container_widget=plotter.get_context_container_widget(CALCULATE_DPC_CONTEXT_KEY))

    main_logger.print_message('VALUES: virtual pixelsize i, j: {:.4f}um, {:.4f}um'.format(virtual_pixelsize[0]*1e6, virtual_pixelsize[1]*1e6))
    script_logger.print('\nvirtual_pixelsize = ' + str(virtual_pixelsize))

    wavelength = hc / phenergy

    main_logger.print_message('wavelength [m] = ' + str('{:.5g}'.format(wavelength)))
    script_logger.print('wavelength [m] = ' + str('{:.5g}'.format(wavelength)))

    lengthSensitivy100 = virtual_pixelsize[0]**2/distDet2sample/100

    # the 100 means that I arbitrarylly assumed the angular error in
    #  fringe displacement to be 2pi/100 = 3.6 deg

    main_logger.print_message('WF Length Sensitivy 100 [m] = ' + str('{:.5g}'.format(lengthSensitivy100)))
    main_logger.print_message('WF Length Sensitivy 100 [1/lambda] = ' + str('{:.5g}'.format(lengthSensitivy100/wavelength)) + '\n')

    script_logger.print('WF Length Sensitivy 100 [m] = ' + str('{:.5g}'.format(lengthSensitivy100)))
    script_logger.print('WF Length Sensitivy 100 [1/lambda] = ' + str('{:.5g}'.format(lengthSensitivy100/wavelength)) + '\n')

    return WavePyData(int00=int00,
                      int01=int01,
                      int10=int10,
                      darkField01=darkField01,
                      darkField10=darkField10,
                      diffPhase01=diffPhase01,
                      diffPhase10=diffPhase10,
                      virtual_pixelsize=virtual_pixelsize)

#--------------------------------------------------------------------------------

def recrop_dpc(dpc_result, initialization_parameters):
    img             = initialization_parameters.get_parameter("img")
    imgRef          = initialization_parameters.get_parameter("imgRef")
    pixelsize       = initialization_parameters.get_parameter("pixelsize")

    int00             = dpc_result.get_parameter("int00")
    int01             = dpc_result.get_parameter("int01")
    int10             = dpc_result.get_parameter("int10")
    darkField01       = dpc_result.get_parameter("darkField01")
    darkField10       = dpc_result.get_parameter("darkField10")
    diffPhase01       = dpc_result.get_parameter("diffPhase01")
    diffPhase10       = dpc_result.get_parameter("diffPhase10")
    virtual_pixelsize = dpc_result.get_parameter("virtual_pixelsize")

    plotter = get_registered_plotter_instance()
    main_logger   = get_registered_logger_instance()
    ini = get_registered_ini_instance()

    plotter.register_context_window(RECROP_DPC_CONTEXT_KEY)

    img_to_crop = np.sqrt((diffPhase01 - diffPhase01.mean())**2 + (diffPhase10 - diffPhase10.mean())**2)

    if plotter.is_active(): _, idx2ndCrop = plotter.show_interactive_plot(SecondCropDialogPlot, container_widget=None, img=img_to_crop, pixelsize=pixelsize)
    else: idx2ndCrop = ini.get_list_from_ini("Parameters", "Crop")

    if idx2ndCrop != [0, -1, 0, -1]:
        int00 = common_tools.crop_matrix_at_indexes(int00, idx2ndCrop)
        int01 = common_tools.crop_matrix_at_indexes(int01, idx2ndCrop)
        int10 = common_tools.crop_matrix_at_indexes(int10, idx2ndCrop)
        darkField01 = common_tools.crop_matrix_at_indexes(darkField01, idx2ndCrop)
        darkField10 = common_tools.crop_matrix_at_indexes(darkField10, idx2ndCrop)
        diffPhase01 = common_tools.crop_matrix_at_indexes(diffPhase01, idx2ndCrop)
        diffPhase10 = common_tools.crop_matrix_at_indexes(diffPhase10, idx2ndCrop)

        factor_i = virtual_pixelsize[0]/pixelsize[0]
        factor_j = virtual_pixelsize[1]/pixelsize[1]

        idx1stCrop = ini.get_list_from_ini("Parameters", "Crop")

        idx4crop = [0, -1, 0, -1]
        idx4crop[0] = int(np.rint(idx1stCrop[0] + idx2ndCrop[0]*factor_i))
        idx4crop[1] = int(np.rint(idx1stCrop[0] + idx2ndCrop[1]*factor_i))
        idx4crop[2] = int(np.rint(idx1stCrop[2] + idx2ndCrop[2]*factor_j))
        idx4crop[3] = int(np.rint(idx1stCrop[2] + idx2ndCrop[3]*factor_j))

        main_logger.print('New Crop: {}, {}, {}, {}'.format(idx4crop[0], idx4crop[1], idx4crop[2], idx4crop[3]))

        ini.set_list_at_ini("Parameters", "Crop", idx4crop)

        # Plot Real Image AFTER crop
        plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, ShowCroppedFigure, img=common_tools.crop_matrix_at_indexes(img, idx4crop), pixelsize=pixelsize, title="Raw Image with 2nd Crop")

        ini.push()

    if not imgRef is None:
        plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, PlotIntensitiesHarms, int00=int00, int01=int01, int10=int10, pixelsize=virtual_pixelsize, titleStr='Intensity')
        plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, PlotDarkField, darkField01=darkField01, darkField10=darkField10, pixelsize=virtual_pixelsize)

    plotter.push_plot_on_context(RECROP_DPC_CONTEXT_KEY, PlotDPC, dpc01=diffPhase01, dpc10=diffPhase10, pixelsize=virtual_pixelsize, titleStr="")

    plotter.draw_context_on_widget(RECROP_DPC_CONTEXT_KEY, container_widget=plotter.get_context_container_widget(RECROP_DPC_CONTEXT_KEY))

    return WavePyData(int00=int00,
                      int01=int01,
                      int10=int10,
                      darkField01=darkField01,
                      darkField10=darkField10,
                      diffPhase01=diffPhase01,
                      diffPhase10=diffPhase10,
                      virtual_pixelsize=virtual_pixelsize)

#--------------------------------------------------------------------------------

def correct_zero_dpc(dpc_result, initialization_parameters):
    dpc01              = dpc_result.get_parameter("diffPhase01")
    dpc10              = dpc_result.get_parameter("diffPhase10")
    virtual_pixelsize  = dpc_result.get_parameter("virtual_pixelsize")

    phenergy           = initialization_parameters.get_parameter("phenergy")
    pixelsize          = initialization_parameters.get_parameter("pixelsize")
    distDet2sample     = initialization_parameters.get_parameter("distDet2sample")
    correct_pi_jump    = initialization_parameters.get_parameter("correct_pi_jump")
    remove_mean        = initialization_parameters.get_parameter("remove_mean")
    correct_dpc_center = initialization_parameters.get_parameter("correct_dpc_center")

    plotter       = get_registered_plotter_instance()
    main_logger   = get_registered_logger_instance()
    script_logger = get_registered_secondary_logger()

    plotter.register_context_window(CORRECT_ZERO_DPC)

    def __get_pi_jump(angle_i):
        return int(np.round(np.mean(angle_i / np.pi)))

    factor = distDet2sample*hc/phenergy
    angle = [dpc01/pixelsize[1]*factor, dpc10/pixelsize[0]*factor]
    pi_jump = [__get_pi_jump(angle[0]), __get_pi_jump(angle[1])]

    script_logger.print('Initial Hrz Mean angle/pi : {:} pi'.format(np.mean(angle[0]/np.pi)))
    script_logger.print('Initial Vt Mean angle/pi : {:} pi'.format(np.mean(angle[1]/np.pi)))

    plotter.push_plot_on_context(CORRECT_ZERO_DPC, CorrectDPC, angle=angle, pi_jump=pi_jump)

    def __get_dpc(angle_i, pixelsize_i):
        return angle_i * pixelsize_i / factor

    if not sum(pi_jump) == 0 and correct_pi_jump:
        angle[0] -= pi_jump[0] * np.pi
        angle[1] -= pi_jump[1] * np.pi

        dpc01 = __get_dpc(angle[0], pixelsize[0])
        dpc10 = __get_dpc(angle[1], pixelsize[1])

        plotter.push_plot_on_context(CORRECT_ZERO_DPC, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Correct \u03c0 jump")

    main_logger.print_message('mean angle/pi 0: {:} pi'.format(np.mean(angle[0]/np.pi)))
    main_logger.print_message('mean angle/pi 1: {:} pi'.format(np.mean(angle[1]/np.pi)))
    script_logger.print('Horz Mean angle/pi : {:} pi'.format(np.mean(angle[0]/np.pi)))
    script_logger.print('Vert Mean angle/pi : {:} pi'.format(np.mean(angle[1]/np.pi)))

    if remove_mean:
        angle[0] -= np.mean(angle[0])
        angle[1] -= np.mean(angle[1])

        dpc01 = __get_dpc(angle[0], pixelsize[0])
        dpc10 = __get_dpc(angle[1], pixelsize[1])

        plotter.push_plot_on_context(CORRECT_ZERO_DPC, CorrectDPCHistos, angle=angle, title="Remove mean")
        plotter.push_plot_on_context(CORRECT_ZERO_DPC, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Remove Mean")

    if correct_dpc_center and plotter.is_active():
        angle = plotter.show_interactive_plot(CorrectDPCCenter, container_widget=None, angle=angle)
        #angle[1] = plotter.show_interactive_plot(CorrectDPCCenter, container_widget=None, angleArray=angle[1], harmonic="10")

        dpc01 = __get_dpc(angle[0], pixelsize[0])
        dpc10 = __get_dpc(angle[1], pixelsize[1])

        plotter.push_plot_on_context(CORRECT_ZERO_DPC, CorrectDPCHistos, angle=angle, title="Correct DPC Center")
        plotter.push_plot_on_context(CORRECT_ZERO_DPC, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Correct DPC Center")

    plotter.draw_context_on_widget(CORRECT_ZERO_DPC, container_widget=plotter.get_context_container_widget(CORRECT_ZERO_DPC))

    return WavePyData(diffPhase01=dpc01, diffPhase10=dpc10, virtual_pixelsize=virtual_pixelsize)

#--------------------------------------------------------------------------------

def remove_linear_fit(correct_zero_dpc_result, initialization_parameters):
    diffPhase01        = correct_zero_dpc_result.get_parameter("diffPhase01")
    diffPhase10        = correct_zero_dpc_result.get_parameter("diffPhase10")
    virtual_pixelsize  = correct_zero_dpc_result.get_parameter("virtual_pixelsize")

    remove_linear      = initialization_parameters.get_parameter("remove_linear")

    plotter = get_registered_plotter_instance()
    ini     = get_registered_ini_instance()

    plotter.register_context_window(REMOVE_LINEAR_FIT)

    if not remove_linear:
        diffPhase01_2save = diffPhase01
        diffPhase10_2save = diffPhase10
    else:
        def __fit_lin_surfaceH(zz, pixelsize):
            xx, yy = common_tools.grid_coord(zz, pixelsize)
            argNotNAN = np.isfinite(zz)
            f = zz[argNotNAN].flatten()
            x = xx[argNotNAN].flatten()
            X_matrix = np.vstack([x, x * 0.0 + 1]).T
            beta_matrix = np.linalg.lstsq(X_matrix, f)[0]
            fit = (beta_matrix[0] * xx + beta_matrix[1])
            mask = zz * 0.0 + 1.0
            mask[~argNotNAN] = np.nan

            return fit * mask, beta_matrix

        def __fit_lin_surfaceV(zz, pixelsize):
            xx, yy = common_tools.grid_coord(zz, pixelsize)
            argNotNAN = np.isfinite(zz)
            f = zz[argNotNAN].flatten()
            y = yy[argNotNAN].flatten()
            X_matrix = np.vstack([y, y * 0.0 + 1]).T
            beta_matrix = np.linalg.lstsq(X_matrix, f)[0]
            fit = (beta_matrix[0] * yy + beta_matrix[1])
            mask = zz * 0.0 + 1.0
            mask[~argNotNAN] = np.nan

            return fit * mask, beta_matrix

        linfitDPC01, cH = __fit_lin_surfaceH(diffPhase01, virtual_pixelsize)
        linfitDPC10, cV = __fit_lin_surfaceV(diffPhase10, virtual_pixelsize)

        ini.set_list_at_ini('Parameters','lin fitting coef cH', cH)
        ini.set_list_at_ini('Parameters','lin fitting coef cV', cV)
        ini.push()

        diffPhase01_2save = diffPhase01 - linfitDPC01
        diffPhase10_2save = diffPhase10 - linfitDPC10

        plotter.push_plot_on_context(REMOVE_LINEAR_FIT, PlotDPC, dpc01=linfitDPC01,       dpc10=linfitDPC10,       pixelsize=virtual_pixelsize, titleStr="Linear DPC Component")
        plotter.push_plot_on_context(REMOVE_LINEAR_FIT, PlotDPC, dpc01=diffPhase01_2save, dpc10=diffPhase10_2save, pixelsize=virtual_pixelsize, titleStr="(removed linear DPC component)")

    plotter.draw_context_on_widget(REMOVE_LINEAR_FIT, container_widget=plotter.get_context_container_widget(REMOVE_LINEAR_FIT))

    return WavePyData(diffPhase01=diffPhase01_2save, diffPhase10=diffPhase10_2save, virtual_pixelsize=virtual_pixelsize)


def dpc_profile_analysis(remove_linear_fit_result, initialization_parameters):
    pass

'''
        fnameH = wpu.get_unique_filename(saveFileSuf + '_dpc_X', 'sdf')
        fnameV = wpu.get_unique_filename(saveFileSuf + '_dpc_Y', 'sdf')

        wpu.save_sdf_file(diffPhase01_2save, virtual_pixelsize,
                          fnameH, {'Title': 'DPC 01', 'Zunit': 'rad'})

        wpu.save_sdf_file(diffPhase10_2save, virtual_pixelsize,
                          fnameV, {'Title': 'DPC 10', 'Zunit': 'rad'})

        projectionFromDiv = 1.0
        wpu.log_this('projectionFromDiv : ' + str('{:.4f}'.format(projectionFromDiv)))

        # remove2ndOrder = False #easyqt.get_yes_or_no('Remove 2nd Order for Profile?')

        # WG: note that the function dpc_profile_analysis is in defined in
        # the file dpc_profile_analysis.py, which need to be in the same folder
        # than this script

        dpc_profile_analysis(None, fnameV,
                             phenergy, grazing_angle=0,
                             projectionFromDiv=projectionFromDiv,
                             remove1stOrderDPC=False,
                             remove2ndOrder=False,
                             nprofiles=5, filter_width=50)
'''

def fit_radius_dpc(correct_zero_dpc_result, initialization_parameters):
    pass

'''
def fit_radius_dpc(dpx, dpy, pixelsize, kwave,
                   saveFigFlag=False, str4title=''):

    xVec = wpu.realcoordvec(dpx.shape[1], pixelsize[1])
    yVec = wpu.realcoordvec(dpx.shape[0], pixelsize[0])

    xmatrix, ymatrix = np.meshgrid(xVec, yVec)

    fig = plt.figure(figsize=(14, 5))
    fig.suptitle(str4title + 'Phase [rad]', fontsize=14)

    ax1 = plt.subplot(121)
    ax2 = plt.subplot(122, sharex=ax1, sharey=ax1)

    ax1.plot(xVec*1e6, dpx[dpx.shape[0]//4, :],
             '-ob', label='1/4')
    ax1.plot(xVec*1e6, dpx[dpx.shape[0]//4*3, :],
             '-og', label='3/4')
    ax1.plot(xVec*1e6, dpx[dpx.shape[0]//2, :],
             '-or', label='1/2')

    lin_fitx = np.polyfit(xVec,
                          dpx[dpx.shape[0]//2, :], 1)
    lin_funcx = np.poly1d(lin_fitx)
    ax1.plot(xVec*1e6, lin_funcx(xVec),
             '--c', lw=2,
             label='Fit 1/2')
    curvrad_x = kwave/(lin_fitx[0])

    wpu.print_blue('lin_fitx[0] x: {:.3g} m'.format(lin_fitx[0]))
    wpu.print_blue('lin_fitx[1] x: {:.3g} m'.format(lin_fitx[1]))

    wpu.print_blue('Curvature Radius of WF x: {:.3g} m'.format(curvrad_x))

    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 1))
    ax1.set_xlabel(r'[$\mu m$]')
    ax1.set_ylabel('dpx [radians]')
    ax1.legend(loc=0, fontsize='small')
    ax1.set_title('Curvature Radius of WF {:.3g} m'.format(curvrad_x),
                  fontsize=16)
    # ax1.set_adjustable('box-forced')
    ax1.set_adjustable('box')

    ax2.plot(yVec*1e6, dpy[:, dpy.shape[1]//4],
             '-ob', label='1/4')
    ax2.plot(yVec*1e6, dpy[:, dpy.shape[1]//4*3],
             '-og', label='3/4')
    ax2.plot(yVec*1e6, dpy[:, dpy.shape[1]//2],
             '-or', label='1/2')

    lin_fity = np.polyfit(yVec,
                          dpy[:, dpy.shape[1]//2], 1)
    lin_funcy = np.poly1d(lin_fity)
    ax2.plot(yVec*1e6, lin_funcy(yVec),
             '--c', lw=2,
             label='Fit 1/2')
    curvrad_y = kwave/(lin_fity[0])
    wpu.print_blue('Curvature Radius of WF y: {:.3g} m'.format(curvrad_y))

    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 1))
    ax2.set_xlabel(r'[$\mu m$]')
    ax2.set_ylabel('dpy [radians]')
    ax2.legend(loc=0, fontsize='small')
    ax2.set_title('Curvature Radius of WF {:.3g} m'.format(curvrad_y),
                  fontsize=16)
    # ax2.set_adjustable('box-forced')
    ax2.set_adjustable('box')

    if saveFigFlag:
        wpu.save_figs_with_idx(saveFileSuf, extension='png')
    plt.show(block=True)

'''
