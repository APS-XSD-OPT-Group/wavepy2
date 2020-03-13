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

from wavepy2.util.plot.plotter import WavePyWidget
from wavepy2.util.common import common_tools

from matplotlib.patches import Rectangle
from matplotlib.figure import Figure

class CropDialogPlot(WavePyWidget):
    def get_plot_tab_name(self):
        return "Crop Plot"

    def build_figure(self, **kwargs):
        img         = kwargs["img"]
        saveFigFlag = kwargs["saveFigFlag"]

        # take index from ini file
        idx4crop = list(map(int, (wpu.get_from_ini_file(inifname, 'Parameters', 'Crop').split(','))))

        wpu.print_red(idx4crop)

        # Plot Real Image wiht default crop

        tmpImage = wpu.crop_matrix_at_indexes(img, idx4crop)

        plt.figure()
        plt.imshow(tmpImage,
                   cmap='viridis',
                   extent=wpu.extent_func(tmpImage, pixelsize)*1e6)
        plt.xlabel(r'$[\mu m]$')
        plt.ylabel(r'$[\mu m]$')
        plt.colorbar()

        plt.title('Raw Image with initial Crop', fontsize=18, weight='bold')

        plt.show(block=False)
        plt.pause(.5)
        # ask if the crop need to be changed
        newCrop = gui_mode and easyqt.get_yes_or_no('New Crop?')

        if saveFigFlag and not newCrop:
            wpu.save_figs_with_idx(saveFileSuf)

        plt.close(plt.gcf())

        if newCrop:

            [colorlimit,
             cmap] = wpu.plot_slide_colorbar(img,
                                             title='SELECT COLOR SCALE,\n' +
                                             'Raw Image, No Crop',
                                             xlabel=r'x [$\mu m$ ]',
                                             ylabel=r'y [$\mu m$ ]',
                                             extent=wpu.extent_func(img,
                                                                    pixelsize)*1e6)

            cmap2crop = plt.cm.get_cmap(cmap)
            cmap2crop.set_over('#FF0000')
            cmap2crop.set_under('#8B008B')
            idx4crop = wpu.graphical_roi_idx(img, verbose=True,
                                             kargs4graph={'cmap': cmap,
                                                          'vmin': colorlimit[0],
                                                          'vmax': colorlimit[1]})

            cmap2crop.set_over(cmap2crop(1))  # Reset Colorbar
            cmap2crop.set_under(cmap2crop(cmap2crop.N-1))

            wpu.set_at_ini_file(inifname, 'Parameters', 'Crop',
                                '{}, {}, {}, {}'.format(idx4crop[0], idx4crop[1],
                                                        idx4crop[2], idx4crop[3]))

            img = wpu.crop_matrix_at_indexes(img, idx4crop)

            # Plot Real Image AFTER crop

            plt.imshow(img, cmap='viridis',
                       extent=wpu.extent_func(img, pixelsize)*1e6)
            plt.xlabel(r'$[\mu m]$')
            plt.ylabel(r'$[\mu m]$')
            plt.colorbar()
            plt.title('Raw Image with New Crop', fontsize=18, weight='bold')

            if saveFigFlag:
                wpu.save_figs_with_idx(saveFileSuf)
            plt.show(block=True)

        else:
            img = tmpImage

        return img, idx4crop
