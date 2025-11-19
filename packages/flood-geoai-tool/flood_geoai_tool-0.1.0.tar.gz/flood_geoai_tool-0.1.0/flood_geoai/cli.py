"""
Command-line interface for Flood GeoAI Tool.
"""

import argparse
import sys
import os
from .core import FloodGeoAITool

def main():
    parser = argparse.ArgumentParser(description='Flood GeoAI Tool - Flood Risk Assessment')
    
    parser.add_argument('--model', '-m', required=True, help='Path to trained model')
    parser.add_argument('--image', '-i', required=True, help='Path to satellite image')
    parser.add_argument('--buildings', '-b', required=True, help='Path to building footprints')
    parser.add_argument('--output', '-o', default='./output', help='Output directory')
    parser.add_argument('--confidence', '-c', type=float, default=0.5, 
                       help='Confidence threshold for water detection')
    
    args = parser.parse_args()
    
    try:
        # Initialize tool
        tool = FloodGeoAITool(args.model)
        
        # Run analysis
        results = tool.run_analysis(
            satellite_image_path=args.image,
            building_footprints_path=args.buildings,
            output_dir=args.output,
            confidence_threshold=args.confidence
        )
        
        print("Analysis completed successfully!")
        print(f"Results saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()