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

from PyQt5.QtWidgets import QMainWindow

# ---------------------------------------------------------------------------
# WIDGET FOR SCRIPTING

class DefaultMainWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.__container_widget = QWidget()
        self.setCentralWidget(self.__container_widget)

    def get_container_widget(self):
        return self.__container_widget

# ---------------------------------------------------------------------------
# WIDGETS UTILS FROM OASYS

from PyQt5.QtWidgets import QWidget, QGroupBox, QTabWidget, QScrollArea, QLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt

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

def widgetBox(widget, box=None, orientation='vertical', margin=None, spacing=4, **misc):
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
    return b

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
        if isinstance(space, bool): __separator(widget)
        else: __separator(widget, space, space)

def __separator(widget, width=4, height=4):
    sep = QWidget(widget)
    if widget.layout() is not None: widget.layout().addWidget(sep)
    sep.setFixedSize(width, height)
    return sep


