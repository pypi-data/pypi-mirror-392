import os
import sys
import warnings

from setuptools import setup, Extension
from Cython.Build import cythonize


try:
    import numpy
except ImportError:
    warnings.warn(
        "numpy must be installed to build the filtering module.")
    sys.exit(1)

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

CYTHON_SOURCE_DIR = "src"
CYTHON_SOURCE_FILES = ["_region_filter.pyx"]
EXTRA_COMPILE_ARGS = [
    "-Wall",
    "-Wextra",
    "-Wno-int-conversion",
    "-std=gnu99",
]

if sys.platform.startswith("win"):
    EXTRA_COMPILE_ARGS = []

# importing these extension modules is tested in `.github/workflows/build.yml`; 
# when adding new modules here, make sure to add them to the `test_command` entry there
extensions = [
    Extension(
        "stregion._region_filter",
        [os.path.join(CYTHON_SOURCE_DIR, x) for x in CYTHON_SOURCE_FILES],
        include_dirs=[
            CYTHON_SOURCE_DIR,
            numpy_include,
        ],
        extra_compile_args=EXTRA_COMPILE_ARGS,
    ),
]

setup(ext_modules=cythonize(extensions))
