# read version from installed package
from importlib.metadata import version
__version__ = version("geovizir")

from geovizir.dplyr import *
from geovizir.features import *
from geovizir.scales import *
from geovizir.data import *
