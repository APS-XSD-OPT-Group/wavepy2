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
import sys

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtCore import QRect



##########################################################################
# WIDGET FOR SCRIPTING

def set_screen_at_center(window):
    qtRectangle = window.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()

    print(centerPoint)
    qtRectangle.moveCenter(centerPoint)
    window.move(qtRectangle.topLeft())
    window.update()

class DefaultMainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.__container_widget = QWidget()
        self.setCentralWidget(self.__container_widget)

        desktop_widget = QDesktopWidget()
        actual_geometry = self.frameGeometry()
        screen_geometry = desktop_widget.availableGeometry()
        new_geometry = QRect()
        new_geometry.setWidth(actual_geometry.width())
        new_geometry.setHeight(actual_geometry.height())
        new_geometry.setTop(screen_geometry.height()*0.05)
        new_geometry.setLeft(screen_geometry.width()*0.05)

        self.setGeometry(new_geometry)

    def get_container_widget(self):
        return self.__container_widget

##########################################################################
# COMMON WIDGETS

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget

from matplotlib.figure import Figure
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from wavepy2.util.common import common_tools

FIXED_WIDTH = 800

class SimplePlot(QWidget):
    def __init__(self, parent, image, title='', xlabel='', ylabel='', **kwargs4imshow):
        super(SimplePlot, self).__init__(parent)

        self.setFixedWidth(FIXED_WIDTH)

        figure_canvas = FigureCanvas(Figure())
        mpl_figure = figure_canvas.figure

        ax = mpl_figure.subplots(1, 1)
        mpl_image = ax.imshow(image, cmap='viridis', **kwargs4imshow)
        mpl_image.cmap.set_over('#FF0000')  # Red
        mpl_image.cmap.set_under('#8B008B')  # Light Cyan

        ax.set_title(title, fontsize=18, weight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        mpl_figure.colorbar(mpl_image, ax=ax, orientation="vertical")

        self.__image_to_change = ImageToChange(mpl_image=mpl_image, mpl_figure=mpl_figure)

        layout = QVBoxLayout()
        layout.addWidget(figure_canvas)
        layout.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)

    def get_image_to_change(self):
        return self.__image_to_change

class ImageToChange(object):
    def __init__(self, mpl_image, mpl_figure):
        self.__mpl_image = mpl_image
        self.__mpl_figure = mpl_figure

        self.__mpl_data = self.__mpl_image.get_array().data.astype(float)
        self.__cmin_o   = self.__mpl_image.get_clim()[0]
        self.__cmax_o   = self.__mpl_image.get_clim()[1]

    def get_mpl_data(self):
        return self.__mpl_data

    def get_mpl_image(self):
        return self.__mpl_image

    def get_mpl_figure(self):
        return self.__mpl_figure

    def get_cmin_o(self):
        return self.__cmin_o

    def get_cmax_o(self):
        return self.__cmax_o

