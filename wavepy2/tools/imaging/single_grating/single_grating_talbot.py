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
from wavepy2.tools.imaging.single_grating.widgets.correct_DPC import CorrectDPC, CorrectDPCSubtractMean, CorrectZeroFromUnwrap


from scipy import constants

hc = constants.value('inverse meter-electron volt relationship')  # hc

CALCULATE_DPC_CONTEXT_KEY = "Calculate DPC"
RECROP_DPC_CONTEXT_KEY = "Recrop DPC"
CORRECT_ZERO_DPC = "Correct Zero DPC"

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
    ini           = get_registered_ini_instance()

    plotter.register_context_window(CORRECT_ZERO_DPC)

    factor = distDet2sample*hc/phenergy

    angle = [dpc01/pixelsize[1]*factor, dpc10/pixelsize[0]*factor]
    dpc   = [dpc01, dpc10]

    script_logger.print('Initial Hrz Mean angle/pi : {:} pi'.format(np.mean(angle[0]/np.pi)))
    script_logger.print('Initial Vt Mean angle/pi : {:} pi'.format(np.mean(angle[1]/np.pi)))

    pi_jump = [int(np.round(np.mean(angle[0] / np.pi))),
               int(np.round(np.mean(angle[1] / np.pi)))]

    plotter.push_plot_on_context(CORRECT_ZERO_DPC, CorrectDPC, angle=angle, pi_jump=pi_jump)

    if not sum(pi_jump) == 0 and correct_pi_jump:
        angle[0] -= pi_jump[0] * np.pi
        angle[1] -= pi_jump[1] * np.pi

        dpc01 = angle[0] * pixelsize[0] / factor
        dpc10 = angle[1] * pixelsize[1] / factor

        dpc = [dpc01, dpc10]

        plotter.push_plot_on_context(CORRECT_ZERO_DPC, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Correct \u03c0 jump")

    main_logger.print_message('mean angle/pi 0: {:} pi'.format(np.mean(angle[0]/np.pi)))
    main_logger.print_message('mean angle/pi 1: {:} pi'.format(np.mean(angle[1]/np.pi)))
    script_logger.print('Horz Mean angle/pi : {:} pi'.format(np.mean(angle[0]/np.pi)))
    script_logger.print('Vert Mean angle/pi : {:} pi'.format(np.mean(angle[1]/np.pi)))

    if remove_mean:
        angle[0] -= np.mean(angle[0])
        angle[1] -= np.mean(angle[1])

        dpc01 = angle[0]*pixelsize[0]/factor
        dpc10 = angle[1]*pixelsize[1]/factor

        dpc = [dpc01, dpc10]

        plotter.push_plot_on_context(CORRECT_ZERO_DPC, CorrectDPCSubtractMean, angle=angle)
        plotter.push_plot_on_context(CORRECT_ZERO_DPC, PlotDPC, dpc01=dpc01, dpc10=dpc10, pixelsize=virtual_pixelsize, titleStr="Remove Mean")

    if correct_dpc_center and plotter.is_active():
        for i in [0, 1]:
            iamhappy = False
            while not iamhappy:
                angle[i], pi_jump[i] = plotter.show_interactive_plot(CorrectZeroFromUnwrap, container_widget=None, angleArray=angle[i])

                #iamhappy = plotter.show_interactive_plot(CorrectDPCCenter, container_widget=None, angle=angle[i], pi_jump=pi_jump[i])

    plotter.draw_context_on_widget(CORRECT_ZERO_DPC, container_widget=plotter.get_context_container_widget(CORRECT_ZERO_DPC))

    return WavePyData(dpc=dpc)

'''
def correct_zero_DPC(dpc01, dpc10,
                     pixelsize, distDet2sample, phenergy, saveFileSuf,
                     correct_pi_jump=False, remove_mean=False,
                     saveFigFlag=True):

    title = ['Angle displacement of fringes 01',
             'Angle displacement of fringes 10']

    factor = distDet2sample*hc/phenergy

    angle = [dpc01/pixelsize[1]*factor, dpc10/pixelsize[0]*factor]
    dpc   = [dpc01, dpc10]

    wpu.log_this('Initial Hrz Mean angle/pi ' +
                 ': {:} pi'.format(np.mean(angle[0]/np.pi)))

    wpu.log_this('Initial Vt Mean angle/pi ' +
                 ': {:} pi'.format(np.mean(angle[1]/np.pi)))

    while True:

        pi_jump = [0, 0]

        pi_jump[0] = int(np.round(np.mean(angle[0]/np.pi)))
        pi_jump[1] = int(np.round(np.mean(angle[1]/np.pi)))

        plt.figure()
        h1 = plt.hist(angle[0].flatten()/np.pi, 201,
                      histtype='step', linewidth=2)
        h2 = plt.hist(angle[1].flatten()/np.pi, 201,
                      histtype='step', linewidth=2)

        plt.xlabel(r'Angle [$\pi$rad]')
        if pi_jump == [0, 0]:
            lim = np.ceil(np.abs((h1[1][0], h1[1][-1],
                                  h2[1][0], h2[1][-1])).max())
            plt.xlim([-lim, lim])

        plt.title('Correct DPC\n' +
                  r'Angle displacement of fringes $[\pi$ rad]' +
                  '\n' + r'Calculated jumps $x$ and $y$ : ' +
                  '{:d}, {:d} $\pi$'.format(pi_jump[0], pi_jump[1]))

        plt.legend(('DPC x', 'DPC y'))
        plt.tight_layout()
        if saveFigFlag:
                    wpu.save_figs_with_idx(saveFileSuf)
        plt.show(block=False)
        plt.pause(.5)

        if pi_jump == [0, 0]:
            break

        if (gui_mode and easyqt.get_yes_or_no('Subtract pi jump of DPC?') or
           correct_pi_jump):

            angle[0] -= pi_jump[0]*np.pi
            angle[1] -= pi_jump[1]*np.pi

            dpc01 = angle[0]*pixelsize[0]/factor
            dpc10 = angle[1]*pixelsize[1]/factor
            dpc = [dpc01, dpc10]

            wgi.plot_DPC(dpc01, dpc10,
                         virtual_pixelsize, saveFigFlag=saveFigFlag,
                         saveFileSuf=saveFileSuf)
            plt.show(block=False)

        else:
            break

    wpu.print_blue('MESSAGE: mean angle/pi ' +
                   '0: {:} pi'.format(np.mean(angle[0]/np.pi)))
    wpu.print_blue('MESSAGE: mean angle/pi ' +
                   '1: {:} pi'.format(np.mean(angle[1]/np.pi)))

    wpu.log_this('Horz Mean angle/pi ' +
                 ': {:} pi'.format(np.mean(angle[0]/np.pi)))

    wpu.log_this('Vert Mean angle/pi ' +
                 ': {:} pi'.format(np.mean(angle[1]/np.pi)))

    #    if easyqt.get_yes_or_no('Subtract mean of DPC?'):
    if (gui_mode and easyqt.get_yes_or_no('Subtract mean of DPC?') or
       remove_mean):

        wpu.log_this('%%% COMMENT: Subtrated mean value of DPC',
                     saveFileSuf)

        angle[0] -= np.mean(angle[0])
        angle[1] -= np.mean(angle[1])

        dpc01 = angle[0]*pixelsize[0]/factor
        dpc10 = angle[1]*pixelsize[1]/factor
        dpc = [dpc01, dpc10]

        plt.figure()
        plt.hist(angle[0].flatten()/np.pi, 201,
                 histtype='step', linewidth=2)
        plt.hist(angle[1].flatten()/np.pi, 201,
                 histtype='step', linewidth=2)

        plt.xlabel(r'Angle [$\pi$rad]')

        plt.title('Correct DPC\n' +
                  r'Angle displacement of fringes $[\pi$ rad]')

        plt.legend(('DPC x', 'DPC y'))
        plt.tight_layout()
        if saveFigFlag:
                    wpu.save_figs_with_idx(saveFileSuf)
        plt.show(block=False)
        plt.pause(.5)

        wgi.plot_DPC(dpc01, dpc10,
                     virtual_pixelsize, saveFigFlag=saveFigFlag,
                     saveFileSuf=saveFileSuf)
        plt.show(block=True)
        plt.pause(.1)
    else:
        pass

    if gui_mode and easyqt.get_yes_or_no('Correct DPC center?'):

        wpu.log_this('%%% COMMENT: DCP center is corrected',
                     saveFileSuf)

        for i in [0, 1]:

            iamhappy = False
            while not iamhappy:

                angle[i], pi_jump[i] = correct_zero_from_unwrap(angle[i])

                wpu.print_blue('MESSAGE: pi jump ' +
                               '{:}: {:} pi'.format(i, pi_jump[i]))
                wpu.print_blue('MESSAGE: mean angle/pi ' +
                               '{:}: {:} pi'.format(i, np.mean(angle[i]/np.pi)))
                plt.figure()
                plt.hist(angle[i].flatten() / np.pi, 101,
                         histtype='step', linewidth=2)
                plt.title(r'Angle displacement of fringes $[\pi$ rad]')

                if saveFigFlag:
                    wpu.save_figs_with_idx(saveFileSuf)
                plt.show()

                plt.figure()

                vlim = np.max((np.abs(wpu.mean_plus_n_sigma(angle[i]/np.pi,
                                                            -5)),
                               np.abs(wpu.mean_plus_n_sigma(angle[i]/np.pi,
                                                            5))))

                plt.imshow(angle[i] / np.pi,
                           cmap='RdGy',
                           vmin=-vlim, vmax=vlim)

                plt.colorbar()
                plt.title(title[i] + r' [$\pi$ rad],')
                plt.xlabel('Pixels')
                plt.ylabel('Pixels')

                plt.pause(.1)

                iamhappy = easyqt.get_yes_or_no('Happy?')

            dpc[i] = angle[i]*pixelsize[i]/factor

    return dpc


'''
