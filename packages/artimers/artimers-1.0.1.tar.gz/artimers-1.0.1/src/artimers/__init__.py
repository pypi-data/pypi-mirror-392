__version__ = "1.0.1"

from .SimpleTimer import SimpleTimer
from .AdvancedTimer import AdvancedTimer
from .GlobalTimer import GlobalTimer as Timer

__all__ = ['SimpleTimer', 'Timer']