class FigureSlideColorbar(QWidget):
    def __init__(self, parent, image, title='', xlabel='', ylabel='', cmin_o=None, cmax_o=None, **kwargs4imshow):
        super(FigureSlideColorbar, self).__init__(parent)

        __radio1_values = ['gray', 'gray_r', 'viridis', 'viridis_r', 'inferno', 'rainbow', 'RdGy_r']
        __radio2_values = ['lin', 'pow 1/7', 'pow 1/3', 'pow 3', 'pow 7']
        __radio3_values = ['none', 'sigma = 1', 'sigma = 3', 'sigma = 5']

        self.__image = image.astype(float) # avoid problems when masking integerimages. necessary because integer NAN doesn't exist
        self.__images_to_change = []

        layout = QGridLayout(self)

        self.setFixedWidth(FIXED_WIDTH)

        figure_canvas = FigureCanvas(Figure())
        figure = figure_canvas.figure

        ax = figure.subplots()
        figure.subplots_adjust(left=-0.25, bottom=0.25)

        surface = ax.imshow(image, cmap='viridis', **kwargs4imshow)
        surface.cmap.set_over('#FF0000')  # Red
        surface.cmap.set_under('#8B008B')  # Light Cyan

        ax.set_title(title, fontsize=14, weight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        figure.colorbar(surface, extend='both')

        #                       [left, bottom, width, height]
        axcmin = figure.add_axes([0.40, 0.05, 0.25, 0.03])
        axcmax = figure.add_axes([0.40, 0.10, 0.25, 0.03])

        if cmin_o is None: cmin_o = surface.get_clim()[0]
        if cmax_o is None: cmax_o = surface.get_clim()[1]

        min_slider_val = (9*cmin_o - cmax_o)/8
        max_slider_val = (9*cmax_o - cmin_o)/8

        scmin = Slider(axcmin, 'Min',
                       min_slider_val, max_slider_val,
                       valinit=cmin_o)
        scmax = Slider(axcmax, 'Max',
                       min_slider_val, max_slider_val,
                       valinit=cmax_o)

        def update(val):
            cmin = scmin.val
            cmax = scmax.val

            if cmin < cmax:
                scmin.label.set_text('Min')
                scmax.label.set_text('Max')
            else:
                scmin.label.set_text('Max')
                scmax.label.set_text('Min')

            surface.set_clim(vmin=min(cmin, cmax), vmax=max(cmin, cmax))

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_clim(vmin=min(cmin, cmax), vmax=max(cmin, cmax))
                image_to_change.get_mpl_figure().canvas.draw()

        scmin.on_changed(update)
        scmax.on_changed(update)

        button_box_container = QWidget()
        button_box_container.setFixedWidth(figure_canvas.get_width_height()[0])
        button_box_container.setFixedHeight(45)
        button_box = widgetBox(button_box_container, orientation="horizontal", width=button_box_container.width())
        separator(button_box, width=button_box_container.width()*0.8)

        def reset():
            scmin.set_val(cmin_o)
            scmax.set_val(cmax_o)
            scmin.reset()
            scmax.reset()

            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_clim(vmin=image_to_change.get_cmin_o(),
                                                         vmax=image_to_change.get_cmax_o())
                image_to_change.get_mpl_figure().canvas.draw()

        def colorfunc():
            surface.set_cmap(__radio1_values[self.radio1])
            surface.cmap.set_over('#FF0000')  # Red
            surface.cmap.set_under('#8B008B')  # Light Cyan
            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_cmap(__radio1_values[self.radio1])
                image_to_change.get_mpl_image().cmap.set_over('#FF0000')  # Red
                image_to_change.get_mpl_image().cmap.set_under('#8B008B')  # Light Cyan
                image_to_change.get_mpl_figure().canvas.draw()

        def lin_or_pow():
            self.radio3 = 0
            self.rb_radio3.buttons[0].setChecked(True)
            filter_sparks()

            if self.radio2   == 0: n = 1
            elif self.radio2 == 1: n = 1/3
            elif self.radio2 == 2: n = 1/7
            elif self.radio2 == 3: n = 3
            elif self.radio2 == 4: n = 7

            def get_image_2plot(image):
                return ((image-image.min())**n*np.ptp(image) / np.ptp(image)**n + image.min())
            
            surface.set_data(get_image_2plot(self.__image))
            figure.canvas.draw()
            
            for image_to_change in self.__images_to_change:
                image_to_change.get_mpl_image().set_data(get_image_2plot(image_to_change.get_mpl_data()))
                image_to_change.get_mpl_figure().canvas.draw()

            
        def filter_sparks(): 
            if self.radio3 == 0: reset(); return
            elif self.radio3 == 1: sigma = 1
            elif self.radio3 == 2: sigma = 3
            elif self.radio3 == 3: sigma = 5

            image_2plot = surface.get_array().data
            
            cmin = common_tools.mean_plus_n_sigma(image_2plot, -sigma)
            cmax = common_tools.mean_plus_n_sigma(image_2plot, sigma)
            
            scmin.set_val(cmin)
            scmax.set_val(cmax)
            surface.set_clim(vmin=cmin, vmax=cmax)

            figure.canvas.draw()

            for image_to_change in self.__images_to_change:
                image_2plot = image_to_change.get_mpl_image().get_array().data
                cmin = common_tools.mean_plus_n_sigma(image_2plot, -sigma)
                cmax = common_tools.mean_plus_n_sigma(image_2plot, sigma)

                image_to_change.get_mpl_image().set_clim(vmin=cmin, vmax=cmax)
                image_to_change.get_mpl_figure().canvas.draw()

        button(button_box, self, "Reset", callback=reset, width=100, height=35)

        radio_button_box_container = QWidget()
        radio_button_box_container.setFixedWidth(120)
        radio_button_box_container.setFixedHeight(figure_canvas.get_width_height()[1] + button_box_container.height())
        radio_button_box = widgetBox(radio_button_box_container, "Options", orientation="vertical", width=button_box_container.width())

        self.radio1 = 2
        self.radio2 = 0
        self.radio3 = 0

        self.rb_radio2 = radioButtons(radio_button_box, self, "radio2", btnLabels=__radio2_values, box="Lin or Pow", callback=lin_or_pow)
        self.rb_radio3 = radioButtons(radio_button_box, self, "radio3", btnLabels=__radio3_values, box="Filter Sparks", callback=filter_sparks)
        self.rb_radio1 = radioButtons(radio_button_box, self, "radio1", btnLabels=__radio1_values, box="Color Map", callback=colorfunc)

        layout.addWidget(figure_canvas, 1, 1)
        layout.addWidget(button_box_container, 2, 1)
        layout.addWidget(radio_button_box_container, 0, 0, 2, 1)

        self.setLayout(layout)

    def set_images_to_change(self, images_to_change):
        self.__images_to_change = images_to_change

from wavepy2.util.log.logger import get_registered_logger_instance
from matplotlib.widgets import RectangleSelector

class GraphicalRoiIdx(QWidget):
    def __init__(self, parent, image, set_crop_output_listener):
        super(GraphicalRoiIdx, self).__init__(parent)

        logger = get_registered_logger_instance()

        layout = QHBoxLayout()

        figure_canvas = FigureCanvas(Figure(facecolor="white", figsize=(10, 8)))
        figure = figure_canvas.figure

        ax = figure.subplots()

        surface = ax.imshow(image, cmap='viridis')
        surface.cmap.set_over('#FF0000')  # Red
        surface.cmap.set_under('#8B008B')  # Light Cyan

        ax.set_xlabel('Pixels')
        ax.set_ylabel('Pixels')
        ax.set_title("Choose Roi, Right Click: reset", fontsize=16, color='r', weight='bold')

        figure.colorbar(surface)

        def onselect(eclick, erelease):
            """eclick and erelease are matplotlib events at press and release"""

            if eclick.button == 3: # right click
                ax.set_xlim(0, np.shape(image)[1])
                ax.set_ylim(np.shape(image)[0], 0)

                set_crop_output_listener([0, -1, 0, -1])

            elif eclick.button == 1:
                ROI_j_lim = np.sort([eclick.xdata, erelease.xdata]).astype(int).tolist()
                ROI_i_lim = np.sort([eclick.ydata, erelease.ydata]).astype(int).tolist()

                idx4crop = [0, 0, 0, 0]

                # this round method has an error of +-1pixel
                if ROI_j_lim[0] <= ROI_j_lim[1]:
                    idx4crop[0] = ROI_j_lim[0] - 1
                    idx4crop[1] = ROI_j_lim[1] + 1
                else:
                    idx4crop[0] = ROI_j_lim[1] - 1
                    idx4crop[1] = ROI_j_lim[0] + 1

                if ROI_i_lim[0] <= ROI_i_lim[1]:
                    idx4crop[2] = ROI_i_lim[0] + 1
                    idx4crop[3] = ROI_i_lim[1] - 1
                else:
                    idx4crop[2] = ROI_i_lim[1] - 1
                    idx4crop[3] = ROI_i_lim[0] + 1

                logger.print('\nSelecting ROI:')
                logger.print(' lower position : (%d, %d)' % (ROI_j_lim[0], ROI_i_lim[0]))
                logger.print(' higher position   : (%d, %d)' % (ROI_j_lim[1], ROI_i_lim[1]))
                logger.print(' width x and y: (%d, %d)' % (ROI_j_lim[1] - ROI_j_lim[0], ROI_i_lim[1] - ROI_i_lim[0]))

                ax.set_xlim(idx4crop[0], idx4crop[1])
                ax.set_ylim(idx4crop[3], idx4crop[2])

        def toggle_selector(event):
            logger.print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                logger.print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                logger.print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)

        toggle_selector.RS = RectangleSelector(figure.gca(), onselect,
                                               drawtype='box',
                                               rectprops=dict(facecolor='purple',
                                                              edgecolor='black',
                                                              alpha=0.5,
                                                              fill=True))

        figure.canvas.mpl_connect('key_press_event', toggle_selector)
        figure.tight_layout(rect=[0, 0, 1, 1])

        layout.addWidget(figure_canvas)

        self.__image_to_change = ImageToChange(mpl_image=surface, mpl_figure=figure)

        self.setLayout(layout)

    def get_image_to_change(self):
        return self.__image_to_change


