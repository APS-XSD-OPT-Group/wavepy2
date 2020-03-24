import numpy as np
from matplotlib.figure import Figure
from wavepy2.util.common.common_tools import extent_func
from wavepy2.util.plot.plotter import WavePyWidget

class SingleGratingHarmonicImages(WavePyWidget):
    def get_plot_tab_name(self): return "Intensity in Fourier Space"

    def build_mpl_figure(self, **kwargs):
        # Intensity is Fourier Space
        intFFT00 = np.log10(np.abs(kwargs["imgFFT00"]))
        intFFT01 = np.log10(np.abs(kwargs["imgFFT01"]))
        intFFT10 = np.log10(np.abs(kwargs["imgFFT10"]))

        figure = Figure(figsize=(14, 5))
        axes = figure.subplots(nrows=1, ncols=3)

        for dat, ax, textTitle in zip([intFFT00, intFFT01, intFFT10],
                                      axes.flat,
                                      ['FFT 00', 'FFT 01', 'FFT 10']):

            # The vmin and vmax arguments specify the color limits
            im = ax.imshow(dat, cmap='inferno', vmin=np.min(intFFT00),
                           vmax=np.max(intFFT00),
                           extent=extent_func(dat))

            ax.set_title(textTitle)
            if textTitle == 'FFT 00': ax.set_ylabel('Pixels')
            ax.set_xlabel('Pixels')

        # Make an axis for the colorbar on the right side
        figure.colorbar(im, cax=figure.add_axes([0.92, 0.1, 0.03, 0.8]))
        figure.suptitle('FFT subsets - Intensity', fontsize=18, weight='bold')

        return figure
