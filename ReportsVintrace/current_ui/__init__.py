"""
Current UI Reports Package
Report downloaders for the current/new Vintrace UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""

# Import report classes
from .vessels_report import VesselsReport
from .barrel_report import BarrelReport
# from .fruit_report import FruitReport  # TODO
# from .analysis_report import AnalysisReport  # TODO

__all__ = [
    'VesselsReport',
    'BarrelReport',
    # 'FruitReport',  # TODO
    # 'AnalysisReport',  # TODO
]