##########################################################################
# WIDGETS UTILS FROM OASYS
#
# This code has been copied by the original Orange source code:
# see: www.orange.biolab.si
#
# source code at: https://github.com/oasys-kit/orange-widget-core/blob/master/orangewidget/gui.py
#
from PyQt5.QtWidgets import QGroupBox, QTabWidget, QScrollArea, \
    QLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, \
    QLabel, QRadioButton, QButtonGroup, QComboBox, QCheckBox
from PyQt5.QtGui import QIcon, QFont, QPalette
from PyQt5.QtCore import Qt

def widgetLabel(widget, label="", labelWidth=None, **misc):
    lbl = QLabel(label, widget)
    if labelWidth: lbl.setFixedSize(labelWidth, lbl.sizeHint().height())
    __miscellanea(lbl, None, widget, **misc)

    return lbl

def lineEdit(widget, master, value, label=None, labelWidth=None,
             orientation='vertical', box=None, callback=None,
             valueType=str, validator=None, controlWidth=None,
             callbackOnType=False, focusInCallback=None,
             enterPlaceholder=False, **misc):
    if box or label:
        b = widgetBox(widget, box, orientation, addToLayout=False)
        widgetLabel(b, label, labelWidth)
        hasHBox = orientation == 'horizontal' or not orientation
    else:
        b = widget
        hasHBox = False

    baseClass = misc.pop("baseClass", None)

    if baseClass:
        ledit = baseClass(b)
        ledit.enterButton = None
        if b is not widget: b.layout().addWidget(ledit)
    elif focusInCallback or callback and not callbackOnType:
        if not hasHBox:
            outer = widgetBox(b, "", 0, addToLayout=(b is not widget))
        else:
            outer = b
        ledit = __LineEditWFocusOut(outer, callback, focusInCallback, enterPlaceholder)
    else:
        ledit = QLineEdit(b)
        ledit.enterButton = None
        if b is not widget: b.layout().addWidget(ledit)

    if value:        ledit.setText(str(getdeepattr(master, value)))
    if controlWidth: ledit.setFixedWidth(controlWidth)
    if validator:    ledit.setValidator(validator)
    if value:        ledit.cback = connectControl(master, value,
                                                  callbackOnType and callback, ledit.textChanged[str],
                                                  __CallFrontLineEdit(ledit), fvcb=value and valueType)[1]

    __miscellanea(ledit, b, widget, **misc)
    if value and (valueType != str): ledit.setAlignment(Qt.AlignRight)
    ledit.setStyleSheet("background-color: white;")

    return ledit

