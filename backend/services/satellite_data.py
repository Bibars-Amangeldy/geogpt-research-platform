"""
Satellite Data Services - Real Satellite Imagery Integration
Based on opengeos/leafmap and NASA Earth Data patterns
Provides access to Sentinel, Landsat, MODIS, and other satellite data
"""

import asyncio
import math
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import json

# Try to import aiohttp, but it's optional for demo mode
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("Note: aiohttp not installed. Using simulated satellite data.")


# ==============================================================
# SATELLITE DATA SOURCES AND ENDPOINTS
# ==============================================================

# STAC API endpoints
STAC_ENDPOINTS = {
    "planetary_computer": "https://planetarycomputer.microsoft.com/api/stac/v1",
    "element84_earth_search": "https://earth-search.aws.element84.com/v1",
    "usgs_stac": "https://landsatlook.usgs.gov/stac-server"
}

# NASA CMR STAC
NASA_CMR_STAC = "https://cmr.earthdata.nasa.gov/stac"

# Copernicus Data Space (Sentinel)
COPERNICUS_API = "https://dataspace.copernicus.eu/odata/v1"


# ==============================================================
# SENTINEL DATA COLLECTIONS
# ==============================================================

SENTINEL_COLLECTIONS = {
    "sentinel-2-l2a": {
        "name": "Sentinel-2 L2A",
        "description": "Surface reflectance imagery",
        "resolution_m": 10,
        "bands": ["B02", "B03", "B04", "B08", "B11", "B12"],
        "band_names": {
            "B02": "Blue",
            "B03": "Green",
            "B04": "Red",
            "B08": "NIR",
            "B11": "SWIR1",
            "B12": "SWIR2"
        },
        "revisit_days": 5,
        "use_cases": ["agriculture", "forestry", "land_cover", "water"]
    },
    "sentinel-1-grd": {
        "name": "Sentinel-1 GRD",
        "description": "SAR Ground Range Detected",
        "resolution_m": 10,
        "bands": ["VV", "VH"],
        "band_names": {
            "VV": "VV Polarization",
            "VH": "VH Polarization"
        },
        "revisit_days": 6,
        "use_cases": ["flood_mapping", "ice_monitoring", "ship_detection"]
    },
    "sentinel-5p-l2": {
        "name": "Sentinel-5P L2",
        "description": "Atmospheric composition",
        "resolution_m": 5500,
        "bands": ["NO2", "CH4", "CO", "O3", "SO2", "HCHO"],
        "band_names": {
            "NO2": "Nitrogen Dioxide",
            "CH4": "Methane",
            "CO": "Carbon Monoxide",
            "O3": "Ozone",
            "SO2": "Sulfur Dioxide",
            "HCHO": "Formaldehyde"
        },
        "revisit_days": 1,
        "use_cases": ["air_quality", "climate", "emissions"]
    },
    "sentinel-3-olci": {
        "name": "Sentinel-3 OLCI",
        "description": "Ocean and Land Color",
        "resolution_m": 300,
        "bands": ["chl_a", "tsm", "cdom"],
        "band_names": {
            "chl_a": "Chlorophyll-a",
            "tsm": "Total Suspended Matter",
            "cdom": "Colored Dissolved Organic Matter"
        },
        "revisit_days": 2,
        "use_cases": ["water_quality", "ocean_color", "vegetation"]
    }
}

