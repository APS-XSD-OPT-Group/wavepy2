#! /usr/bin/env python3

import os

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'wavepy2'

VERSION = '0.0.1'
ISRELEASED = False

DESCRIPTION = 'Wavepy 2 library'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Luca Rebuffi, Xianbo Shi, Zhi Qiao, Walan Grizolli'
AUTHOR_EMAIL = 'lrebuffi@anl.gov'
URL = 'https://github.com/aps-xsd-opt-group/wavepy2'
DOWNLOAD_URL = 'https://github.com/aps-xsd-opt-group/wavepy2'
MAINTAINER = 'XSD-OPT Group @ APS-ANL'
MAINTAINER_EMAIL = 'lrebuffi@anl.gov'
LICENSE = 'BSD-3'

KEYWORDS = ['dictionary',
    'glossary',
    'synchrotron'
    'simulation',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering :: Visualization',
    'Intended Audience :: Science/Research',
]

INSTALL_REQUIRES = (
    'setuptools',
    'numpy',
    'scipy',
    'h5py',
    'pyfftw',
    'scikit-image',
    'termcolor',
    'tifffile',
    'pandas',
)

SETUP_REQUIRES = (
    'setuptools',
)

PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
}


def setup_package():

    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        zip_safe=False,
        include_package_data=True,
        install_requires=INSTALL_REQUIRES,
        setup_requires=SETUP_REQUIRES,
    )

if __name__ == '__main__':
    setup_package()
