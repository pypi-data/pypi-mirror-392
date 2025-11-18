"""
MAE - Modern Automation for EMS
Web scraping toolkit for telecom EMS portals
"""

from .ems_automation import EmsAutomation
from .ems_walk import EmsWalk, TrackedEmsWalk
from . import xpath_builder as xp

__version__ = "1.0.0"
__all__ = ["EmsAutomation", "EmsWalk", "TrackedEmsWalk", "xp"]
