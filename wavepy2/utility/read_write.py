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

"""
Module for importing data files.
"""

__author__ = "Doga Gursoy, Francesco De Carlo"
__copyright__ = "Copyright (c) 2020, UChicago Argonne, LLC."

import os, numpy, six, tifffile

def read_tiff(fname, slc=None):
    """
    Read data from tiff file.

    Parameters
    ----------
    fname : str
        String defining the path of file or file name.
    slc : sequence of tuples, optional
        Range of values for slicing data in each axis.
        ((start_1, end_1, step_1), ... , (start_N, end_N, step_N))
        defines slicing parameters for each axis of the data matrix.

    Returns
    -------
    ndarray
        Output 2D image.
    """
    fname = __check_read(fname)

    try:
        arr = tifffile.imread(fname)
    except IOError:
        raise ValueError('No such file or directory: %s', fname)

    return __slice_array(arr, slc)

def write_tiff(data, fname='tmp/data.tiff', dtype=None, overwrite=False):
    """
    Write image data to a tiff file.

    Parameters
    ----------
    data : ndarray
        Array data to be saved.
    fname : str
        File name to which the data is saved. ``.tiff`` extension
        will be appended if it does not already have one.
    dtype : data-type, optional
        By default, the data-type is inferred from the input data.
    overwrite: bool, optional
        if True, overwrites the existing file if the file exists.
    """
    fname, data = __init_write(data, fname, '.tiff', dtype, overwrite)

    tifffile.imsave(fname, data)


##########################################################################
# PRIVATE

def __get_body(fname, digit=None):
    """
    Get file name after extension removed.
    """
    body = os.path.splitext(fname)[0]
    if digit is not None: body = ''.join(body[:-digit])

    return body

def __get_extension(fname):
    """
    Get file extension.
    """
    return '.' + fname.split(".")[-1]

def __check_read(fname):
    known_extensions = ['.edf', '.tiff', '.tif', '.h5', '.hdf', '.npy']

    if not isinstance(fname, six.string_types):
        raise ValueError('File name must be a string')
    else:
        if __get_extension(fname) not in known_extensions:
            raise ValueError('Unknown file extension')

    return os.path.abspath(fname)

def __fix_slice(slc):
    """
    Fix up a slc object to be tuple of slices.
    slc = None is treated as no slc
    slc is container and each element is converted into a slice object
    None is treated as slice(None)

    Parameters
    ----------
    slc : None or sequence of tuples
        Range of values for slicing data in each axis.
        ((start_1, end_1, step_1), ... , (start_N, end_N, step_N))
        defines slicing parameters for each axis of the data matrix.
    """
    if slc is None: return None  # need arr shape to create slice

    fixed_slc = list()

    for s in slc:
        if not isinstance(s, slice):
            # create slice object
            if s is None or isinstance(s, int):
                # slice(None) is equivalent to np.s_[:]
                # numpy will return an int when only an int is passed to
                # np.s_[]
                s = slice(s)
            else:
                s = slice(*s)
        fixed_slc.append(s)

    return tuple(fixed_slc)

def __slice_array(arr, slc):
    """
    Perform slicing on ndarray.

    Parameters
    ----------
    arr : ndarray
        Input array to be sliced.
    slc : sequence of tuples
        Range of values for slicing data in each axis.
        ((start_1, end_1, step_1), ... , (start_N, end_N, step_N))
        defines slicing parameters for each axis of the data matrix.

    Returns
    -------
    ndarray
        Sliced array.
    """
    if slc is None: return arr[:]

    return arr[__fix_slice(slc)]

def __init_dirs(fname):
    """
    Initialize directories for saving output files.

    Parameters
    ----------
    fname : str
        Output file name.
    """
    dname = os.path.dirname(os.path.abspath(fname))
    if not os.path.exists(dname):
        os.makedirs(dname)


def __suggest_new_fname(fname, digit):
    """
    Suggest new string with an attached (or increased) value indexing
    at the end of a given string.

    For example if "myfile.tiff" exist, it will return "myfile-1.tiff".

    Parameters
    ----------
    fname : str
        Output file name.
    digit : int, optional
        Number of digits in indexing stacked files.

    Returns
    -------
    str
        Indexed new string.
    """
    if os.path.isfile(fname):
        body = __get_body(fname)
        ext = __get_extension(fname)

        indq = 1
        file_exist = False

        while not file_exist:
            fname = body + '-' + '{0:0={1}d}'.format(indq, digit) + ext
            if not os.path.isfile(fname):
                file_exist = True
            else:
                indq += 1

    return fname

def __as_dtype(arr, dtype):
    if not arr.dtype == dtype: arr = numpy.array(arr, dtype=dtype)

    return arr

def __init_write(arr, fname, ext, dtype, overwrite):
    if not (isinstance(fname, six.string_types)):
        fname = 'tmp/data' + ext
    elif not fname.endswith(ext):
        fname = fname + ext

    fname = os.path.abspath(fname)

    if not overwrite: fname = __suggest_new_fname(fname, digit=1)

    __init_dirs(fname)

    if dtype is not None: arr = __as_dtype(arr, dtype)

    return fname, arr

