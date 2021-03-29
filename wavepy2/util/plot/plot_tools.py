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

class AbstractContextWidget():

    def __init__(self, container_widget):
        self.__container_widget = container_widget

    def get_container_widget(self):
        return self.__container_widget

class DefaultContextWidget(AbstractContextWidget):
    def __init__(self, container_widget):
        super(DefaultContextWidget, self).__init__(container_widget)

class DefaultMainWindow(QMainWindow, AbstractContextWidget):
    def __init__(self, title):
        super(DefaultMainWindow, self).__init__(container_widget=QWidget())
        self.setWindowTitle(title)
        self.setCentralWidget(self.get_container_widget())

        desktop_widget = QDesktopWidget()
        actual_geometry = self.frameGeometry()
        screen_geometry = desktop_widget.availableGeometry()
        new_geometry = QRect()
        new_geometry.setWidth(actual_geometry.width())
        new_geometry.setHeight(actual_geometry.height())
        new_geometry.setTop(screen_geometry.height()*0.05)
        new_geometry.setLeft(screen_geometry.width()*0.05)

        self.setGeometry(new_geometry)

        self.setStyleSheet(stylesheet_string)

class PlottingProperties:
    def __init__(self, container_widget=None, context_widget=None, **parameters):
        self.__container_widget = container_widget
        self.__context_widget = context_widget
        self.__parameters = parameters

    def get_container_widget(self):
        return self.__container_widget

    def get_context_widget(self):
        return self.__context_widget

    def get_parameters(self):
        return self.__parameters

    def get_parameter(self, parameter_name, default_value=None):
        try:
            return self.__parameters[parameter_name]
        except:
            return default_value

    def set_parameter(self, parameter_name, value):
        self.__parameters[parameter_name] = value


WIDGET_FIXED_WIDTH = 800

##########################################################################
# UTILITY FROM WAVEPY

from wavepy2.util.log.logger import get_registered_logger_instance
from wavepy2.util.common import common_tools

def save_sdf_file(array, pixelsize=[1, 1], fname='output.sdf', extraHeader={}, application_name=None):
    logger = get_registered_logger_instance(application_name=application_name)

    if len(array.shape) != 2:
        logger.print_error('Function save_sdf: array must be 2-dimensional')
        raise ValueError('Function save_sdf: array must be 2-dimensional')

    header = 'aBCR-0.0\n' + \
             'ManufacID\t=\tWavePy2\n' + \
             'CreateDate\t=\t' + \
             common_tools.datetime_now_str()[:-2].replace('_', '') + '\n' + \
             'ModDate\t=\t' + \
             common_tools.datetime_now_str()[:-2].replace('_', '') + '\n' + \
             'NumPoints\t=\t' + str(array.shape[1]) + '\n' + \
             'NumProfiles\t=\t' + str(array.shape[0]) + '\n' + \
             'Xscale\t=\t' + str(pixelsize[1]) + '\n' + \
             'Yscale\t=\t' + str(pixelsize[0]) + '\n' + \
             'Zscale\t=\t1\n' + \
             'Zresolution\t=\t0\n' + \
             'Compression\t=\t0\n' + \
             'DataType\t=\t7 \n' + \
             'CheckType\t=\t0\n' + \
             'NumDataSet\t=\t1\n' + \
             'NanPresent\t=\t0\n'

    for key in extraHeader.keys():
        header += key + '\t=\t' + extraHeader[key] + '\n'
    header += '*'

    if array.dtype == 'float64': fmt = '%1.8g'
    elif array.dtype == 'int64': fmt = '%d'
    else: fmt = '%f'

    np.savetxt(fname, array.flatten(), fmt=fmt, header=header, comments='')
    logger.print_message(fname + ' saved!')