def button(widget, master, label, callback=None, width=None, height=None,
           toggleButton=False, value="", default=False, autoDefault=True,
           buttonType=QPushButton, **misc):
    button = buttonType(widget)
    if label:
        button.setText(label)
    if width:
        button.setFixedWidth(width)
    if height:
        button.setFixedHeight(height)
    if toggleButton or value:
        button.setCheckable(True)
    if buttonType == QPushButton:
        button.setDefault(default)
        button.setAutoDefault(autoDefault)

    if value:
        button.setChecked(getdeepattr(master, value))
        __connectControl(master, value, None, button.toggled[bool], __CallFrontButton(button),
                         cfunc=callback and __FunctionCallback(master, callback, widget=button))
    elif callback:
        button.clicked.connect(callback)

    __miscellanea(button, None, widget, **misc)

    return button

# btnLabels is a list of either char strings or pixmaps
def radioButtons(widget, master, value, btnLabels=(), tooltips=None,
                 box=None, label=None, orientation='vertical',
                 callback=None, **misc):
    bg = widgetBox(widget, box, orientation, addToLayout=False)
    if not label is None: widgetLabel(bg, label)
    rb = QButtonGroup(bg)
    if bg is not widget: bg.group = rb
    bg.buttons = []
    bg.ogValue = value
    bg.ogMaster = master
    for i, lab in enumerate(btnLabels):
        __appendRadioButton(bg, lab, tooltip=tooltips and tooltips[i])
    __connectControl(master, value, callback, bg.group.buttonClicked[int],
                     __CallFrontRadioButtons(bg), __CallBackRadioButton(bg, master))
    misc.setdefault('addSpace', bool(box))
    __miscellanea(bg.group, bg, widget, **misc)

    return bg

