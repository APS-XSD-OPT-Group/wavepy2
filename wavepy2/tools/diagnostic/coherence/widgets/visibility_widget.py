from matplotlib.figure import Figure
from wavepy2.util.plot.plotter import WavePyWidget

from warnings import filterwarnings
filterwarnings("ignore")

class VisibilityPlot(WavePyWidget):
    def __init__(self, parent=None, application_name=None, **kwargs):
        WavePyWidget.__init__(self, parent=parent, application_name=application_name)

    def get_plot_tab_name(self): return "Visibility vs detector distance"

    def build_mpl_figure(self, **kwargs):
        zvec      = kwargs["zvec"]
        contrastV = kwargs["contrastV"]
        contrastH = kwargs["contrastH"]

        # contrast vs z
        figure = Figure(figsize=(10, 7))
        figure.gca().plot(zvec * 1e3, contrastV * 100, '-ko', label='Vert')
        figure.gca().plot(zvec * 1e3, contrastH * 100, '-ro', label='Hor')
        figure.gca().set_xlabel(r'Distance $z$  [mm]', fontsize=14)
        figure.gca().set_ylabel(r'Visibility $\times$ 100 [%]', fontsize=14)
        figure.gca().set_title('Visibility vs detector distance', fontsize=14, weight='bold')
        figure.gca().legend(fontsize=14, loc=7)

        return figure
