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

##########################################################################
# UTILITY FROM WAVEPY

from aps.common.logger import get_registered_logger_instance
from aps.common.widgets.context_widget import PlottingProperties as PlottingProperties, WIDGET_FIXED_WIDTH # to ensure
from aps.wavepy2.util.common import common_tools


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

import pickle
# %%
def load_pickle_surf(fname):

    file = open(fname, 'rb')
    figx = pickle.load(file)

    data = figx.axes[0].images[0].get_array().data
    [xi, xf, yi, yf] = figx.axes[0].images[0].get_extent()

    #ax = figx.axes[0].images[0].get_axes()
    #title  = figx.axes[0].images[0].axes.properties()['title']
    #xlabel = figx.axes[0].images[0].axes.properties()['xlabel']
    #ylabel = figx.axes[0].images[0].axes.properties()['ylabel']
    #cmap   = figx.axes[0].images[0].properties()['cmap'].name

    xxGrid, yyGrid = np.meshgrid(np.linspace(xi, xf, data.shape[1]),
                                 np.linspace(yi, yf, data.shape[0]),
                                 indexing='xy')

    return data, xxGrid, yyGrid



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