def comboBox(widget, master, value, box=None, label=None, labelWidth=None,
             orientation='vertical', items=(), callback=None,
             sendSelectedValue=False, valueType=str,
             control2attributeDict=None, emptyString=None, editable=False,
             **misc):
    if box or label:
        hb = widgetBox(widget, box, orientation, addToLayout=False)
        if label is not None: widgetLabel(hb, label, labelWidth)
    else:
        hb = widget
    combo = QComboBox(hb)
    combo.setEditable(editable)
    combo.box = hb
    for item in items:
        if isinstance(item, (tuple, list)):
            combo.addItem(*item)
        else:
            combo.addItem(str(item))

    if value:
        cindex = __getdeepattr(master, value)
        if isinstance(cindex, str):
            if items and cindex in items:
                cindex = items.index(__getdeepattr(master, value))
            else:
                cindex = 0
        if cindex > combo.count() - 1: cindex = 0
        combo.setCurrentIndex(cindex)

        if sendSelectedValue:
            if control2attributeDict is None: control2attributeDict = {}
            if emptyString: control2attributeDict[emptyString] = ""
            __connectControl(master, value, callback, combo.activated[str],
                             __CallFrontComboBox(combo, valueType, control2attributeDict),
                             __ValueCallbackCombo(master, value, valueType, control2attributeDict))
        else:
            __connectControl(master, value, callback, combo.activated[int],
                             __CallFrontComboBox(combo, None, control2attributeDict))
    __miscellanea(combo, hb, widget, **misc)

    return combo

def checkBox(widget, master, value, label, box=None,
             callback=None, getwidget=False, id_=None, labelWidth=None,
             disables=None, **misc):
    if box:
        b = widgetBox(widget, box, orientation=None, addToLayout=False)
    else:
        b = widget
    cbox = QCheckBox(label, b)

    if labelWidth: cbox.setFixedSize(labelWidth, cbox.sizeHint().height())
    cbox.setChecked(getdeepattr(master, value))

    __connectControl(master, value, None, cbox.toggled[bool],
                     __CallFrontCheckBox(cbox),
                     cfunc=callback and __FunctionCallback(master, callback, widget=cbox, getwidget=getwidget, id=id_))
    if isinstance(disables, QWidget): disables = [disables]
    cbox.disables = disables or []
    cbox.makeConsistent = __Disabler(cbox, master, value)
    cbox.toggled[bool].connect(cbox.makeConsistent)
    cbox.makeConsistent(value)
    __miscellanea(cbox, b, widget, **misc)

    return cbox

def tabWidget(widget, height=None, width=None):
    w = QTabWidget(widget)
    w.setStyleSheet('QTabBar::tab::selected {background-color: #a6a6a6;}')

    if not widget.layout() is None: widget.layout().addWidget(w)
    if not height is None: w.setFixedHeight(height)
    if not width is None: w.setFixedWidth(width)

    return w

