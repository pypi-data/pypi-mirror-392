"""
Utility functions for Flood GeoAI Tool.
"""

import os
import json

def ensure_directory(path):
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)
    return path

def save_json(data, filepath):
    """Save data as JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(filepath):
    """Load data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)