def save_csv_file(arrayList, fname='output.csv', headerList=[], comments='', application_name=None):
    logger = get_registered_logger_instance(application_name=application_name)

    header = ''
    if headerList != []:
        for item in headerList:
            header += item + ', '

        header = header[:-2]  # remove last comma

    if comments != '': header = comments + '\n' + header

    if isinstance(arrayList, list):
        data2save = np.c_[arrayList[0], arrayList[1]]
        for array in arrayList[2:]: data2save = np.c_[data2save, array]
    elif isinstance(arrayList, np.ndarray): data2save = arrayList
    else: raise TypeError

    if data2save.dtype == 'float64': fmt = '%1.8g'
    elif data2save.dtype == 'int64': fmt = '%d'
    else: fmt = '%f'

    np.savetxt(fname, data2save, fmt=fmt, header=header, delimiter=', ')
    logger.print_message(fname + ' saved!')


def load_sdf_file(fname, printHeader=False):
    with open(fname) as input_file:
        nline = 0
        header = ''
        if printHeader: print('########## HEADER from ' + fname)

        for line in input_file:
            nline += 1
            if printHeader: print(line, end='')
            if 'NumPoints' in line: xpoints = int(line.split('=')[-1])
            if 'NumProfiles' in line: ypoints = int(line.split('=')[-1])
            if 'Xscale' in line: xscale = float(line.split('=')[-1])
            if 'Yscale' in line: yscale = float(line.split('=')[-1])
            if 'Zscale' in line: zscale = float(line.split('=')[-1])
            if '*' in line: break
            else: header += line

    if printHeader: print('########## END HEADER from ' + fname)

    data = np.loadtxt(fname, skiprows=nline)
    data = data.reshape(ypoints, xpoints)*zscale
    headerdic = {}
    header = header.replace('\t', '')
    for item in header.split('\n'):
        items = item.split('=')
        if len(items) > 1: headerdic[items[0]] = items[1]

    return data, [yscale, xscale], headerdic

def load_csv_file(fname):
    with open(fname) as input_file:
        comments = []
        for line in input_file:
            if '#' in line:
                comments.append(line[2:-1])
                header = line[2:-1]  # remove # and \n
            else: break

    data = np.loadtxt(fname, delimiter=',')

    headerlist = []
    for item in header.split(', '): headerlist.append(item)

    return data, headerlist, comments


from matplotlib.pyplot import get_cmap
import itertools