def createTabPage(tabWidget, name, widgetToAdd=None, canScroll=False):
    if widgetToAdd is None: widgetToAdd = widgetBox(tabWidget, addToLayout=0, margin=4)
    if canScroll:
        scrollArea = QScrollArea()
        tabWidget.addTab(scrollArea, name)
        scrollArea.setWidget(widgetToAdd)
        scrollArea.setWidgetResizable(1)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    else:
        tabWidget.addTab(widgetToAdd, name)

    return widgetToAdd

def widgetBox(widget, box=None, orientation='vertical', margin=None, spacing=4, height=None, width=None, **misc):
    if box:
        b = QGroupBox(widget)
        if isinstance(box, str): b.setTitle(" " + box.strip() + " ")
        if margin is None: margin = 7
    else:
        b = QWidget(widget)
        b.setContentsMargins(0, 0, 0, 0)
        if margin is None: margin = 0

    __setLayout(b, orientation)
    b.layout().setSpacing(spacing)
    b.layout().setContentsMargins(margin, margin, margin, margin)
    misc.setdefault('addSpace', bool(box))
    __miscellanea(b, None, widget, **misc)

    b.layout().setAlignment(Qt.AlignTop)
    if not height is None: b.setFixedHeight(height)
    if not width is None:b.setFixedWidth(width)

    return b

def separator(widget, width=4, height=4):
    sep = QWidget(widget)
    if widget.layout() is not None: widget.layout().addWidget(sep)
    sep.setFixedSize(width, height)
    return sep


##########################################################################
##########################################################################
##########################################################################
# PRIVATE
#
# This code has been copied by the original Orange source code:
# see: www.orange.biolab.si
#
# source code at: https://github.com/oasys-kit/orange-widget-core/blob/master/orangewidget/gui.py
#

from functools import reduce

def __getdeepattr(obj, attr, *arg, **kwarg):
    if isinstance(obj, dict): return obj.get(attr)

    try:
        return reduce(lambda o, n: getattr(o, n), attr.split("."), obj)
    except AttributeError:
        if arg: return arg[0]
        if kwarg: return kwarg["default"]
        raise AttributeError("'%s' has no attribute '%s'" % (obj, attr))

def __setLayout(widget, orientation):
    if isinstance(orientation, QLayout): widget.__setLayout(orientation)
    elif orientation == 'horizontal' or not orientation: widget.setLayout(QHBoxLayout())
    else: widget.setLayout(QVBoxLayout())

def __miscellanea(control, box, parent,
                  addToLayout=True, stretch=0, sizePolicy=None, addSpace=False,
                  disabled=False, tooltip=None):
    if disabled: control.setDisabled(disabled)
    if tooltip is not None: control.setToolTip(tooltip)
    if box is parent: box = None
    elif box and box is not control and not hasattr(control, "box"): control.box = box
    if box and box.layout() is not None and isinstance(control, QWidget) and box.layout().indexOf(control) == -1: box.layout().addWidget(control)
    if sizePolicy is not None: (box or control).setSizePolicy(sizePolicy)
    if addToLayout and parent and parent.layout() is not None:
        parent.layout().addWidget(box or control, stretch)
        __addSpace(parent, addSpace)

def __addSpace(widget, space):
    if space:
        if isinstance(space, bool): separator(widget)
        else: separator(widget, space, space)


def __appendRadioButton(group, label, insertInto=None,
                      disabled=False, tooltip=None, sizePolicy=None,
                      addToLayout=True, stretch=0, addSpace=False):
    i = len(group.buttons)
    if isinstance(label, str): w = QRadioButton(label)
    else:
        w = QRadioButton(str(i))
        w.setIcon(QIcon(label))
    if not hasattr(group, "buttons"): group.buttons = []
    group.buttons.append(w)
    group.group.addButton(w)
    w.setChecked(__getdeepattr(group.ogMaster, group.ogValue) == i)

    # miscellanea for this case is weird, so we do it here
    if disabled: w.setDisabled(disabled)
    if tooltip is not None: w.setToolTip(tooltip)
    if sizePolicy: w.setSizePolicy(sizePolicy)
    if addToLayout:
        dest = insertInto or group
        dest.layout().addWidget(w, stretch)
        __addSpace(dest, addSpace)

    return w

