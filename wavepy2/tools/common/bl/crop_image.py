import numpy as np

from wavepy2.util.common import common_tools
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.plot.plot_tools import PlottingProperties
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.widgets.crop_widget import CropDialogPlot, CropWidgetPlot
from wavepy2.tools.common.widgets.colorbar_crop_widget import ColorbarCropDialogPlot, ColorbarCropWidgetPlot

CROP_KEY          = "Crop Key"
COLORBAR_CROP_KEY = "Colorbar Crop Key"


def draw_crop_image(img, context_key=CROP_KEY, plotting_properties=PlottingProperties(), application_name=None, **kwargs):
    plotter = get_registered_plotter_instance(application_name=application_name)

    if plotter.is_active():
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id     = plotting_properties.get_parameter("use_unique_id", False)


        unique_id = plotter.register_context_window(context_key,
                                                    context_window=plotting_properties.get_context_widget(),
                                                    use_unique_id=use_unique_id)

        plotter.push_plot_on_context(context_key, CropWidgetPlot, unique_id, img=img, **kwargs)
        plotter.draw_context(context_key, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return plotter.get_plots_of_context(context_key, unique_id=unique_id)
    else:
        return None

def crop_image(img, plotting_properties=PlottingProperties(), application_name=None, **kwargs):
    plotter = get_registered_plotter_instance(application_name=application_name)

    if plotter.is_active():
        img, idx4crop, img_size_o = plotter.show_interactive_plot(CropDialogPlot,
                                                                  container_widget=plotting_properties.get_container_widget(),
                                                                  img=img, **kwargs)
    else:
        ini = get_registered_ini_instance(application_name=application_name)

        img_size_o = np.shape(img)
        idx4crop   = ini.get_list_from_ini("Parameters", "Crop")
        img        = common_tools.crop_matrix_at_indexes(img, idx4crop)

    return img, idx4crop, img_size_o


def draw_colorbar_crop_image(img, pixelsize, context_key=COLORBAR_CROP_KEY, plotting_properties=PlottingProperties(), application_name=None, **kwargs):
    plotter = get_registered_plotter_instance(application_name=application_name)

    if plotter.is_active():
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = plotter.register_context_window(context_key,
                                                    context_window=plotting_properties.get_context_widget(),
                                                    use_unique_id=use_unique_id)

        plotter.push_plot_on_context(context_key, ColorbarCropWidgetPlot, unique_id, img=img, pixelsize=pixelsize, **kwargs)
        plotter.draw_context(context_key, add_context_label=add_context_label, unique_id=unique_id, **kwargs)

        return plotter.get_plots_of_context(context_key, unique_id=unique_id)
    else:
        return None

def colorbar_crop_image(img, pixelsize, plotting_properties=PlottingProperties(), application_name=None, **kwargs):
    plotter = get_registered_plotter_instance(application_name=application_name)

    if plotter.is_active():
        img, idx4crop, img_size_o, cmap, clim = plotter.show_interactive_plot(ColorbarCropDialogPlot,
                                                                              container_widget=plotting_properties.get_container_widget(),
                                                                              img=img, pixelsize=pixelsize, **kwargs)
    else:
        ini = get_registered_ini_instance(application_name=application_name)

        img_size_o = np.shape(img)
        idx4crop = ini.get_list_from_ini("Parameters", "Crop")
        img = common_tools.crop_matrix_at_indexes(img, idx4crop)
        cmap = None
        clim = None

    return img, idx4crop, img_size_o, cmap, clim
