"""
SUCLEPY — Smart Universal Cleaner Library for Python
----------------------------------------------------
Clean Data. Clear Insights.

Developed by: Subodh Kumar Yadav
GitHub: https://github.com/subodhkryadav
LinkedIn: https://www.linkedin.com/in/subodh-kumar-yadav-522828293/
"""

# Updated Version for new release
__version__ = "1.0.1"
__author__ = "Subodh Kumar Yadav"

# Core functionality imports (public API)
from .main import auto_clean
from .config.settings import set_rules
from .core.cleaner import Cleaner
from .core.reporter import CleaningReport

# Alias for docs alignment: sp.config() → set_rules()
config = set_rules

# Expose public functions + classes
__all__ = [
    "auto_clean",        # main entry point for cleaning
    "config",            # alias for global config
    "set_rules",         # actual config function
    "Cleaner",           # direct cleaner access
    "CleaningReport"     # access report class
]