CONTROLLED_ATTRIBUTES = "controlledAttributes"
DISABLER = 1
HIDER = 2

class __Disabler:
    def __init__(self, widget, master, valueName, propagateState=True,
                 type=DISABLER):
        self.widget = widget
        self.master = master
        self.valueName = valueName
        self.propagateState = propagateState
        self.type = type

    def __call__(self, *value):
        currState = self.widget.isEnabled()
        if currState or not self.propagateState:
            if len(value): disabled = not value[0]
            else: disabled = not __getdeepattr(self.master, self.valueName)
        else: disabled = 1
        for w in self.widget.disables:
            if type(w) is tuple:
                if isinstance(w[0], int):
                    i = 1
                    if w[0] == -1: disabled = not disabled
                else: i = 0
                if self.type == DISABLER: w[i].setDisabled(disabled)
                elif self.type == HIDER:
                    if disabled: w[i].hide()
                    else: w[i].show()
                if hasattr(w[i], "makeConsistent"): w[i].makeConsistent()
            else:
                if self.type == DISABLER: w.setDisabled(disabled)
                elif self.type == HIDER:
                    if disabled: w.hide()
                    else: w.show()

class __LineEditWFocusOut(QLineEdit):
    def __init__(self, parent, callback, focusInCallback=None,
                 placeholder=False):
        super().__init__(parent)
        if parent.layout() is not None:
            parent.layout().addWidget(self)
        self.callback = callback
        self.focusInCallback = focusInCallback
        self.enterButton, self.placeHolder = \
            _enterButton(parent, self, placeholder)
        self.enterButton.clicked.connect(self.returnPressedHandler)
        self.textChanged[str].connect(self.markChanged)
        self.returnPressed.connect(self.returnPressedHandler)

    def markChanged(self, *_):
        if self.placeHolder:
            self.placeHolder.hide()
        self.enterButton.show()

    def markUnchanged(self, *_):
        self.enterButton.hide()
        if self.placeHolder:
            self.placeHolder.show()

    def returnPressedHandler(self):
        if self.enterButton.isVisible():
            self.markUnchanged()
            if hasattr(self, "cback") and self.cback:
                self.cback(self.text())
            if self.callback:
                self.callback()

    def setText(self, t):
        super().setText(t)
        if self.enterButton:
            self.markUnchanged()

    def focusOutEvent(self, *e):
        super().focusOutEvent(*e)
        self.returnPressedHandler()

    def focusInEvent(self, *e):
        if self.focusInCallback:
            self.focusInCallback()
        return super().focusInEvent(*e)

class __ControlledCallback:
    def __init__(self, widget, attribute, f=None):
        self.widget = widget
        self.attribute = attribute
        self.f = f
        self.disabled = 0
        if isinstance(widget, dict):
            return  # we can't assign attributes to dict
        if not hasattr(widget, "callbackDeposit"):
            widget.callbackDeposit = []
        widget.callbackDeposit.append(self)

    def acyclic_setattr(self, value):
        if self.disabled:
            return
        if self.f:
            if self.f in (int, float) and (
                    not value or isinstance(value, str) and value in "+-"):
                value = self.f(0)
            else:
                value = self.f(value)
        opposite = getattr(self, "opposite", None)
        if opposite:
            try:
                opposite.disabled += 1
                if type(self.widget) is dict:
                    self.widget[self.attribute] = value
                else:
                    setattr(self.widget, self.attribute, value)
            finally:
                opposite.disabled -= 1
        else:
            if isinstance(self.widget, dict):
                self.widget[self.attribute] = value
            else:
                setattr(self.widget, self.attribute, value)

class __ValueCallback(__ControlledCallback):
    def __call__(self, value):
        if value is None:
            return
        try:
            self.acyclic_setattr(value)
        except Exception:
            print("gui.ValueCallback: %s" % value)
            traceback.print_exception(*sys.exc_info())