# MODIS Products for Kazakhstan
MODIS_PRODUCTS = {
    "MOD11A2": {
        "name": "Land Surface Temperature",
        "description": "8-day LST at 1km resolution",
        "resolution_m": 1000,
        "temporal_resolution": "8-day",
        "parameters": ["LST_Day", "LST_Night", "Emissivity"],
        "use_cases": ["urban_heat", "agriculture", "climate"]
    },
    "MOD13Q1": {
        "name": "Vegetation Indices",
        "description": "16-day NDVI/EVI at 250m",
        "resolution_m": 250,
        "temporal_resolution": "16-day",
        "parameters": ["NDVI", "EVI", "NIR_reflectance"],
        "use_cases": ["vegetation_health", "agriculture", "drought"]
    },
    "MCD64A1": {
        "name": "Burned Area",
        "description": "Monthly burned area at 500m",
        "resolution_m": 500,
        "temporal_resolution": "monthly",
        "parameters": ["Burn_Date", "Burn_Confidence", "First_Day", "Last_Day"],
        "use_cases": ["fire_monitoring", "land_cover_change"]
    },
    "MOD10A2": {
        "name": "Snow Cover",
        "description": "8-day snow cover at 500m",
        "resolution_m": 500,
        "temporal_resolution": "8-day",
        "parameters": ["Snow_Cover", "Snow_Albedo"],
        "use_cases": ["hydrology", "climate", "glaciers"]
    }
}


# ==============================================================
# KAZAKHSTAN SPECIFIC SATELLITE DATA
# ==============================================================

KAZAKHSTAN_SATELLITE_SCENES = {
    "almaty_urban_2024": {
        "name": "Almaty Urban Area - 2024",
        "coordinates": [76.9458, 43.2220],
        "bounds": [[76.75, 43.10], [77.15, 43.35]],
        "collection": "sentinel-2-l2a",
        "date": "2024-08-15",
        "cloud_cover": 5,
        "tile_url": "https://sentinel-hub.com/tiles/almaty",
        "products": {
            "true_color": "RGB(B04, B03, B02)",
            "false_color": "RGB(B08, B04, B03)",
            "ndvi": "(B08-B04)/(B08+B04)",
            "urban": "RGB(B12, B11, B04)"
        }
    },
    "astana_development_2024": {
        "name": "Astana Development - 2024",
        "coordinates": [71.4491, 51.1801],
        "bounds": [[71.25, 51.05], [71.65, 51.30]],
        "collection": "sentinel-2-l2a",
        "date": "2024-07-20",
        "cloud_cover": 3,
        "products": {
            "true_color": "RGB(B04, B03, B02)",
            "urban_expansion": "RGB(B12, B08, B04)"
        }
    },
    "balkhash_water_2024": {
        "name": "Lake Balkhash Water Level - 2024",
        "coordinates": [75.0, 46.5],
        "bounds": [[73.0, 45.5], [79.0, 47.5]],
        "collection": "sentinel-2-l2a",
        "date": "2024-09-01",
        "cloud_cover": 8,
        "products": {
            "water_index": "(B03-B08)/(B03+B08)",
            "chlorophyll": "(B04-B02)/(B04+B02)",
            "turbidity": "B04/B02"
        }
    },
    "tengiz_oil_2024": {
        "name": "Tengiz Oil Field Monitoring - 2024",
        "coordinates": [53.45, 46.23],
        "bounds": [[52.5, 45.5], [54.5, 47.0]],
        "collection": "sentinel-1-grd",
        "date": "2024-10-15",
        "products": {
            "oil_spill_detection": "VV - VH difference",
            "infrastructure": "VV backscatter"
        }
    },
    "tian_shan_glaciers_2024": {
        "name": "Tian Shan Glaciers - 2024",
        "coordinates": [77.0833, 43.0500],
        "bounds": [[76.8, 42.8], [77.4, 43.3]],
        "collection": "sentinel-2-l2a",
        "date": "2024-09-10",
        "cloud_cover": 12,
        "products": {
            "snow_ice": "RGB(B12, B11, B04)",
            "glacier_extent": "(B03-B11)/(B03+B11)",
            "debris_cover": "B12/B11"
        }
    }
}


