from wavepy2.util.common import common_tools
from wavepy2.util.plot.plotter import get_registered_plotter_instance
from wavepy2.util.plot.plot_tools import PlottingProperties
from wavepy2.util.ini.initializer import get_registered_ini_instance

from wavepy2.tools.common.widgets.crop_widget import CropDialogPlot, CropWidgetPlot
from wavepy2.tools.common.widgets.colorbar_crop_widget import ColorbarCropDialogPlot, ColorbarCropWidgetPlot

CROP_KEY          = "Crop Key"
COLORBAR_CROP_KEY = "Colorbar Crop Key"


def draw_crop_image(img, initialization_parameters, plotting_properties=PlottingProperties()):
    plotter = get_registered_plotter_instance()

    if plotter.is_active():
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = plotter.register_context_window(CROP_KEY,
                                                    context_window=plotting_properties.get_context_widget(),
                                                    use_unique_id=use_unique_id)

        plotter.push_plot_on_context(CROP_KEY, CropWidgetPlot, unique_id, img=img)
        plotter.draw_context(CROP_KEY, add_context_label=add_context_label, unique_id=unique_id)

        return plotter.get_plots_of_context(CROP_KEY, unique_id=unique_id)
    else:
        return None

def crop_image(img, pixelsize, initialization_parameters, plotting_properties=PlottingProperties()):
    plotter = get_registered_plotter_instance()
    ini     = get_registered_ini_instance()

    if plotter.is_active():
        img, idx4crop, img_size_o, _, _ = plotter.show_interactive_plot(ColorbarCropDialogPlot,
                                                                        container_widget=plotting_properties.get_container_widget(),
                                                                        img=img, pixelsize=pixelsize)
    else:
        img_size_o = np.shape(img)
        idx4crop = ini.get_list_from_ini("Parameters", "Crop")
        img = common_tools.crop_matrix_at_indexes(img, idx4crop)

    return img, idx4crop, img_size_o


def draw_colorbar_crop_image(img, pixelsize, initialization_parameters, plotting_properties=PlottingProperties()):
    plotter = get_registered_plotter_instance()

    if plotter.is_active():
        add_context_label = plotting_properties.get_parameter("add_context_label", True)
        use_unique_id = plotting_properties.get_parameter("use_unique_id", False)

        unique_id = plotter.register_context_window(COLORBAR_CROP_KEY,
                                                    context_window=plotting_properties.get_context_widget(),
                                                    use_unique_id=use_unique_id)

        plotter.push_plot_on_context(COLORBAR_CROP_KEY, ColorbarCropWidgetPlot, unique_id, img=img, pixelsize=pixelsize)
        plotter.draw_context(COLORBAR_CROP_KEY, add_context_label=add_context_label, unique_id=unique_id)

        return plotter.get_plots_of_context(COLORBAR_CROP_KEY, unique_id=unique_id)
    else:
        return None

def colorbar_crop_image(img, pixelsize, initialization_parameters, plotting_properties=PlottingProperties()):
    plotter = get_registered_plotter_instance()
    ini     = get_registered_ini_instance()

    if plotter.is_active():
        img, idx4crop, img_size_o, _, _ = plotter.show_interactive_plot(ColorbarCropDialogPlot,
                                                                        container_widget=plotting_properties.get_container_widget(),
                                                                        img=img, pixelsize=pixelsize)
    else:
        img_size_o = np.shape(img)
        idx4crop = ini.get_list_from_ini("Parameters", "Crop")
        img = common_tools.crop_matrix_at_indexes(img, idx4crop)

    return img, idx4crop, img_size_o
