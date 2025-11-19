"""
Tests for Flood GeoAI Tool.
"""

import unittest
import tempfile
import os

class TestFloodGeoAI(unittest.TestCase):
    
    def test_import(self):
        """Test that the package can be imported."""
        try:
            from flood_geoai import FloodGeoAITool
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import FloodGeoAITool")
    
    def test_dependencies(self):
        """Test that all dependencies are available."""
        try:
            import rasterio
            import geopandas
            import torch
            import skimage
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Missing dependency: {e}")

if __name__ == '__main__':
    unittest.main()