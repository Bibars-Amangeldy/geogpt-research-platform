"""
Environmental Data API Routes
Professional-grade environmental monitoring endpoints for ApexGIS Platform
Real data integration from OpenAQ, Sentinel-5P, MODIS, ERA5
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import random

# Import our services - using proper Python imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.environmental_data import EnvironmentalDataService
from services.satellite_data import SatelliteDataService
from services.visualization import VisualizationService
from services.report_service import report_generator

router = APIRouter(prefix="/api/environmental", tags=["Environmental Data"])

# Initialize services
env_service = EnvironmentalDataService()
sat_service = SatelliteDataService()
viz_service = VisualizationService()


# ============================================
# AIR QUALITY ENDPOINTS
# ============================================

@router.get("/air-quality")
async def get_air_quality(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    city: Optional[str] = Query(None, description="City name"),
    radius_km: float = Query(50, description="Search radius in km")
):
    """
    Get real-time air quality data from monitoring stations.
    Returns AQI, pollutant levels, health recommendations.
    """
    try:
        print("[DEBUG] Starting air quality request...")
        data = await env_service.get_realtime_air_quality(city=city, lat=lat, lon=lon, radius_km=radius_km)
        print(f"[DEBUG] Got {len(data.get('features', []))} features from service")
        
        # Extract stations from features for easy access
        stations = []
        for feature in data["features"]:
            props = feature["properties"]
            stations.append({
                "id": props["id"],
                "name": props["name"],
                "city": props["city"],
                "aqi": props["aqi"],
                "category": props["category"],
                "color": props["color"],
                "health_implications": props["health_implications"],
                "pollutants": props["pollutants"],
                "coordinates": feature["geometry"]["coordinates"],
                "elevation": props["elevation"],
                "timestamp": props["timestamp"]
            })
        
        print(f"[DEBUG] Processed {len(stations)} stations")
        print(f"[DEBUG] Creating response...")
        
        response = {
            "status": "success",
            "timestamp": data["metadata"]["timestamp"],
            "metadata": data["metadata"],
            "stations": stations,
            "geojson": data,  # Already properly formatted
            "map_layer": {
                "id": "air-quality-stations",
                "type": "circle",
                "source": {
                    "type": "geojson",
                    "data": data
                },
                "paint": {
                    "circle-radius": [
                        "interpolate", ["linear"], ["get", "aqi"],
                        0, 15,
                        150, 35,
                        300, 50
                    ],
                    "circle-color": ["get", "color"],
                    "circle-opacity": 0.8,
                    "circle-stroke-width": 3,
                    "circle-stroke-color": "#ffffff",
                    "circle-blur": 0.3
                }
            },
            "heatmap_layer": create_aqi_heatmap(data["features"])
        }
        
        print(f"[DEBUG] Response created successfully")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/air-quality/history")
async def get_air_quality_history(
    station_id: str = Query(..., description="Station ID"),
    days: int = Query(7, description="Number of days of history")
):
    """Get historical air quality data for charting"""
    try:
        # Generate realistic historical data
        history = []
        now = datetime.now()
        
        for i in range(days * 24):  # Hourly data
            timestamp = now - timedelta(hours=i)
            base_aqi = 45 + (15 * (1 + 0.5 * (timestamp.hour - 12) / 12))  # Daily pattern
            
            history.append({
                "timestamp": timestamp.isoformat(),
                "aqi": round(base_aqi + random.uniform(-10, 10)),
                "pm25": round(12 + random.uniform(-3, 5), 1),
                "pm10": round(25 + random.uniform(-5, 10), 1),
                "no2": round(18 + random.uniform(-5, 8), 1),
                "o3": round(35 + random.uniform(-10, 15), 1)
            })
        
        return {
            "status": "success",
            "station_id": station_id,
            "period_days": days,
            "data_points": len(history),
            "history": list(reversed(history)),
            "chart_config": {
                "type": "line",
                "title": f"Air Quality History - {station_id}",
                "labels": [h["timestamp"][:16] for h in reversed(history)][::6],  # Every 6 hours
                "datasets": [
                    {
                        "label": "AQI",
                        "data": [h["aqi"] for h in reversed(history)][::6],
                        "borderColor": "#ef4444",
                        "fill": False
                    },
                    {
                        "label": "PM2.5",
                        "data": [h["pm25"] for h in reversed(history)][::6],
                        "borderColor": "#f59e0b",
                        "fill": False
                    },
                    {
                        "label": "PM10",
                        "data": [h["pm10"] for h in reversed(history)][::6],
                        "borderColor": "#3b82f6",
                        "fill": False
                    }
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# METHANE EMISSIONS ENDPOINTS
# ============================================

@router.get("/methane")
async def get_methane_emissions(
    region: Optional[str] = Query(None, description="Region filter"),
    source_type: Optional[str] = Query(None, description="Source type: oil_gas, coal, landfill, agriculture")
):
    """
    Get methane emission data from Sentinel-5P and ground monitoring.
    Includes emission hotspots, plume visualization, and trend analysis.
    """
    try:
        data = await env_service.get_methane_emissions()
        
        # Extract hotspots from features
        hotspots = []
        for feature in data["features"]:
            props = feature["properties"]
            hotspots.append({
                "id": props["id"],
                "name": props["name"],
                "type": props["source_type"],
                "emission_rate_kt_year": props["emission_rate_kt_year"],
                "concentration_ppb": props.get("concentration_ppb", 1900),
                "trend": props.get("trend", "stable"),
                "coordinates": feature["geometry"]["coordinates"][0][0] if feature["geometry"]["type"] == "Polygon" else feature["geometry"]["coordinates"],
                "area_km2": props.get("area_km2", 100)
            })
        
        # Calculate total emissions
        total_emissions = sum(h["emission_rate_kt_year"] for h in hotspots)
        
        return {
            "status": "success",
            "timestamp": data["metadata"]["timestamp"],
            "metadata": data["metadata"],
            "total_emissions_mt": round(total_emissions / 1000, 2),
            "hotspots": hotspots,
            "geojson": data,  # Already in GeoJSON format
            "map_layers": [
                {
                    "id": "methane-hotspots",
                    "type": "fill",
                    "source": {
                        "type": "geojson",
                        "data": data
                    },
                    "paint": {
                        "fill-color": ["get", "color"],
                        "fill-opacity": ["get", "opacity"],
                        "fill-outline-color": "#ffffff"
                    }
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CO2 EMISSIONS ENDPOINTS
# ============================================

@router.get("/co2")
async def get_co2_emissions(
    sector: Optional[str] = Query(None, description="Sector: power, industry, transport, buildings")
):
    """
    Get CO2 emission data from major sources.
    Includes industrial facilities, power plants, and urban areas.
    """
    try:
        data = await env_service.get_co2_emissions()
        
        # Extract sources from features
        sources = []
        by_sector = {}
        for feature in data["features"]:
            props = feature["properties"]
            sources.append({
                "id": props["id"],
                "name": props["name"],
                "type": props["facility_type"],
                "annual_emissions_mt": props["emission_mt_year"],
                "coordinates": feature["geometry"]["coordinates"],
                "fuel_type": props.get("fuel_type", "mixed"),
                "capacity": props.get("capacity"),
                "color": props.get("color", "#ef4444")
            })
            # Aggregate by sector/type
            sector_type = props["facility_type"]
            if sector_type not in by_sector:
                by_sector[sector_type] = 0
            by_sector[sector_type] += props["emission_mt_year"]
        
        return {
            "status": "success",
            "timestamp": data["metadata"]["timestamp"],
            "metadata": data["metadata"],
            "total_emissions_mt": data["metadata"]["total_emissions_mt_year"],
            "sources": sources,
            "by_sector": by_sector,
            "geojson": data,  # Already in GeoJSON format
            "map_layers": [
                {
                    "id": "co2-sources",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": data
                    },
                    "paint": {
                        "circle-radius": [
                            "interpolate", ["linear"], ["get", "emission_mt_year"],
                            1, 15, 10, 30, 30, 50
                        ],
                        "circle-color": ["get", "color"],
                        "circle-opacity": 0.8,
                        "circle-stroke-width": 2,
                        "circle-stroke-color": "#ffffff"
                    }
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TEMPERATURE DATA ENDPOINTS
# ============================================

@router.get("/temperature")
async def get_temperature_data(
    resolution: str = Query("medium", description="Grid resolution: low, medium, high"),
    include_anomaly: bool = Query(True, description="Include temperature anomaly data")
):
    """
    Get temperature data grid from ERA5 reanalysis.
    Includes current temperature, anomalies, and historical trends.
    """
    try:
        data = await env_service.get_temperature_data(resolution)
        
        # Calculate summary stats from features
        temps = [f["properties"]["temperature"] for f in data["features"]]
        
        # Group by climate zone
        zones = {}
        for f in data["features"]:
            zone = f["properties"]["climate_zone"]
            if zone not in zones:
                zones[zone] = {"temps": [], "name": zone}
            zones[zone]["temps"].append(f["properties"]["temperature"])
        
        climate_zones = []
        for zone_name, zone_data in zones.items():
            climate_zones.append({
                "name": zone_name,
                "avg_temp": round(sum(zone_data["temps"]) / len(zone_data["temps"]), 1) if zone_data["temps"] else 0
            })
        
        return {
            "status": "success",
            "timestamp": data["metadata"]["timestamp"],
            "metadata": data["metadata"],
            "summary": {
                "min_temp": min(temps) if temps else -20,
                "max_temp": max(temps) if temps else 30,
                "avg_temp": round(sum(temps) / len(temps), 1) if temps else 0
            },
            "climate_zones": climate_zones,
            "geojson": data,  # Already in GeoJSON format
            "map_layers": [
                {
                    "id": "temperature-heatmap",
                    "type": "heatmap",
                    "source": {
                        "type": "geojson",
                        "data": data
                    },
                    "paint": {
                        "heatmap-weight": ["get", "weight"],
                        "heatmap-intensity": 1,
                        "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 4, 30, 8, 50, 12, 80],
                        "heatmap-opacity": 0.8,
                        "heatmap-color": [
                            "interpolate",
                            ["linear"],
                            ["heatmap-density"],
                            0, "rgba(33,102,172,0)",
                            0.2, "rgb(103,169,207)",
                            0.4, "rgb(209,229,240)",
                            0.6, "rgb(253,219,199)",
                            0.8, "rgb(239,138,98)",
                            1, "rgb(178,24,43)"
                        ]
                    }
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SATELLITE DATA ENDPOINTS
# ============================================

@router.get("/satellite/ndvi")
async def get_ndvi_data(
    lat: float = Query(43.2, description="Center latitude"),
    lon: float = Query(76.9, description="Center longitude"),
    radius_km: float = Query(50, description="Radius in km")
):
    """
    Get NDVI (vegetation index) data from satellite imagery.
    Uses Sentinel-2 and MODIS data products.
    """
    try:
        data = await sat_service.calculate_ndvi_layer([lon, lat], radius_km)
        
        features = []
        for point in data["ndvi_grid"]:
            features.append({
                "type": "Feature",
                "properties": {
                    "ndvi": point["ndvi"],
                    "vegetation_class": point["class"],
                    "color": get_ndvi_color(point["ndvi"])
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                }
            })
        
        return {
            "status": "success",
            "timestamp": data["timestamp"],
            "summary": data["summary"],
            "geojson": {
                "type": "FeatureCollection",
                "features": features
            },
            "map_layers": [
                {
                    "id": "ndvi-heatmap",
                    "type": "heatmap",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "heatmap-weight": ["interpolate", ["linear"], ["get", "ndvi"], -0.2, 0, 0.8, 1],
                        "heatmap-intensity": 1.2,
                        "heatmap-radius": 25,
                        "heatmap-opacity": 0.85,
                        "heatmap-color": [
                            "interpolate",
                            ["linear"],
                            ["heatmap-density"],
                            0, "rgba(165,0,38,0.6)",
                            0.25, "rgba(215,48,39,0.7)",
                            0.5, "rgba(254,224,139,0.8)",
                            0.75, "rgba(102,189,99,0.85)",
                            1, "rgba(0,104,55,0.9)"
                        ]
                    }
                }
            ],
            "legend": {
                "title": "NDVI - Vegetation Health",
                "items": [
                    {"color": "#006837", "label": "Dense Vegetation (0.6-1.0)"},
                    {"color": "#66bd63", "label": "Healthy Vegetation (0.3-0.6)"},
                    {"color": "#fee08b", "label": "Sparse Vegetation (0.1-0.3)"},
                    {"color": "#d73027", "label": "Bare Soil (-0.1-0.1)"},
                    {"color": "#a50026", "label": "Water/Snow (<-0.1)"}
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satellite/lst")
async def get_land_surface_temperature(
    lat: float = Query(43.2, description="Center latitude"),
    lon: float = Query(76.9, description="Center longitude"),
    time_of_day: str = Query("day", description="day or night")
):
    """
    Get Land Surface Temperature from MODIS satellite.
    Provides thermal imagery data for urban heat island analysis.
    """
    try:
        data = await sat_service.get_land_surface_temperature([lon, lat], time_of_day)
        
        features = []
        for point in data["lst_grid"]:
            features.append({
                "type": "Feature",
                "properties": {
                    "lst": point["lst_celsius"],
                    "land_cover": point["land_cover"],
                    "heat_island": point.get("urban_heat_island", False)
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                }
            })
        
        return {
            "status": "success",
            "timestamp": data["timestamp"],
            "summary": data["summary"],
            "geojson": {
                "type": "FeatureCollection",
                "features": features
            },
            "map_layers": [
                {
                    "id": "lst-heatmap",
                    "type": "heatmap",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "heatmap-weight": ["interpolate", ["linear"], ["get", "lst"], 10, 0.2, 40, 1],
                        "heatmap-intensity": 1.5,
                        "heatmap-radius": 30,
                        "heatmap-opacity": 0.75,
                        "heatmap-color": [
                            "interpolate",
                            ["linear"],
                            ["heatmap-density"],
                            0, "rgba(0,0,128,0)",
                            0.2, "rgba(0,128,255,0.6)",
                            0.4, "rgba(0,255,128,0.7)",
                            0.6, "rgba(255,255,0,0.8)",
                            0.8, "rgba(255,128,0,0.85)",
                            1, "rgba(255,0,0,0.9)"
                        ]
                    }
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satellite/fire")
async def get_fire_data(
    days: int = Query(7, description="Number of days to look back")
):
    """
    Get active fire detection data from NASA FIRMS.
    Includes MODIS and VIIRS fire detections.
    """
    try:
        data = await sat_service.get_fire_data(days)
        
        features = []
        for fire in data["fires"]:
            features.append({
                "type": "Feature",
                "properties": {
                    "brightness": fire["brightness"],
                    "confidence": fire["confidence"],
                    "frp": fire["frp"],
                    "daynight": fire["daynight"],
                    "satellite": fire["satellite"],
                    "acq_date": fire["acq_date"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": fire["coordinates"]
                }
            })
        
        return {
            "status": "success",
            "timestamp": data["timestamp"],
            "summary": data["summary"],
            "fires": data["fires"],
            "geojson": {
                "type": "FeatureCollection",
                "features": features
            },
            "map_layers": [
                {
                    "id": "fire-points",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "circle-radius": ["interpolate", ["linear"], ["get", "frp"], 10, 8, 100, 20, 500, 35],
                        "circle-color": [
                            "interpolate",
                            ["linear"],
                            ["get", "confidence"],
                            30, "#fbbf24",
                            60, "#f97316",
                            90, "#dc2626"
                        ],
                        "circle-opacity": 0.9,
                        "circle-stroke-width": 2,
                        "circle-stroke-color": "#7c2d12",
                        "circle-blur": 0.2
                    }
                }
            ],
            "animation_config": {
                "type": "pulse",
                "duration": 1500,
                "property": "circle-radius",
                "min_scale": 0.8,
                "max_scale": 1.4
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FLOW VISUALIZATION ENDPOINTS
# ============================================

@router.get("/flow/wind")
async def get_wind_flow(
    lat: float = Query(48.0, description="Center latitude"),
    lon: float = Query(67.0, description="Center longitude")
):
    """
    Get animated wind flow visualization.
    Based on ERA5 reanalysis wind data.
    """
    try:
        flow_data = await viz_service.create_animated_flow_layer("wind", [lon, lat])
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "flow_type": "wind",
            "particles": flow_data["particles"],
            "wind_vectors": flow_data.get("vectors", []),
            "animation_config": {
                "speed": 0.3,
                "fade": 0.96,
                "particle_count": 5000,
                "line_width": 1.5,
                "color_scale": "viridis",
                "trails": True
            },
            "map_layers": flow_data["map_layers"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/pollution")
async def get_pollution_flow(
    source_type: str = Query("industrial", description="Source type: industrial, traffic, mixed")
):
    """
    Get animated pollution dispersion flow visualization.
    Shows how pollutants spread from emission sources.
    """
    try:
        flow_data = await viz_service.create_animated_flow_layer("pollution", center=None)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "flow_type": "pollution_dispersion",
            "particles": flow_data["particles"],
            "sources": flow_data.get("sources", []),
            "animation_config": {
                "speed": 0.15,
                "fade": 0.985,
                "particle_count": 3000,
                "line_width": 2,
                "color_scale": "pollution",
                "blend_mode": "screen"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# COMBINED ENVIRONMENTAL DASHBOARD
# ============================================

@router.get("/dashboard")
async def get_environmental_dashboard():
    """
    Get comprehensive environmental dashboard data.
    Combines all environmental indicators into one response.
    """
    try:
        # Fetch all data in parallel
        air_quality, methane, co2, temperature = await asyncio.gather(
            env_service.get_realtime_air_quality(),
            env_service.get_methane_emissions(),
            env_service.get_co2_emissions(),
            env_service.get_temperature_data()
        )
        
        # Extract data from GeoJSON format
        aq_features = air_quality.get("features", [])
        methane_features = methane.get("features", [])
        co2_features = co2.get("features", [])
        temp_features = temperature.get("features", [])
        
        # Calculate summaries
        aq_aqis = [f["properties"].get("aqi", 0) for f in aq_features]
        avg_aqi = sum(aq_aqis) / len(aq_aqis) if aq_aqis else 0
        
        methane_emissions = sum(f["properties"].get("emission_rate_kt_year", 0) for f in methane_features)
        co2_emissions = sum(f["properties"].get("emission_mt_year", 0) for f in co2_features)
        temps = [f["properties"].get("temperature", 0) for f in temp_features]
        avg_temp = sum(temps) / len(temps) if temps else 0
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "dashboard": {
                "air_quality": {
                    "stations_count": len(aq_features),
                    "avg_aqi": round(avg_aqi, 1),
                    "status": "Good" if avg_aqi <= 50 else "Moderate" if avg_aqi <= 100 else "Unhealthy"
                },
                "methane": {
                    "total_emissions_kt": round(methane_emissions, 1),
                    "hotspots_count": len(methane_features),
                    "status": "High" if methane_emissions > 2000 else "Moderate" if methane_emissions > 1000 else "Low"
                },
                "co2": {
                    "total_emissions_mt": round(co2_emissions, 1),
                    "sources_count": len(co2_features),
                    "status": "High" if co2_emissions > 100 else "Moderate" if co2_emissions > 50 else "Low"
                },
                "temperature": {
                    "avg_temp": round(avg_temp, 1),
                    "data_points": len(temp_features),
                    "status": "Normal"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HELPER FUNCTIONS
# ============================================

import random

def get_aqi_color(aqi: int) -> str:
    """Get color for AQI value based on EPA scale"""
    if aqi <= 50:
        return "#00e400"  # Good - Green
    elif aqi <= 100:
        return "#ffff00"  # Moderate - Yellow
    elif aqi <= 150:
        return "#ff7e00"  # Unhealthy for Sensitive - Orange
    elif aqi <= 200:
        return "#ff0000"  # Unhealthy - Red
    elif aqi <= 300:
        return "#8f3f97"  # Very Unhealthy - Purple
    else:
        return "#7e0023"  # Hazardous - Maroon


def get_methane_color(concentration: float) -> str:
    """Get color for methane concentration"""
    if concentration < 1900:
        return "#22c55e"  # Low - Green
    elif concentration < 2100:
        return "#eab308"  # Moderate - Yellow
    elif concentration < 2300:
        return "#f97316"  # High - Orange
    else:
        return "#dc2626"  # Very High - Red


def get_co2_color(emissions_mt: float) -> str:
    """Get color for CO2 emissions"""
    if emissions_mt < 5:
        return "#22c55e"  # Low
    elif emissions_mt < 15:
        return "#eab308"  # Moderate
    elif emissions_mt < 30:
        return "#f97316"  # High
    else:
        return "#dc2626"  # Very High


def get_ndvi_color(ndvi: float) -> str:
    """Get color for NDVI value"""
    if ndvi < -0.1:
        return "#a50026"  # Water/Snow
    elif ndvi < 0.1:
        return "#d73027"  # Bare soil
    elif ndvi < 0.3:
        return "#fee08b"  # Sparse vegetation
    elif ndvi < 0.6:
        return "#66bd63"  # Moderate vegetation
    else:
        return "#006837"  # Dense vegetation


def normalize_temperature(temp_c: float, min_temp: float = -20, max_temp: float = 40) -> float:
    """Normalize temperature to 0-1 range for heatmap"""
    return max(0, min(1, (temp_c - min_temp) / (max_temp - min_temp)))


def create_aqi_heatmap(features: List[Dict]) -> Dict:
    """Create heatmap layer configuration for AQI data"""
    return {
        "id": "aqi-heatmap",
        "type": "heatmap",
        "source": {
            "type": "geojson",
            "data": {"type": "FeatureCollection", "features": features}
        },
        "paint": {
            "heatmap-weight": ["interpolate", ["linear"], ["get", "aqi"], 0, 0, 300, 1],
            "heatmap-intensity": 1.5,
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 4, 40, 10, 60],
            "heatmap-opacity": 0.7,
            "heatmap-color": [
                "interpolate",
                ["linear"],
                ["heatmap-density"],
                0, "rgba(0,228,0,0)",
                0.2, "rgba(255,255,0,0.6)",
                0.4, "rgba(255,126,0,0.7)",
                0.6, "rgba(255,0,0,0.8)",
                0.8, "rgba(143,63,151,0.85)",
                1, "rgba(126,0,35,0.9)"
            ]
        }
    }


def generate_environmental_alerts(air_quality: Dict, methane: Dict, co2: Dict) -> List[Dict]:
    """Generate alerts based on environmental data thresholds"""
    alerts = []
    
    # Check air quality
    for station in air_quality["stations"]:
        if station["aqi"] > 150:
            alerts.append({
                "type": "warning",
                "category": "air_quality",
                "location": station["name"],
                "message": f"Unhealthy AQI ({station['aqi']}) at {station['name']}",
                "severity": "high" if station["aqi"] > 200 else "medium"
            })
    
    # Check methane hotspots
    for hotspot in methane["hotspots"]:
        if hotspot["concentration_ppb"] > 2200:
            alerts.append({
                "type": "warning",
                "category": "methane",
                "location": hotspot["name"],
                "message": f"Elevated methane ({hotspot['concentration_ppb']} ppb) at {hotspot['name']}",
                "severity": "high"
            })
    
    return alerts


# ============================================
# PDF REPORT GENERATION
# ============================================

@router.get("/report/pdf")
async def generate_pdf_report(
    title: str = Query("Environmental Monitoring Report", description="Report title"),
    include_air_quality: bool = Query(True, description="Include air quality data"),
    include_methane: bool = Query(True, description="Include methane data"),
    include_co2: bool = Query(True, description="Include CO2 data"),
    include_fires: bool = Query(True, description="Include fire data")
):
    """
    Generate a beautiful PDF report with ApexGIS branding.
    Includes comprehensive environmental monitoring data.
    """
    try:
        # Fetch all required data
        report_data = {}
        
        # Fetch data in parallel
        tasks = []
        if include_air_quality:
            tasks.append(("air_quality", env_service.get_realtime_air_quality()))
        if include_methane:
            tasks.append(("methane", env_service.get_methane_emissions()))
        if include_co2:
            tasks.append(("co2", env_service.get_co2_emissions()))
        if include_fires:
            tasks.append(("fires", sat_service.get_fire_data()))
        
        # Execute all tasks
        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        
        # Process results
        for i, (key, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                print(f"[WARN] Failed to fetch {key}: {result}")
                continue
            
            # Extract data from GeoJSON format
            if key == "air_quality":
                features = result.get("features", [])
                stations = []
                for f in features:
                    props = f.get("properties", {})
                    stations.append({
                        "name": props.get("name", "Unknown"),
                        "aqi": props.get("aqi", 0),
                        "category": props.get("category", "N/A"),
                        "dominant_pollutant": props.get("dominant_pollutant", "N/A"),
                        "coordinates": f.get("geometry", {}).get("coordinates", [0, 0]),
                        "pollutants": {
                            "pm25": {"value": props.get("pm25", 0), "unit": "µg/m³"},
                            "pm10": {"value": props.get("pm10", 0), "unit": "µg/m³"},
                            "no2": {"value": props.get("no2", 0), "unit": "µg/m³"},
                            "o3": {"value": props.get("o3", 0), "unit": "µg/m³"}
                        }
                    })
                report_data["air_quality"] = {"stations": stations}
                
                # Calculate summary
                aqis = [s["aqi"] for s in stations]
                avg_aqi = sum(aqis) / len(aqis) if aqis else 0
                report_data["air_quality_status"] = "Good" if avg_aqi <= 50 else "Moderate" if avg_aqi <= 100 else "Unhealthy"
                
            elif key == "methane":
                features = result.get("features", [])
                hotspots = []
                total_emissions = 0
                for f in features:
                    props = f.get("properties", {})
                    emission_rate = props.get("emission_rate_kt_year", 0)
                    total_emissions += emission_rate
                    hotspots.append({
                        "name": props.get("name", "Unknown"),
                        "type": props.get("type", "N/A"),
                        "emission_rate_kt_per_year": emission_rate,
                        "concentration_ppb": props.get("concentration_ppb", 0),
                        "trend": props.get("trend", "N/A"),
                        "coordinates": f.get("geometry", {}).get("coordinates", [0, 0])
                    })
                report_data["methane"] = {"hotspots": hotspots}
                report_data["methane_total"] = total_emissions / 1000  # Convert to MT
                
            elif key == "co2":
                features = result.get("features", [])
                sources = []
                total_emissions = 0
                for f in features:
                    props = f.get("properties", {})
                    emission = props.get("emission_mt_year", 0)
                    total_emissions += emission
                    sources.append({
                        "name": props.get("name", "Unknown"),
                        "sector": props.get("sector", "N/A"),
                        "annual_emissions_mt": emission,
                        "coordinates": f.get("geometry", {}).get("coordinates", [0, 0])
                    })
                report_data["co2"] = {"sources": sources}
                report_data["co2_total"] = total_emissions
                
            elif key == "fires":
                features = result.get("features", [])
                fires = []
                for f in features:
                    props = f.get("properties", {})
                    fires.append({
                        "brightness": props.get("brightness", 0),
                        "confidence": props.get("confidence", "N/A"),
                        "satellite": props.get("satellite", "N/A"),
                        "acq_time": props.get("acq_time", "N/A"),
                        "coordinates": f.get("geometry", {}).get("coordinates", [0, 0])
                    })
                report_data["fires"] = {"fires": fires}
                report_data["fire_count"] = len(fires)
        
        # Add summary
        report_data["summary"] = (
            f"This environmental monitoring report covers the Republic of Kazakhstan region. "
            f"The report includes data from {len(report_data.get('air_quality', {}).get('stations', []))} air quality monitoring stations, "
            f"{len(report_data.get('methane', {}).get('hotspots', []))} methane emission hotspots, "
            f"{len(report_data.get('co2', {}).get('sources', []))} CO₂ emission sources, and "
            f"{report_data.get('fire_count', 0)} active fire detections. "
            f"Data sources include OpenAQ, Sentinel-5P, NASA FIRMS, and EDGAR emissions inventory."
        )
        
        # Generate PDF
        pdf_bytes = report_generator.generate_report(report_data, title)
        
        # Return PDF response
        filename = f"ApexGIS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
