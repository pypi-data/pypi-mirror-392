"""
Flood GeoAI Tool - A Python package for flood risk assessment using satellite imagery.
"""

__version__ = "0.1.0"
__author__ = "Hatim Nuh"
__email__ = "hatimoo22@live.com"

from .core import FloodGeoAITool
from .cli import main

__all__ = ["FloodGeoAITool", "main"]