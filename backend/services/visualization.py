"""
Advanced Visualization Services - Professional Geo-Visualization
Based on best practices from opengeos/leafmap and deck.gl
Provides animated layers, particle systems, flow visualization
"""

import math
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import json


# ==============================================================
# PROFESSIONAL COLOR PALETTES
# Based on ColorBrewer and scientific visualization standards
# ==============================================================

COLOR_PALETTES = {
    "sequential_blue": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
    "sequential_green": ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"],
    "sequential_red": ["#fff5f0", "#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#a50f15", "#67000d"],
    "diverging_rdbu": ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#f7f7f7", "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"],
    "diverging_spectral": ["#9e0142", "#d53e4f", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", "#e6f598", "#abdda4", "#66c2a5", "#3288bd", "#5e4fa2"],
    "categorical": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    "terrain": ["#333333", "#4d4d4d", "#666666", "#808080", "#999999", "#b3b3b3", "#cccccc", "#e6e6e6", "#ffffff"],
    "temperature": ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"],
    "precipitation": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
    "ndvi": ["#8b4513", "#d2691e", "#daa520", "#bdb76b", "#9acd32", "#228b22", "#006400", "#004d00", "#003300"],
    "emissions": ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc4e2a", "#e31a1c", "#bd0026", "#800026"],
}


class VisualizationService:
    """
    Professional visualization service for presidential-quality maps
    Provides animated layers, particle systems, and advanced styling
    """
    
    def __init__(self):
        self.palettes = COLOR_PALETTES
    
    # ==============================================================
    # ANIMATED FLOW VISUALIZATION
    # ==============================================================
    
    async def create_animated_flow_layer(self, flow_type: str, 
                                    center: List[float],
                                    data: Dict = None) -> Dict[str, Any]:
        """
        Create animated flow visualization
        Supports wind, water, pollution dispersion
        """
        if flow_type == "wind":
            return self._create_wind_flow(center, data)
        elif flow_type == "water":
            return self._create_water_flow(center, data)
        elif flow_type == "pollution":
            return self._create_pollution_dispersion(center, data)
        elif flow_type == "traffic":
            return self._create_traffic_flow(center, data)
        else:
            return self._create_generic_flow(center, data)
    
    def _create_wind_flow(self, center: List[float], data: Dict = None) -> Dict[str, Any]:
        """Create animated wind flow visualization"""
        features = []
        particles = []
        
        # Generate wind field grid
        grid_size = 20
        for i in range(-grid_size, grid_size + 1, 2):
            for j in range(-grid_size, grid_size + 1, 2):
                lng = center[0] + i * 0.1
                lat = center[1] + j * 0.08
                
                # Simulate wind direction and speed
                # Prevailing westerlies in Kazakhstan
                base_direction = 270  # West
                direction = base_direction + random.gauss(0, 30)
                speed = 5 + random.gauss(5, 3)  # m/s
                
                # Calculate end point for wind arrow
                dx = math.cos(math.radians(direction)) * speed * 0.02
                dy = math.sin(math.radians(direction)) * speed * 0.02
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "direction": round(direction),
                        "speed_ms": round(speed, 1),
                        "speed_kmh": round(speed * 3.6, 1),
                        "u": round(dx, 4),
                        "v": round(dy, 4),
                        "color": self._speed_to_color(speed)
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[lng, lat], [lng + dx, lat + dy]]
                    }
                })
                
                # Generate particles for animation
                for _ in range(2):
                    particles.append({
                        "lng": lng + random.uniform(-0.05, 0.05),
                        "lat": lat + random.uniform(-0.04, 0.04),
                        "direction": direction,
                        "speed": speed
                    })
        
        return {
            "id": "wind-flow",
            "type": "animated-flow",
            "layers": [
                {
                    "id": "wind-arrows",
                    "type": "line",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "line-color": ["get", "color"],
                        "line-width": ["interpolate", ["linear"], ["get", "speed_ms"], 0, 1, 10, 3, 20, 5],
                        "line-opacity": 0.6
                    }
                }
            ],
            "animation": {
                "type": "particle",
                "particles": particles,
                "duration_ms": 3000,
                "particle_color": "#22d3ee",
                "particle_size": 3,
                "trail_length": 15,
                "fade": True
            },
            "metadata": {
                "source": "ECMWF ERA5 Wind Data Simulation",
                "unit": "m/s",
                "prevailing_direction": "Westerly",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def _speed_to_color(self, speed: float) -> str:
        """Convert wind speed to color"""
        if speed < 3:
            return "#93c5fd"  # Light blue - calm
        elif speed < 6:
            return "#3b82f6"  # Blue - light
        elif speed < 10:
            return "#22c55e"  # Green - moderate
        elif speed < 15:
            return "#f59e0b"  # Orange - strong
        elif speed < 20:
            return "#ef4444"  # Red - very strong
        else:
            return "#991b1b"  # Dark red - severe
    
    def _create_water_flow(self, center: List[float], data: Dict = None) -> Dict[str, Any]:
        """Create animated water/river flow visualization"""
        features = []
        
        # Simulate river network near Almaty
        rivers = [
            {
                "name": "Bolshaya Almatinka",
                "path": [[77.0833, 43.0500], [77.0667, 43.1000], [77.0500, 43.1500], 
                        [76.9833, 43.2000], [76.9167, 43.2500]],
                "discharge": 2.8
            },
            {
                "name": "Malaya Almatinka", 
                "path": [[77.0500, 43.0833], [77.0333, 43.1167], [76.9833, 43.1667],
                        [76.9500, 43.2000]],
                "discharge": 1.9
            }
        ]
        
        for river in rivers:
            path = river["path"]
            discharge = river["discharge"]
            
            # Create flow segments
            for i in range(len(path) - 1):
                start = path[i]
                end = path[i + 1]
                
                # Calculate flow direction
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = math.sqrt(dx*dx + dy*dy)
                
                # Generate flow particles along segment
                num_particles = int(length * 500)
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "river": river["name"],
                        "discharge": discharge,
                        "flow_direction": math.degrees(math.atan2(dy, dx)),
                        "segment": i,
                        "color": "#22d3ee",
                        "width": max(3, discharge * 1.5)
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [start, end]
                    }
                })
        
        return {
            "id": "water-flow",
            "type": "animated-flow",
            "layers": [
                {
                    "id": "river-lines",
                    "type": "line",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "line-color": "#22d3ee",
                        "line-width": ["get", "width"],
                        "line-opacity": 0.8
                    }
                }
            ],
            "animation": {
                "type": "flow",
                "speed": 0.5,
                "particle_count": 100,
                "particle_color": "#ffffff",
                "particle_size": 2,
                "direction": "downstream"
            },
            "metadata": {
                "source": "Hydrological Network Kazakhstan",
                "unit": "m³/s",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def _create_pollution_dispersion(self, center: List[float], 
                                      data: Dict = None) -> Dict[str, Any]:
        """Create animated pollution dispersion visualization"""
        features = []
        particles = []
        
        # Source point (emission source)
        source = center if center else [71.4491, 51.1801]
        
        # Generate dispersion plume based on Gaussian model
        wind_direction = 270 + random.gauss(0, 20)  # Prevailing westerlies
        wind_speed = 5 + random.uniform(0, 5)
        
        # Generate concentration field
        num_points = 200
        for _ in range(num_points):
            # Gaussian plume model
            downwind = random.expovariate(1/0.1)  # Distance downwind
            crosswind = random.gauss(0, downwind * 0.1)  # Spread
            
            # Convert to lat/lng
            dx = math.cos(math.radians(wind_direction)) * downwind
            dy = math.sin(math.radians(wind_direction)) * downwind
            
            dx += math.cos(math.radians(wind_direction + 90)) * crosswind
            dy += math.sin(math.radians(wind_direction + 90)) * crosswind
            
            lng = source[0] + dx
            lat = source[1] + dy
            
            # Concentration decreases with distance
            concentration = max(0, 1 - downwind * 5) * random.uniform(0.7, 1.3)
            
            if concentration > 0.1:
                features.append({
                    "type": "Feature",
                    "properties": {
                        "concentration": round(concentration, 3),
                        "distance_km": round(downwind * 111, 1),
                        "color": self._concentration_to_color(concentration),
                        "weight": concentration
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                })
                
                particles.append({
                    "lng": lng,
                    "lat": lat,
                    "concentration": concentration,
                    "direction": wind_direction + random.gauss(0, 10),
                    "speed": wind_speed * (0.5 + concentration * 0.5)
                })
        
        return {
            "id": "pollution-dispersion",
            "type": "animated-flow",
            "layers": [
                {
                    "id": "pollution-heatmap",
                    "type": "heatmap",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "heatmap-weight": ["get", "weight"],
                        "heatmap-intensity": 1.5,
                        "heatmap-color": [
                            "interpolate", ["linear"], ["heatmap-density"],
                            0, "rgba(0,0,0,0)",
                            0.2, "rgba(255,255,0,0.3)",
                            0.4, "rgba(255,165,0,0.5)",
                            0.6, "rgba(255,69,0,0.7)",
                            0.8, "rgba(255,0,0,0.8)",
                            1.0, "rgba(139,0,0,0.9)"
                        ],
                        "heatmap-radius": 25,
                        "heatmap-opacity": 0.7
                    }
                }
            ],
            "animation": {
                "type": "particle",
                "particles": particles,
                "duration_ms": 4000,
                "particle_color": "#fbbf24",
                "particle_size": 4,
                "trail_length": 20,
                "fade": True,
                "disperse": True
            },
            "source_marker": {
                "coordinates": source,
                "type": "emission_source",
                "color": "#ef4444"
            },
            "metadata": {
                "source": "Gaussian Plume Model Simulation",
                "wind_direction": round(wind_direction),
                "wind_speed_ms": round(wind_speed, 1),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def _concentration_to_color(self, concentration: float) -> str:
        """Convert concentration to color"""
        if concentration < 0.2:
            return "#fef3c7"
        elif concentration < 0.4:
            return "#fde047"
        elif concentration < 0.6:
            return "#fb923c"
        elif concentration < 0.8:
            return "#ef4444"
        else:
            return "#991b1b"
    
    def _create_traffic_flow(self, center: List[float], data: Dict = None) -> Dict[str, Any]:
        """Create animated traffic flow visualization"""
        features = []
        
        # Simulate major roads
        roads = [
            {"name": "Al-Farabi Ave", "path": [[76.85, 43.22], [76.90, 43.22], [76.95, 43.22], [77.00, 43.22]], "lanes": 6},
            {"name": "Dostyk Ave", "path": [[76.95, 43.18], [76.95, 43.21], [76.95, 43.24], [76.95, 43.27]], "lanes": 4},
            {"name": "Abay Ave", "path": [[76.88, 43.24], [76.92, 43.24], [76.96, 43.24], [77.00, 43.24]], "lanes": 4},
        ]
        
        # Get current hour for traffic variation
        hour = datetime.now().hour
        is_rush_hour = 7 <= hour <= 9 or 17 <= hour <= 20
        
        for road in roads:
            # Traffic volume based on time
            base_volume = 50 if is_rush_hour else 20
            volume = base_volume + random.randint(-10, 10)
            
            # Speed based on volume (inverse relationship)
            speed = max(10, 60 - volume * 0.5)
            
            for i in range(len(road["path"]) - 1):
                features.append({
                    "type": "Feature",
                    "properties": {
                        "road": road["name"],
                        "lanes": road["lanes"],
                        "volume": volume,
                        "speed_kmh": round(speed),
                        "congestion": "heavy" if volume > 40 else "moderate" if volume > 25 else "light",
                        "color": "#ef4444" if volume > 40 else "#f59e0b" if volume > 25 else "#22c55e"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [road["path"][i], road["path"][i + 1]]
                    }
                })
        
        return {
            "id": "traffic-flow",
            "type": "animated-flow",
            "layers": [
                {
                    "id": "traffic-lines",
                    "type": "line",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "line-color": ["get", "color"],
                        "line-width": ["*", ["get", "lanes"], 1.5],
                        "line-opacity": 0.8
                    }
                }
            ],
            "animation": {
                "type": "dash",
                "dash_length": 20,
                "gap_length": 10,
                "speed": 2,
                "direction": "forward"
            },
            "metadata": {
                "source": "Traffic Flow Simulation",
                "is_rush_hour": is_rush_hour,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def _create_generic_flow(self, center: List[float], data: Dict = None) -> Dict[str, Any]:
        """Create generic flow visualization"""
        return self._create_wind_flow(center, data)
    
    # ==============================================================
    # 3D TERRAIN VISUALIZATION
    # ==============================================================
    
    def create_3d_terrain_layer(self, bounds: List[List[float]], 
                                 resolution: str = "high") -> Dict[str, Any]:
        """
        Create 3D terrain visualization
        Uses DEM data simulation based on Kazakhstan topography
        """
        features = []
        
        # Resolution settings
        res_map = {"high": 0.02, "medium": 0.05, "low": 0.1}
        step = res_map.get(resolution, 0.05)
        
        min_lng, min_lat = bounds[0]
        max_lng, max_lat = bounds[1]
        
        lat = min_lat
        while lat <= max_lat:
            lng = min_lng
            while lng <= max_lng:
                elevation = self._estimate_elevation(lng, lat)
                
                # Create grid cell
                features.append({
                    "type": "Feature",
                    "properties": {
                        "elevation": round(elevation),
                        "color": self._elevation_to_color(elevation),
                        "slope": round(random.uniform(0, 45), 1),
                        "aspect": round(random.uniform(0, 360))
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [lng, lat],
                            [lng + step, lat],
                            [lng + step, lat + step],
                            [lng, lat + step],
                            [lng, lat]
                        ]]
                    }
                })
                
                lng += step
            lat += step
        
        return {
            "id": "terrain-3d",
            "type": "fill-extrusion",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "fill-extrusion-color": ["get", "color"],
                "fill-extrusion-height": ["*", ["get", "elevation"], 10],  # Exaggeration
                "fill-extrusion-base": 0,
                "fill-extrusion-opacity": 0.8
            },
            "metadata": {
                "source": "SRTM DEM Simulation",
                "resolution": resolution,
                "exaggeration": 10,
                "unit": "meters"
            }
        }
    
    def _estimate_elevation(self, lng: float, lat: float) -> float:
        """Estimate elevation based on Kazakhstan topography"""
        elevation = 300  # Base elevation
        
        # Tian Shan mountains (southeast)
        dist_tian_shan = math.sqrt((lng - 77)**2 + (lat - 43)**2)
        if dist_tian_shan < 3:
            elevation += (3 - dist_tian_shan) * 1500
            if dist_tian_shan < 0.5:  # Peaks
                elevation += random.uniform(500, 1500)
        
        # Altai mountains (northeast)
        dist_altai = math.sqrt((lng - 86)**2 + (lat - 49)**2)
        if dist_altai < 2:
            elevation += (2 - dist_altai) * 1000
        
        # Caspian depression (west)
        dist_caspian = math.sqrt((lng - 51)**2 + (lat - 45)**2)
        if dist_caspian < 3:
            elevation = max(-28, elevation - (3 - dist_caspian) * 100)
        
        # Central Kazakh uplands
        if 65 < lng < 75 and 47 < lat < 52:
            elevation += random.uniform(100, 400)
        
        # Add noise for natural variation
        elevation += random.uniform(-50, 50)
        
        return max(-28, elevation)  # Caspian is lowest at -28m
    
    def _elevation_to_color(self, elevation: float) -> str:
        """Convert elevation to terrain color"""
        if elevation < 0:
            return "#1a5276"  # Below sea level - deep blue
        elif elevation < 200:
            return "#2e7d32"  # Low plains - green
        elif elevation < 500:
            return "#558b2f"  # Hills - light green
        elif elevation < 1000:
            return "#8bc34a"  # Low mountains - yellow-green
        elif elevation < 2000:
            return "#c0ca33"  # Mountains - yellow
        elif elevation < 3000:
            return "#f9a825"  # High mountains - orange
        elif elevation < 4000:
            return "#e65100"  # Very high - dark orange
        else:
            return "#ffffff"  # Snow-capped peaks
    
    # ==============================================================
    # PROFESSIONAL LEGENDS AND SCALES
    # ==============================================================
    
    def create_legend(self, layer_type: str, title: str,
                      unit: str = "", custom_colors: List = None) -> Dict[str, Any]:
        """Create professional legend for visualization"""
        
        legends = {
            "temperature": {
                "title": title or "Temperature",
                "unit": unit or "°C",
                "type": "gradient",
                "colors": self.palettes["temperature"],
                "labels": ["-40", "-30", "-20", "-10", "0", "10", "20", "30", "40"]
            },
            "precipitation": {
                "title": title or "Precipitation",
                "unit": unit or "mm",
                "type": "gradient",
                "colors": self.palettes["precipitation"],
                "labels": ["0", "5", "10", "25", "50", "100", "200", "300", ">400"]
            },
            "ndvi": {
                "title": title or "Vegetation Index (NDVI)",
                "unit": "",
                "type": "gradient",
                "colors": self.palettes["ndvi"],
                "labels": ["-0.5", "-0.2", "0", "0.2", "0.4", "0.6", "0.8", "1.0"]
            },
            "air_quality": {
                "title": title or "Air Quality Index",
                "unit": "",
                "type": "discrete",
                "items": [
                    {"color": "#00e400", "label": "Good (0-50)"},
                    {"color": "#ffff00", "label": "Moderate (51-100)"},
                    {"color": "#ff7e00", "label": "Unhealthy for Sensitive (101-150)"},
                    {"color": "#ff0000", "label": "Unhealthy (151-200)"},
                    {"color": "#8f3f97", "label": "Very Unhealthy (201-300)"},
                    {"color": "#7e0023", "label": "Hazardous (301+)"}
                ]
            },
            "emissions": {
                "title": title or "Emissions Intensity",
                "unit": unit or "kt/year",
                "type": "gradient",
                "colors": self.palettes["emissions"],
                "labels": ["Low", "", "", "", "Moderate", "", "", "", "High"]
            },
            "elevation": {
                "title": title or "Elevation",
                "unit": unit or "m",
                "type": "gradient",
                "colors": ["#1a5276", "#2e7d32", "#558b2f", "#8bc34a", "#c0ca33", "#f9a825", "#e65100", "#ffffff"],
                "labels": ["<0", "200", "500", "1000", "2000", "3000", "4000", ">5000"]
            },
            "glacier_status": {
                "title": title or "Glacier Status",
                "unit": "",
                "type": "discrete",
                "items": [
                    {"color": "#22c55e", "label": "Stable"},
                    {"color": "#f59e0b", "label": "Retreating"},
                    {"color": "#ef4444", "label": "Critical"}
                ]
            }
        }
        
        return legends.get(layer_type, {
            "title": title,
            "unit": unit,
            "type": "gradient",
            "colors": custom_colors or self.palettes["sequential_blue"],
            "labels": []
        })
    
    def create_scale_bar(self, center: List[float], zoom: int) -> Dict[str, Any]:
        """Create scale bar for map"""
        # Calculate scale based on latitude and zoom
        lat = center[1]
        meters_per_pixel = 156543.03392 * math.cos(math.radians(lat)) / (2 ** zoom)
        
        # Determine appropriate scale unit
        scale_pixels = 100
        scale_meters = meters_per_pixel * scale_pixels
        
        if scale_meters > 1000:
            value = round(scale_meters / 1000, 1)
            unit = "km"
        else:
            value = round(scale_meters)
            unit = "m"
        
        return {
            "value": value,
            "unit": unit,
            "pixels": scale_pixels,
            "position": "bottom-left"
        }
    
    # ==============================================================
    # TIME SERIES ANIMATION
    # ==============================================================
    
    def create_time_series_animation(self, data_type: str,
                                      time_range: Dict,
                                      interval: str = "daily") -> Dict[str, Any]:
        """Create time series animation configuration"""
        
        start_date = datetime.fromisoformat(time_range.get("start", "2024-01-01"))
        end_date = datetime.fromisoformat(time_range.get("end", "2024-12-31"))
        
        # Generate time steps
        steps = []
        current = start_date
        while current <= end_date:
            steps.append(current.isoformat())
            if interval == "daily":
                current += timedelta(days=1)
            elif interval == "weekly":
                current += timedelta(weeks=1)
            elif interval == "monthly":
                current += timedelta(days=30)
            elif interval == "yearly":
                current += timedelta(days=365)
        
        return {
            "type": "time-series",
            "data_type": data_type,
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "interval": interval,
            "steps": steps,
            "total_frames": len(steps),
            "playback": {
                "autoplay": False,
                "loop": True,
                "speed_ms": 500,
                "controls": ["play", "pause", "step", "slider"]
            },
            "display": {
                "show_timestamp": True,
                "format": "%Y-%m-%d" if interval in ["daily", "weekly"] else "%Y-%m",
                "position": "top-right"
            }
        }


# Create singleton instance
visualization_service = VisualizationService()
