
from __future__ import absolute_import

from . import configure
configure.check_config()

from .core import *

__all__ = ['configure']

__author__ = ['Christopher Gordon <chris.gordon@dfo-mpo.gc.ca>']

__version__ = '0.0.1'

