"""
Initialization for cosmicqc package
"""

from .analyze import find_outliers, identify_outliers, label_outliers
from .detection import ContaminationDetector

# note: version placeholder is updated during build
# by poetry-dynamic-versioning.
__version__ = "1.0.0"