def line_style_cycle(ls=['-', '--'], ms=['s', 'o', '^', 'd'], ncurves=2, cmap_str='default'):
    list_ls = list(a[0] + a[1] for a in itertools.product(ls, ms))
    ls_cycle = itertools.cycle(list_ls[0:ncurves])

    if cmap_str == 'default':
        lc_list = ['#4C72B0', '#55A868', '#C44E52', '#8172B2',
                   '#CCB974', '#64B5CD', '#1f77b4', '#ff7f0e',
                   '#2ca02c', '#d62728', '#9467bd', '#8c564b',
                   '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    else:
        cmap = get_cmap(cmap_str)
        lc_list = [cmap(x) for x in np.linspace(0, 1, ncurves)]

    lc_cycle = itertools.cycle(lc_list)

    return ls_cycle, lc_cycle

from scipy.interpolate import UnivariateSpline

def fwhm_xy(xvalues, yvalues):
    spline = UnivariateSpline(xvalues, yvalues-np.min(yvalues)/2-np.max(yvalues)/2, s=0)

    xvalues = spline.roots().tolist()
    yvalues = (spline(spline.roots()) + np.min(yvalues)/2 + np.max(yvalues)/2).tolist()

    if len(xvalues) == 2: return [xvalues, yvalues]
    else: return[[], []]


##########################################################################
# WIDGETS UTILS FROM OASYS

from PyQt5.QtWidgets import QWidget, QMessageBox, QTextEdit, QFileDialog

class ConfirmDialog(QMessageBox):
    def __init__(self, parent, message, title):
        super(ConfirmDialog, self).__init__(parent)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setIcon(QMessageBox.Question)
        self.setText(message)
        self.setWindowTitle(title)

    @classmethod
    def confirmed(cls, parent=None, message="Confirm Action?", title="Confirm Action"):
        return ConfirmDialog(parent, message, title).exec_() == QMessageBox.Ok

class OptionDialog(QMessageBox):
    def __init__(self, parent, message, title, options, default):
        super(OptionDialog, self).__init__(parent)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setIcon(QMessageBox.Question)
        self.setText(message)
        self.setWindowTitle(title)

        self.selection = default

        comboBox( widgetBox(self, "", height=40), self, label="Select Option", items=options, callback=self.set_selection, orientation="horizontal")

    def set_selection(self, index):
        self.selection = index

    @classmethod
    def get_option(cls, parent=None, message="Select Option", title="Select Option", option=["No", "Yes"], default=0):
        dlg = OptionDialog(parent, message, title, option, default)
        if dlg.exec_() == QMessageBox.Ok: return dlg.selection
        else: return None

class ValueDialog(QMessageBox):
    def __init__(self, parent, message, title, default):
        super(ValueDialog, self).__init__(parent)

        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(QMessageBox.Question)
        self.setText(message)
        self.setWindowTitle(title)

        self.value = default

        lineEdit(widgetBox(self, "", height=40), self, "value", "", orientation="horizontal")

    @classmethod
    def get_value(cls, parent=None, message="Input Value", title="Input Option", default=0):
        dlg = ValueDialog(parent, message, title, default)
        if dlg.exec_() == QMessageBox.Ok: return dlg.value
        else: return None


def selectFileFromDialog(widget, previous_file_path="", message="Select File", start_directory=".", file_extension_filter="*.*"):
    file_path = QFileDialog.getOpenFileName(widget, message, start_directory, file_extension_filter)[0]
    if not file_path is None and not file_path.strip() == "": return file_path
    else: return previous_file_path


def selectDirectoryFromDialog(widget, previous_directory_path="", message="Select Directory", start_directory="."):
    directory_path = QFileDialog.getExistingDirectory(widget, message, start_directory)
    if not directory_path is None and not directory_path.strip() == "": return directory_path
    else: return previous_directory_path

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

    if value:        ledit.setText(str(__getdeepattr(master, value)))
    if controlWidth: ledit.setFixedWidth(controlWidth)
    if validator:    ledit.setValidator(validator)
    if value:        ledit.cback = __connectControl(master, value,
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
        button.setChecked(__getdeepattr(master, value))
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
    cbox.setChecked(__getdeepattr(master, value))

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

def textArea(height=None, width=None, readOnly=True, noWrap=None):
    area = QTextEdit()
    area.setReadOnly(readOnly)
    area.setStyleSheet("background-color: white;")
    if noWrap is not None:
        area.setLineWrapMode(QTextEdit.NoWrap)

    if not height is None: area.setFixedHeight(height)
    if not width is None: area.setFixedWidth(width)

    return area


import six, os

def package_dirname(package):
    if isinstance(package, six.string_types): package = __import__(package, fromlist=[""])
    return os.path.dirname(package.__file__)

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

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton

_getdeepattr = __getdeepattr

def _enterButton(parent, control, placeholder=True):
    """
    Utility function that returns a button with a symbol for "Enter" and
    optionally a placeholder to show when the enter button is hidden. Both
    are inserted into the parent's layout, if it has one. If placeholder is
    constructed it is shown and the button is hidden.

    The height of the button is the same as the height of the widget passed
    as argument `control`.

    :param parent: parent widget into which the button is inserted
    :type parent: PyQt5.QtWidgets.QWidget
    :param control: a widget for determining the height of the button
    :type control: PyQt5.QtWidgets.QWidget
    :param placeholder: a flag telling whether to construct a placeholder
        (default: True)
    :type placeholder: bool
    :return: a tuple with a button and a place holder (or `None`)
    :rtype: PyQt5.QtWidgets.QToolButton or tuple
    """
    global _enter_icon
    if not _enter_icon:
        _enter_icon = QIcon(os.path.join(package_dirname("wavepy2.util.plot"), "icons/Dlg_enter.png"))
    button = QToolButton(parent)
    height = control.sizeHint().height()
    button.setFixedSize(height, height)
    button.setIcon(_enter_icon)
    if parent.layout() is not None:
        parent.layout().addWidget(button)
    if placeholder:
        button.hide()
        holder = QWidget(parent)
        holder.setFixedSize(height, height)
        if parent.layout() is not None:
            parent.layout().addWidget(holder)
    else:
        holder = None
    return button, holder

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
            else: disabled = not _getdeepattr(self.master, self.valueName)
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
        self.enterButton, self.placeHolder = _enterButton(parent, self, placeholder)
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
            pass

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
    cback = cback or value and __ValueCallback(master, value, fvcb)
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

stylesheet_string = "" + \
"/*" + "\n" + \
" * Icon search paths relative to this files directory." + "\n" + \
" * (main.py script will add this to QDir.searchPaths)" + "\n" + \
" */" + "\n" + \
"" + "\n" + \
"/* Main window background color */" + "\n" + \
"" + "\n" + \
"QMainWindow {" + "\n" + \
"    background-color: #E9EFF2;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"QMainWindow::separator {" + "\n" + \
"    width: 1px; /* when vertical */" + "\n" + \
"    height: 1px; /* when horizontal */" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"/* The widget buttons in the dock tool box */" + "\n" + \
"" + "\n" + \
"WidgetToolBox WidgetToolGrid QToolButton {" + "\n" + \
"    border: none;" + "\n" + \
"    background-color: #F2F2F2;" + "\n" + \
"    border-radius: 8px;" + "\n" + \
"/*" + "\n" + \
"    font-family: \"Helvetica\";" + "\n" + \
"    font-size: 10px;" + "\n" + \
"    font-weight: bold;" + "\n" + \
"*/" + "\n" + \
"    color: #333;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"/* Dock widget tool box tab buttons (categories) */" + "\n" + \
"" + "\n" + \
"WidgetToolBox QToolButton#toolbox-tab-button {" + "\n" + \
"    /* nativeStyling property overrides the QStyle and uses a fixed drawing" + "\n" + \
"    routine */" + "\n" + \
"    qproperty-nativeStyling_: \"false\";" + "\n" + \
"" + "\n" + \
"    font-family: \"Helvetica\";" + "\n" + \
"    font-size: 14px;" + "\n" + \
"    font-weight: bold;" + "\n" + \
"    color: #333;" + "\n" + \
"    border: none;" + "\n" + \
"    border-bottom: 1px solid #B5B8B8;" + "\n" + \
"    background: qlineargradient(" + "\n" + \
"        x1: 0, y1: 0, x2: 0, y2: 1," + "\n" + \
"        stop: 0 #F2F2F2," + "\n" + \
"        stop: 0.5 #F2F2F2," + "\n" + \
"        stop: 0.8 #EBEBEB," + "\n" + \
"        stop: 1.0 #DBDBDB" + "\n" + \
"    );" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"WidgetToolBox QToolButton#toolbox-tab-button:hover {" + "\n" + \
"    background-color: palette(light);" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"WidgetToolBox QToolButton#toolbox-tab-button:checked {" + "\n" + \
"    background-color: palette(dark);" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"WidgetToolBox QToolButton#toolbox-tab-button:focus {" + "\n" + \
"    background-color: palette(highlight);" + "\n" + \
"    border: 1px solid #609ED7" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"WidgetToolBox ToolGrid {" + "\n" + \
"    background-color: #F2F2F2;" + "\n" + \
"    padding-bottom: 8px;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"WidgetToolBox QWidget#toolbox-contents {" + "\n" + \
"    background-color: #F2F2F2; /* match the ToolGrid's background */" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"WidgetToolBox ToolGrid QToolButton[last-column] {" + "\n" + \
"    border-right: none;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"WidgetToolBox  ToolGrid QToolButton:focus {" + "\n" + \
"    background-color: palette(window);" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"WidgetToolBox  ToolGrid QToolButton:hover {" + "\n" + \
"    background-color: palette(light);" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"WidgetToolBox  ToolGrid QToolButton:pressed {" + "\n" + \
"    background-color: palette(dark);" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"/* QuickCategoryToolbar popup menus */" + "\n" + \
"" + "\n" + \
"CategoryPopupMenu {" + "\n" + \
"	background-color: #E9EFF2;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CategoryPopupMenu ToolTree QTreeView::item {" + "\n" + \
"	height: 25px;" + "\n" + \
"	border-bottom: 1px solid #e9eff2;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CategoryPopupMenu QTreeView::item:selected {" + "\n" + \
"	background: qlineargradient(" + "\n" + \
"		x1: 0, y1: 0, x2: 0, y2: 1," + "\n" + \
"		stop: 0 #688EF6," + "\n" + \
"		stop: 0.5 #4047f4," + "\n" + \
"		stop: 1.0 #2D68F3" + "\n" + \
"	);" + "\n" + \
"	color: white;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"/* Canvas Dock Header */" + "\n" + \
"" + "\n" + \
"CollapsibleDockWidget::title {" + "\n" + \
"    background: qlineargradient(" + "\n" + \
"        x1: 0, y1: 0, x2: 0, y2: 1," + "\n" + \
"        stop: 0 #808080, stop: 1.0 #666" + "\n" + \
"    );" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"/* Dock widget title bar button icons (icon size for both must be set)." + "\n" + \
" * The buttons define the title bar height." + "\n" + \
" */" + "\n" + \
"" + "\n" + \
"CollapsibleDockWidget::close-button, CollapsibleDockWidget::float-button {" + "\n" + \
"    padding: 1px;" + "\n" + \
"    icon-size: 11px;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CanvasToolDock WidgetToolBox {" + "\n" + \
"    border: 1px solid #B5B8B8;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"/* Toolbar at the bottom of the dock widget when in in expanded state" + "\n" + \
" */" + "\n" + \
"" + "\n" + \
"CanvasToolDock QToolBar {" + "\n" + \
"    height: 28;" + "\n" + \
"    spacing: 1;" + "\n" + \
"    border: none;" + "\n" + \
"    /*" + "\n" + \
"    background: qlineargradient(" + "\n" + \
"        x1: 0, y1: 0, x2: 0, y2: 1," + "\n" + \
"        stop: 0 #808080, stop: 1.0 #666" + "\n" + \
"    );" + "\n" + \
"    */" + "\n" + \
"    background-color: #898989;" + "\n" + \
"" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CanvasToolDock QToolBar QToolButton {" + "\n" + \
"    border: none;" + "\n" + \
"    background: qlineargradient(" + "\n" + \
"        x1: 0, y1: 0, x2: 0, y2: 1," + "\n" + \
"        stop: 0 #808080, stop: 1.0 #666" + "\n" + \
"    );" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CanvasToolDock QToolBar QToolButton:menu-indicator {" + "\n" + \
"     image: url(canvas_icons:/Dropdown.svg);" + "\n" + \
"     subcontrol-position: top right;" + "\n" + \
"     height: 8px;" + "\n" + \
"     width: 8px;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CanvasToolDock QToolBar QToolButton:checked," + "\n" + \
"CanvasToolDock QToolBar QToolButton:pressed {" + "\n" + \
"    background-color: #FFA840;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"/* Toolbar in the dock when in collapsed state." + "\n" + \
" */" + "\n" + \
"" + "\n" + \
"CollapsibleDockWidget QWidget#canvas-quick-dock QToolBar {" + "\n" + \
"    spacing: 1;" + "\n" + \
"    border: none;" + "\n" + \
"    /*" + "\n" + \
"    background: qlineargradient(" + "\n" + \
"        x1: 0, y1: 0, x2: 0, y2: 1," + "\n" + \
"        stop: 0 #808080, stop: 1.0 #666" + "\n" + \
"    );" + "\n" + \
"    */" + "\n" + \
"    background-color: #898989;" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"" + "\n" + \
"CollapsibleDockWidget QWidget#canvas-quick-dock QToolBar QToolButton {" + "\n" + \
"    border: none;" + "\n" + \
"    background: qlineargradient(" + "\n" + \
"        x1: 0, y1: 0, x2: 1, y2: 0," + "\n" + \
"        stop: 0 #808080, stop: 1.0 #666" + "\n" + \
"    );" + "\n" + \
"}" + "\n" + \
"" + "\n" + \
"CollapsibleDockWidget QWidget#canvas-quick-dock QToolBar QToolButton:menu-indicator {"+ "\n" + \
"     image: url(canvas_icons:/Dropdown.svg);"+ "\n" + \
"     subcontrol-position: top right;"+ "\n" + \
"     height: 8px;"+ "\n" + \
"     width: 8px;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"CollapsibleDockWidget QWidget#canvas-quick-dock QToolBar QToolButton:checked,"+ "\n" + \
"CollapsibleDockWidget QWidget#canvas-quick-dock QToolBar QToolButton:pressed {"+ "\n" + \
"    background-color: #FFA840;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
""+ "\n" + \
"/* Splitter between the widget toolbox and quick help."+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"CanvasToolDock QSplitter::handle {"+ "\n" + \
"    border: 1px solid #B5B8B8;"+ "\n" + \
""+ "\n" + \
"/*    border-top: 1px solid #B5B8B8;"+ "\n" + \
" *   border-bottom: 1px solid #B5B8B8;"+ "\n" + \
" *   border-left: 1px solid #B6B6B6;"+ "\n" + \
" *   border-right: 1px solid #B6B6B6;"+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"    background:  qlineargradient("+ "\n" + \
"        x1: 0, y1: 0, x2: 0, y2: 1,"+ "\n" + \
"        stop: 0 #D4D4D4, stop: 0.05 #EDEDED,"+ "\n" + \
"        stop: 0.5 #F2F2F2,"+ "\n" + \
"        stop: 0.95 #EDEDED, stop: 1.0 #E0E0E0"+ "\n" + \
"    );"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
""+ "\n" + \
"/* Scheme Info Dialog"+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog {"+ "\n" + \
"    font-family: \"Helvetica\";"+ "\n" + \
"    background-color: #E9EFF2;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog SchemeInfoEdit QLabel {"+ "\n" + \
"    font-family: \"Helvetica\";"+ "\n" + \
"    font-weight: bold;"+ "\n" + \
"    font-size: 16px;"+ "\n" + \
"    color: black;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog QLabel#heading {"+ "\n" + \
"    font-size: 21px;"+ "\n" + \
"    color: #515151;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog StyledWidget#auto-show-container * {"+ "\n" + \
"    font-family: \"Helvetica\";"+ "\n" + \
"    font-size: 12px;"+ "\n" + \
"    color: #1A1A1A;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog StyledWidget#auto-show-container {"+ "\n" + \
"    border-top: 1px solid #C1C2C3;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog SchemeInfoEdit QLineEdit {"+ "\n" + \
"    padding: 4px;"+ "\n" + \
"    /* background-color: red; */"+ "\n" + \
"    /* font-weight: normal; */"+ "\n" + \
"    font-size: 12px;"+ "\n" + \
"    color: #1A1A1A;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"SchemeInfoDialog SchemeInfoEdit QTextEdit {"+ "\n" + \
"    padding: 4px;"+ "\n" + \
"    background-color: white;"+ "\n" + \
"    /* font-weight: normal; */"+ "\n" + \
"    font-size: 12px;"+ "\n" + \
"    color: #1A1A1A;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
""+ "\n" + \
"/* Preview Dialog (Recent Schemes and Tutorials)"+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"PreviewDialog {"+ "\n" + \
"    background-color: #E9EFF2;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"PreviewDialog QLabel#heading {"+ "\n" + \
"    font-family: \"Helvetica\";"+ "\n" + \
"    font-weight: bold;"+ "\n" + \
"    font-size: 21px;"+ "\n" + \
"    color: #515151;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"PreviewDialog PreviewBrowser * {"+ "\n" + \
"    font-family: \"Helvetica\";"+ "\n" + \
"    color: #1A1A1A;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"PreviewDialog PreviewBrowser TextLabel#path-text {"+ "\n" + \
"    font-size: 12px;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"PreviewDialog PreviewBrowser QLabel#path-label {"+ "\n" + \
"    font-size: 12px;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"PreviewDialog DropShadowFrame {"+ "\n" + \
"    qproperty-radius_: 10;"+ "\n" + \
"    qproperty-color_: rgb(0, 0, 0, 100);"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"/* Welcome Screen Dialog"+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"WelcomeDialog {"+ "\n" + \
"    background-color: #E9EFF2;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"WelcomeDialog QToolButton {"+ "\n" + \
"	font-family: \"Helvetica\";"+ "\n" + \
"	font-size: 13px;"+ "\n" + \
"	font-style: normal;"+ "\n" + \
"	font-weight: bold;"+ "\n" + \
"	color: #333;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"WelcomeDialog QWidget#bottom-bar {"+ "\n" + \
"	border-top: 1px solid #C1C2C3;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"WelcomeDialog QWidget#bottom-bar QCheckBox {	"+ "\n" + \
"	font-family: \"Helvetica\";"+ "\n" + \
"	font-size: 12px;"+ "\n" + \
"	color: #333;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"/* SchemeEditWidget"+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"SchemeEditWidget {"+ "\n" + \
"	font-family: \"Helvetica\";"+ "\n" + \
"	font-size: 12px;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"/* Quick Menu "+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"QuickMenu {"+ "\n" + \
"	background-color: #E9EFF2;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu QFrame#menu-frame {"+ "\n" + \
"	border: 1px solid #9CACB4;"+ "\n" + \
"    border-radius: 3px;"+ "\n" + \
"    background-color: #E9EFF2;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu QTreeView::item {"+ "\n" + \
"	border-bottom: 1px solid #e9eff2;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu QTreeView::item:selected {"+ "\n" + \
"	background: qlineargradient("+ "\n" + \
"		x1: 0, y1: 0, x2: 0, y2: 1,"+ "\n" + \
"		stop: 0 #688EF6,"+ "\n" + \
"		stop: 0.5 #4047f4,"+ "\n" + \
"		stop: 1.0 #2D68F3"+ "\n" + \
"	);"+ "\n" + \
"	color: white;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu TabBarWidget QToolButton {"+ "\n" + \
"	height: 25px;"+ "\n" + \
"	border-bottom: 1px solid palette(dark);"+ "\n" + \
"	padding-right: 5px;"+ "\n" + \
"	padding-left: 5px;"+ "\n" + \
"	qproperty-showMenuIndicator_: true;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu TabBarWidget QToolButton#search-tab-button {"+ "\n" + \
"	background-color: #9CACB4;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu TabBarWidget QToolButton:menu-indicator {"+ "\n" + \
"	image: url(canvas_icons:/arrow-right.svg);"+ "\n" + \
"	subcontrol-position: center right;"+ "\n" + \
"	height: 8px;"+ "\n" + \
"	width: 8px;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"/* Quick Menu search line edit"+ "\n" + \
" */"+ "\n" + \
""+ "\n" + \
"QuickMenu QLineEdit {"+ "\n" + \
"    height: 25px;"+ "\n" + \
"    margin: 0px;"+ "\n" + \
"    padding: 0px;"+ "\n" + \
"    border: 1px solid #9CACB4;"+ "\n" + \
"    border-radius: 3px;"+ "\n" + \
"    background-color: white;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu QLineEdit:focus {"+ "\n" + \
"    border: 2px solid #9CACB4;"+ "\n" + \
"    border-radius: 2px;"+ "\n" + \
"}"+ "\n" + \
""+ "\n" + \
"QuickMenu QLineEdit QToolButton {"+ "\n" + \
"	qproperty-flat_: false;"+ "\n" + \
"    height: 25px;"+ "\n" + \
"    border: 1px solid #9CACB4;"+ "\n" + \
"    border-top-left-radius: 3px;"+ "\n" + \
"    border-bottom-left-radius: 3px;"+ "\n" + \
"    background-color: #9CACB4;"+ "\n" + \
"    padding: 0px;"+ "\n" + \
"    margin: 0px;"+ "\n" + \
"    icon-size: 23px;"+ "\n" + \
"}"