class __ValueCallbackCombo(__ValueCallback):
    def __init__(self, widget, attribute, f=None, control2attributeDict=None):
        super().__init__(widget, attribute, f)
        self.control2attributeDict = control2attributeDict or {}

    def __call__(self, value):
        value = str(value)
        return super().__call__(self.control2attributeDict.get(value, value))

class __FunctionCallback:
    def __init__(self, master, f, widget=None, id=None, getwidget=False):
        self.master = master
        self.widget = widget
        self.f = f
        self.id = id
        self.getwidget = getwidget
        if hasattr(master, "callbackDeposit"): master.callbackDeposit.append(self)
        self.disabled = 0

    def __call__(self, *value):
        if not self.disabled and value is not None:
            kwds = {}
            if self.id is not None: kwds['id'] = self.id
            if self.getwidget: kwds['widget'] = self.widget
            if isinstance(self.f, list):
                for f in self.f:
                    f(**kwds)
            else:
                self.f(**kwds)

class __CallBackRadioButton:
    def __init__(self, control, widget):
        self.control = control
        self.widget = widget
        self.disabled = False

    def __call__(self, *_):  # triggered by toggled()
        if not self.disabled and self.control.ogValue is not None:
            arr = [butt.isChecked() for butt in self.control.buttons]
            self.widget.__setattr__(self.control.ogValue, arr.index(1))

class __ControlledCallFront:
    def __init__(self, control):
        self.control = control
        self.disabled = 0

    def action(self, *_):
        pass

    def __call__(self, *args):
        if not self.disabled:
            opposite = getattr(self, "opposite", None)
            if opposite:
                try:
                    for op in opposite:
                        op.disabled += 1
                    self.action(*args)
                finally:
                    for op in opposite:
                        op.disabled -= 1
            else:
                self.action(*args)

class __CallFrontButton(__ControlledCallFront):
    def action(self, value):
        if value is not None: self.control.setChecked(bool(value))

class __CallFrontLineEdit(__ControlledCallFront):
    def action(self, value):
        self.control.setText(str(value))

class __CallFrontRadioButtons(__ControlledCallFront):
    def action(self, value):
        if value < 0 or value >= len(self.control.buttons): value = 0
        self.control.buttons[value].setChecked(1)

class __CallFrontComboBox(__ControlledCallFront):
    def __init__(self, control, valType=None, control2attributeDict=None):
        super().__init__(control)
        self.valType = valType
        if control2attributeDict is None:
            self.attribute2controlDict = {}
        else:
            self.attribute2controlDict = \
                {y: x for x, y in control2attributeDict.items()}

    def action(self, value):
        if value is not None:
            value = self.attribute2controlDict.get(value, value)
            if self.valType:
                for i in range(self.control.count()):
                    if self.valType(str(self.control.itemText(i))) == value:
                        self.control.setCurrentIndex(i)
                        return
                values = ""
                for i in range(self.control.count()):
                    values += str(self.control.itemText(i)) + \
                        (i < self.control.count() - 1 and ", " or ".")
                print("unable to set %s to value '%s'. Possible values are %s"
                      % (self.control, value, values))
            else:
                if value < self.control.count():
                    self.control.setCurrentIndex(value)

class __CallFrontCheckBox(__ControlledCallFront):
    def action(self, value):
        if value is not None:
            values = [Qt.Unchecked, Qt.Checked, Qt.PartiallyChecked]
            self.control.setCheckState(values[value])

def __connectControl(master, value, f, signal, cfront, cback=None, cfunc=None, fvcb=None):
    cback = cback or value and ValueCallback(master, value, fvcb)
    if cback:
        if signal:
            signal.connect(cback)
        cback.opposite = cfront
        if value and cfront and hasattr(master, CONTROLLED_ATTRIBUTES): getattr(master, CONTROLLED_ATTRIBUTES)[value] = cfront
    cfunc = cfunc or f and __FunctionCallback(master, f)
    if cfunc:
        if signal: signal.connect(cfunc)
        cfront.opposite = tuple(filter(None, (cback, cfunc)))

    return cfront, cback, cfunc