class SatelliteDataService:
    """
    Provides satellite data access and processing
    Based on best practices from opengeos/leafmap and NASA Earth Data
    """
    
    def __init__(self, planetary_computer_key: str = None):
        self.pc_key = planetary_computer_key
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    # ==============================================================
    # SATELLITE TILE LAYERS
    # ==============================================================
    
    def get_available_collections(self) -> Dict[str, Any]:
        """Get list of available satellite collections"""
        return {
            "sentinel": SENTINEL_COLLECTIONS,
            "modis": MODIS_PRODUCTS,
            "available_scenes": list(KAZAKHSTAN_SATELLITE_SCENES.keys())
        }
    
    def get_satellite_layer(self, scene_id: str, product: str = "true_color") -> Dict[str, Any]:
        """
        Get satellite layer configuration for map display
        Returns a tile layer specification
        """
        scene = KAZAKHSTAN_SATELLITE_SCENES.get(scene_id)
        if not scene:
            return None
        
        # Generate tile URL (in production, this would be from actual STAC/COG)
        tile_base = f"https://tiles.planet.com/data/v1/layers/{scene_id}"
        
        return {
            "id": f"satellite-{scene_id}-{product}",
            "name": f"{scene['name']} - {product.replace('_', ' ').title()}",
            "type": "raster",
            "source": {
                "type": "raster",
                "tiles": [
                    f"{tile_base}/{{z}}/{{x}}/{{y}}.png?product={product}"
                ],
                "tileSize": 256,
                "bounds": [
                    scene["bounds"][0][0], scene["bounds"][0][1],
                    scene["bounds"][1][0], scene["bounds"][1][1]
                ],
                "attribution": f"© Copernicus Sentinel Data {scene['date'][:4]}"
            },
            "paint": {
                "raster-opacity": 0.85
            },
            "metadata": {
                "collection": scene["collection"],
                "date": scene["date"],
                "cloud_cover": scene["cloud_cover"],
                "product": product,
                "formula": scene["products"].get(product, "RGB")
            }
        }
    
    # ==============================================================
    # NDVI/VEGETATION ANALYSIS
    # ==============================================================
    
    def calculate_ndvi_layer(self, center: List[float], 
                             radius_km: float = 50) -> Dict[str, Any]:
        """
        Generate NDVI layer for vegetation analysis
        Simulates Sentinel-2 NDVI calculation
        """
        features = []
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Generate NDVI grid
        resolution = 0.01  # ~1km resolution
        lat_range = int(radius_km / 111)
        lng_range = int(radius_km / (111 * math.cos(math.radians(center[1]))))
        
        for i in range(-lat_range, lat_range + 1):
            for j in range(-lng_range, lng_range + 1):
                lat = center[1] + i * resolution
                lng = center[0] + j * resolution
                
                # Calculate NDVI based on location characteristics
                ndvi = self._estimate_ndvi(lng, lat)
                
                # Color mapping
                color = self._ndvi_to_color(ndvi)
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "ndvi": round(ndvi, 3),
                        "color": color,
                        "vegetation_class": self._ndvi_class(ndvi),
                        "weight": max(0.1, (ndvi + 0.5) / 1.5)
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                })
        
        return {
            "id": "ndvi-analysis",
            "type": "heatmap",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": features
                }
            },
            "paint": {
                "heatmap-weight": ["get", "weight"],
                "heatmap-intensity": 1.2,
                "heatmap-color": [
                    "interpolate", ["linear"], ["heatmap-density"],
                    0, "rgba(255,255,255,0)",
                    0.1, "#d73027",
                    0.2, "#fc8d59",
                    0.3, "#fee08b",
                    0.5, "#d9ef8b",
                    0.7, "#91cf60",
                    0.9, "#1a9850"
                ],
                "heatmap-radius": 15,
                "heatmap-opacity": 0.8
            },
            "metadata": {
                "source": "Sentinel-2 NDVI Simulation",
                "timestamp": timestamp,
                "center": center,
                "radius_km": radius_km,
                "formula": "(B08-B04)/(B08+B04)"
            }
        }
    
    def _estimate_ndvi(self, lng: float, lat: float) -> float:
        """Estimate NDVI based on location"""
        # Higher NDVI in mountain foothills and river valleys
        # Lower in deserts and urban areas
        
        # Check if near mountains (Tian Shan)
        dist_to_mountains = math.sqrt((lng - 77)**2 + (lat - 43)**2)
        mountain_factor = max(0, 0.4 - dist_to_mountains * 0.05)
        
        # Check if in desert region (central Kazakhstan)
        if 60 < lng < 75 and 44 < lat < 48:
            base_ndvi = 0.1
        # Check if in steppe
        elif lat > 48:
            base_ndvi = 0.25
        # Southern regions
        elif lat < 44:
            base_ndvi = 0.2
        else:
            base_ndvi = 0.15
        
        # Add mountain vegetation boost
        ndvi = base_ndvi + mountain_factor
        
        # Add randomness
        ndvi += random.uniform(-0.1, 0.1)
        
        # Seasonal adjustment (assuming summer)
        month = datetime.now().month
        if month in [6, 7, 8]:  # Summer peak
            ndvi *= 1.3
        elif month in [12, 1, 2]:  # Winter low
            ndvi *= 0.3
        
        return max(-0.5, min(1.0, ndvi))
    
    def _ndvi_to_color(self, ndvi: float) -> str:
        """Convert NDVI to color"""
        if ndvi < -0.1:
            return "#2166ac"  # Water
        elif ndvi < 0.1:
            return "#d6604d"  # Bare soil/rock
        elif ndvi < 0.2:
            return "#f4a582"  # Sparse vegetation
        elif ndvi < 0.3:
            return "#fddbc7"  # Light vegetation
        elif ndvi < 0.4:
            return "#d1e5f0"  # Moderate vegetation
        elif ndvi < 0.5:
            return "#92c5de"  # Good vegetation
        elif ndvi < 0.6:
            return "#4393c3"  # Dense vegetation
        else:
            return "#1a9850"  # Very dense vegetation
    
    def _ndvi_class(self, ndvi: float) -> str:
        """Get vegetation class from NDVI"""
        if ndvi < -0.1:
            return "Water"
        elif ndvi < 0.1:
            return "Bare Soil/Rock"
        elif ndvi < 0.2:
            return "Sparse Vegetation"
        elif ndvi < 0.3:
            return "Grassland"
        elif ndvi < 0.5:
            return "Shrubland/Crops"
        elif ndvi < 0.7:
            return "Forest"
        else:
            return "Dense Forest"
    
    # ==============================================================
    # LAND SURFACE TEMPERATURE
    # ==============================================================
    
    def get_land_surface_temperature(self, center: List[float],
                                      radius_km: float = 100) -> Dict[str, Any]:
        """
        Generate Land Surface Temperature layer
        Simulates MODIS LST data
        """
        features = []
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Get current hour for diurnal variation
        hour = datetime.now().hour
        month = datetime.now().month
        
        resolution = 0.05  # ~5km resolution
        lat_range = int(radius_km / 111)
        lng_range = int(radius_km / (111 * math.cos(math.radians(center[1]))))
        
        for i in range(-lat_range, lat_range + 1, 5):
            for j in range(-lng_range, lng_range + 1, 5):
                lat = center[1] + i * resolution
                lng = center[0] + j * resolution
                
                # Calculate LST
                lst = self._estimate_lst(lng, lat, hour, month)
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "lst_celsius": round(lst, 1),
                        "lst_kelvin": round(lst + 273.15, 1),
                        "color": self._lst_to_color(lst),
                        "weight": max(0.1, (lst + 30) / 80)
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                })
        
        return {
            "id": "lst-analysis",
            "type": "heatmap",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": features
                }
            },
            "paint": {
                "heatmap-weight": ["get", "weight"],
                "heatmap-intensity": 1,
                "heatmap-color": [
                    "interpolate", ["linear"], ["heatmap-density"],
                    0, "rgba(255,255,255,0)",
                    0.1, "#313695",
                    0.2, "#4575b4",
                    0.3, "#74add1",
                    0.4, "#abd9e9",
                    0.5, "#e0f3f8",
                    0.6, "#fee090",
                    0.7, "#fdae61",
                    0.8, "#f46d43",
                    0.9, "#d73027",
                    1.0, "#a50026"
                ],
                "heatmap-radius": 30,
                "heatmap-opacity": 0.75
            },
            "metadata": {
                "source": "MODIS Land Surface Temperature Simulation",
                "timestamp": timestamp,
                "product": "MOD11A2",
                "unit": "Celsius"
            }
        }
    
    def _estimate_lst(self, lng: float, lat: float, hour: int, month: int) -> float:
        """Estimate Land Surface Temperature"""
        # Base temperature by latitude
        base_temp = 25 - abs(lat - 45) * 0.8
        
        # Seasonal variation
        if month in [6, 7, 8]:  # Summer
            base_temp += 20
        elif month in [12, 1, 2]:  # Winter
            base_temp -= 25
        elif month in [3, 4, 5]:  # Spring
            base_temp += 5
        else:  # Autumn
            base_temp += 5
        
        # Diurnal variation
        if 10 <= hour <= 14:  # Peak heating
            base_temp += 10
        elif 6 <= hour <= 9:
            base_temp += (hour - 6) * 2
        elif 15 <= hour <= 20:
            base_temp -= (hour - 14)
        else:  # Night
            base_temp -= 8
        
        # Urban heat island effect
        # Check if near major cities
        cities = [(76.9458, 43.2220), (71.4491, 51.1801)]  # Almaty, Astana
        for city_lng, city_lat in cities:
            dist = math.sqrt((lng - city_lng)**2 + (lat - city_lat)**2)
            if dist < 0.5:
                base_temp += 5 * (1 - dist * 2)
        
        # Elevation effect (higher = cooler)
        # Mountain regions
        dist_to_mountains = math.sqrt((lng - 77)**2 + (lat - 43)**2)
        if dist_to_mountains < 2:
            base_temp -= 15 * (1 - dist_to_mountains / 2)
        
        # Random variation
        base_temp += random.uniform(-3, 3)
        
        return base_temp
    
    def _lst_to_color(self, lst: float) -> str:
        """Convert LST to color"""
        if lst < -20:
            return "#313695"
        elif lst < -10:
            return "#4575b4"
        elif lst < 0:
            return "#74add1"
        elif lst < 10:
            return "#abd9e9"
        elif lst < 20:
            return "#e0f3f8"
        elif lst < 25:
            return "#ffffbf"
        elif lst < 30:
            return "#fee090"
        elif lst < 35:
            return "#fdae61"
        elif lst < 40:
            return "#f46d43"
        elif lst < 45:
            return "#d73027"
        else:
            return "#a50026"
    
    # ==============================================================
    # BURNED AREA / FIRE DATA
    # ==============================================================
    
    async def get_fire_data(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get fire/burned area data for Kazakhstan
        Simulates FIRMS active fire data
        """
        features = []
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Known fire-prone regions in Kazakhstan
        fire_regions = [
            {"center": [61.5, 50.5], "radius": 2, "name": "Western Steppe"},
            {"center": [70.0, 52.0], "radius": 1.5, "name": "Northern Grain Belt"},
            {"center": [77.5, 43.5], "radius": 0.5, "name": "Almaty Foothills"},
            {"center": [80.0, 44.0], "radius": 1, "name": "Eastern Mountains"},
            {"center": [65.0, 45.0], "radius": 2, "name": "Central Steppe"}
        ]
        
        for region in fire_regions:
            # Generate random number of fires
            num_fires = random.randint(0, 15)
            
            for _ in range(num_fires):
                lat = region["center"][1] + random.gauss(0, region["radius"] * 0.3)
                lng = region["center"][0] + random.gauss(0, region["radius"] * 0.4)
                
                # Fire properties
                frp = random.uniform(5, 150)  # Fire Radiative Power in MW
                confidence = random.randint(60, 100)
                brightness = 300 + frp * 0.5 + random.uniform(-20, 20)
                
                # Age of fire detection
                age_hours = random.randint(0, days_back * 24)
                detection_time = datetime.utcnow() - timedelta(hours=age_hours)
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "frp_mw": round(frp, 1),
                        "brightness_kelvin": round(brightness, 1),
                        "confidence": confidence,
                        "detection_time": detection_time.isoformat() + "Z",
                        "age_hours": age_hours,
                        "region": region["name"],
                        "color": self._frp_to_color(frp),
                        "radius": min(20, max(5, frp / 10))
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                })
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "MODIS/VIIRS Active Fire Detection Simulation",
                "timestamp": timestamp,
                "days_back": days_back,
                "total_fires": len(features),
                "product": "FIRMS"
            }
        }
    
    def _frp_to_color(self, frp: float) -> str:
        """Convert Fire Radiative Power to color"""
        if frp < 20:
            return "#fde047"  # Low
        elif frp < 50:
            return "#fb923c"  # Moderate
        elif frp < 100:
            return "#ef4444"  # High
        else:
            return "#991b1b"  # Very high
    
    # ==============================================================
    # SNOW COVER DATA
    # ==============================================================
    
    def get_snow_cover(self, bounds: Dict = None) -> Dict[str, Any]:
        """
        Get snow cover data for Kazakhstan
        Simulates MODIS snow cover product
        """
        features = []
        timestamp = datetime.utcnow().isoformat() + "Z"
        month = datetime.now().month
        
        # Snow cover varies by season and elevation
        is_winter = month in [11, 12, 1, 2, 3]
        is_transition = month in [4, 10]
        
        # Define snow regions
        if is_winter:
            # Winter - extensive snow cover
            regions = [
                {"bounds": [[50, 48], [90, 56]], "coverage": 0.9, "name": "Northern Kazakhstan"},
                {"bounds": [[76, 42], [81, 45]], "coverage": 1.0, "name": "Tian Shan"},
                {"bounds": [[50, 42], [75, 48]], "coverage": 0.6, "name": "Central Kazakhstan"},
            ]
        elif is_transition:
            # Transition - partial snow
            regions = [
                {"bounds": [[50, 52], [90, 56]], "coverage": 0.5, "name": "Northern Kazakhstan"},
                {"bounds": [[76, 42], [81, 45]], "coverage": 0.8, "name": "Tian Shan"},
            ]
        else:
            # Summer - only mountain snow
            regions = [
                {"bounds": [[76, 42], [81, 44]], "coverage": 0.4, "name": "Tian Shan Glaciers"},
            ]
        
        for region in regions:
            bounds = region["bounds"]
            coverage = region["coverage"]
            
            # Generate grid points
            for lat in range(bounds[0][1], bounds[1][1]):
                for lng in range(bounds[0][0], bounds[1][0], 2):
                    # Probability of snow based on coverage
                    if random.random() < coverage:
                        # Snow depth estimation
                        if is_winter:
                            depth_cm = random.randint(10, 80)
                        else:
                            depth_cm = random.randint(0, 30)
                        
                        # Elevation adjustment
                        dist_to_mountains = math.sqrt((lng - 77)**2 + (lat - 43)**2)
                        if dist_to_mountains < 3:
                            depth_cm += 50
                        
                        albedo = 0.6 + depth_cm / 200
                        
                        features.append({
                            "type": "Feature",
                            "properties": {
                                "snow_cover": True,
                                "depth_cm": depth_cm,
                                "albedo": round(min(0.95, albedo), 2),
                                "region": region["name"],
                                "weight": min(1, depth_cm / 80)
                            },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lng + 0.5, lat + 0.5]
                            }
                        })
        
        return {
            "id": "snow-cover",
            "type": "heatmap",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": features
                }
            },
            "paint": {
                "heatmap-weight": ["get", "weight"],
                "heatmap-intensity": 1.2,
                "heatmap-color": [
                    "interpolate", ["linear"], ["heatmap-density"],
                    0, "rgba(255,255,255,0)",
                    0.2, "#e0f3f8",
                    0.4, "#abd9e9",
                    0.6, "#74add1",
                    0.8, "#4575b4",
                    1.0, "#ffffff"
                ],
                "heatmap-radius": 40,
                "heatmap-opacity": 0.7
            },
            "metadata": {
                "source": "MODIS Snow Cover Simulation",
                "timestamp": timestamp,
                "product": "MOD10A2",
                "season": "winter" if is_winter else "summer"
            }
        }


# Create singleton instance
satellite_service = SatelliteDataService()
