import rasterio
import geopandas as gpd
import numpy as np
from shapely.geometry import shape
from skimage import measure
import torch
import os
import json

class FloodGeoAITool:
    def __init__(self, model_path):
        """
        Initialize the GeoAI tool with your trained model.
        """
        self.model_path = model_path
        self.model = self.load_model()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
    def load_model(self):
        """
        Load your trained flood detection model.
        """
        try:
            # Load PyTorch model
            model = torch.load(self.model_path, map_location='cpu')
            model.eval()
            print("Model loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def preprocess_image(self, image_array):
        """
        Preprocess the satellite image for the model.
        """
        # Normalize based on data type
        if image_array.dtype == np.uint16:
            image_array = image_array / 65535.0
        elif image_array.dtype == np.uint8:
            image_array = image_array / 255.0
            
        # Ensure correct shape: (channels, height, width)
        if len(image_array.shape) == 2:
            image_array = np.expand_dims(image_array, axis=0)
        elif len(image_array.shape) == 3:
            if image_array.shape[2] <= 4:  # If channels are last
                image_array = np.moveaxis(image_array, 2, 0)
        
        return image_array.astype(np.float32)

    def detect_surface_water(self, image_path, confidence_threshold=0.5):
        """
        Run your trained model on the satellite image to detect water.
        """
        with rasterio.open(image_path) as src:
            image_data = src.read()
            transform = src.transform
            crs = src.crs
        
        print(f"Input image shape: {image_data.shape}")
        
        # Preprocess the image
        processed_image = self.preprocess_image(image_data)
        print(f"Processed image shape: {processed_image.shape}")
        
        # Convert to tensor
        input_tensor = torch.from_numpy(processed_image).unsqueeze(0)
        
        # Run inference
        with torch.no_grad():
            if self.model is not None:
                output = self.model(input_tensor)
                
                # Handle model output
                if isinstance(output, torch.Tensor):
                    if output.shape[1] == 1:  # Binary segmentation
                        predictions = torch.sigmoid(output).squeeze().numpy()
                        water_mask = (predictions > confidence_threshold).astype(np.uint8)
                    else:  # Multi-class segmentation
                        predictions = torch.softmax(output, dim=1).squeeze().numpy()
                        water_mask = (np.argmax(predictions, axis=0) == 1).astype(np.uint8)
                else:
                    raise ValueError("Model output format not recognized")
            else:
                # Fallback water detection
                print("Using fallback water detection")
                water_mask = self.fallback_water_detection(processed_image)
        
        print(f"Water pixels detected: {np.sum(water_mask)} / {water_mask.size}")
        return water_mask, transform, crs

    def fallback_water_detection(self, image_data):
        """
        Simple fallback using NDWI-like calculation.
        """
        if image_data.shape[0] >= 4:
            green = image_data[1]  # Green band
            nir = image_data[3]    # NIR band
        else:
            green = image_data[1]  # Green band
            nir = image_data[0]    # Red band
            
        ndwi = (green - nir) / (green + nir + 1e-8)
        water_mask = (ndwi > 0.2).astype(np.uint8)
        return water_mask

    def polygonize_water_mask(self, water_mask, transform, crs, min_area=100):
        """
        Convert raster water mask to vector polygons.
        """
        contours = measure.find_contours(water_mask, 0.5)
        
        polygons = []
        for contour in contours:
            coords = [rasterio.transform.xy(transform, row, col) for row, col in contour]
            polygon = shape({"type": "Polygon", "coordinates": [coords]})
            
            if polygon.area >= min_area:
                polygons.append(polygon)
        
        if polygons:
            water_gdf = gpd.GeoDataFrame({
                'id': range(len(polygons)),
                'class': ['water'] * len(polygons),
                'area_sq_m': [poly.area for poly in polygons],
                'geometry': polygons
            }, crs=crs)
            
            return water_gdf
        else:
            # Return empty GeoDataFrame with correct structure
            return gpd.GeoDataFrame(columns=['id', 'class', 'area_sq_m', 'geometry'], crs=crs)

    def analyze_flood_impact(self, water_polygons_gdf, buildings_gdf):
        """
        Analyze which buildings are affected by water and calculate statistics.
        """
        # Initialize flood_status column with 'dry'
        buildings_gdf = buildings_gdf.copy()
        buildings_gdf['flood_status'] = 'dry'
        
        if water_polygons_gdf.empty:
            print("No water detected in the image.")
            stats = {
                'total_buildings': len(buildings_gdf),
                'flooded_buildings': 0,
                'flooded_percentage': 0.0,
                'total_water_area': 0.0
            }
            return buildings_gdf, stats
        
        # Create a unified geometry of all water bodies
        water_union = water_polygons_gdf.unary_union
        
        # Find buildings that intersect with water
        buildings_in_water_mask = buildings_gdf.geometry.intersects(water_union)
        buildings_in_water = buildings_gdf[buildings_in_water_mask].copy()
        
        # Update flood status
        buildings_gdf.loc[buildings_in_water_mask, 'flood_status'] = 'flooded'
        
        # Calculate statistics
        stats = {
            'total_buildings': len(buildings_gdf),
            'flooded_buildings': len(buildings_in_water),
            'flooded_percentage': (len(buildings_in_water) / len(buildings_gdf)) * 100 if len(buildings_gdf) > 0 else 0,
            'total_water_area': water_polygons_gdf.geometry.area.sum()
        }
        
        print(f"Found {len(buildings_in_water)} flooded buildings out of {len(buildings_gdf)} total")
        return buildings_gdf, stats

    def generate_risk_map(self, buildings_gdf, water_polygons_gdf, buffer_distance=50):
        """
        Generate a flood risk map based on proximity to water.
        """
        buildings_gdf = buildings_gdf.copy()
        
        if water_polygons_gdf.empty:
            buildings_gdf['risk_level'] = 'low'
            return buildings_gdf
        
        water_union = water_polygons_gdf.unary_union
        
        # Create risk zones
        high_risk_zone = water_union.buffer(buffer_distance)
        medium_risk_zone = water_union.buffer(buffer_distance * 2).difference(high_risk_zone)
        
        def assign_risk(geometry, flood_status):
            # If already flooded, very high risk
            if flood_status == 'flooded':
                return 'very high'
            elif geometry.intersects(high_risk_zone):
                return 'high'
            elif geometry.intersects(medium_risk_zone):
                return 'medium'
            else:
                return 'low'
        
        # Apply risk assignment
        buildings_gdf['risk_level'] = buildings_gdf.apply(
            lambda row: assign_risk(row.geometry, row.flood_status), 
            axis=1
        )
        
        return buildings_gdf

    def run_analysis(self, satellite_image_path, building_footprints_path, output_dir="./output"):
        """
        Run the complete flood analysis pipeline.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print("Step 1: Detecting surface water...")
        water_mask, transform, crs = self.detect_surface_water(satellite_image_path)
        
        print("Step 2: Converting water mask to polygons...")
        water_polygons = self.polygonize_water_mask(water_mask, transform, crs)
        
        print("Step 3: Loading building footprints...")
        buildings = gpd.read_file(building_footprints_path)
        print(f"Loaded {len(buildings)} buildings")
        
        # Ensure same CRS
        if buildings.crs != crs:
            print(f"Converting buildings CRS from {buildings.crs} to {crs}")
            buildings = buildings.to_crs(crs)
        
        print("Step 4: Analyzing flood impact...")
        buildings_with_status, stats = self.analyze_flood_impact(water_polygons, buildings)
        
        print("Step 5: Generating risk map...")
        risk_map = self.generate_risk_map(buildings_with_status, water_polygons)
        
        print("Step 6: Saving results...")
        # Save results
        if not water_polygons.empty:
            water_polygons.to_file(f"{output_dir}/detected_water.shp")
        else:
            print("No water polygons to save")
            
        risk_map.to_file(f"{output_dir}/flood_risk_map.shp")
        
        # Save flooded buildings separately - FIXED: Check if column exists
        if 'flood_status' in risk_map.columns:
            flooded_buildings = risk_map[risk_map['flood_status'] == 'flooded']
            if not flooded_buildings.empty:
                flooded_buildings.to_file(f"{output_dir}/flooded_buildings.shp")
                print(f"Saved {len(flooded_buildings)} flooded buildings")
            else:
                print("No flooded buildings to save")
        else:
            print("Warning: 'flood_status' column not found in risk map")
        
        # Save statistics
        with open(f"{output_dir}/flood_statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total buildings analyzed: {stats['total_buildings']}")
        print(f"Flooded buildings: {stats['flooded_buildings']}")
        print(f"Flood percentage: {stats['flooded_percentage']:.2f}%")
        print(f"Total water area: {stats['total_water_area']:.2f} sq units")
        print(f"Results saved to: {output_dir}")
        print("="*50)
        
        return risk_map, water_polygons, stats