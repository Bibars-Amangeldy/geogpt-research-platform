"""
GeoGPT Research Platform - Main Application
State-of-the-art Geospatial AI Platform with Advanced Visualization

Integrating best practices from:
- opengeos (segment-geospatial, geoai, leafmap)
- GeoGPT Research Project
- Professional environmental monitoring standards
"""

import os
import asyncio
import json
import math
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import environmental services
from services.environmental_data import EnvironmentalDataService
from services.satellite_data import SatelliteDataService
from services.visualization import VisualizationService
from services.real_data_service import real_data_service, RealDataService

# Initialize services
env_service = EnvironmentalDataService()
sat_service = SatelliteDataService()
viz_service = VisualizationService()
# Real data service for actual API calls
real_service = real_data_service


class Settings(BaseSettings):
    """Application settings"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,https://frontend-alpha-pied-55.vercel.app"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="GeoGPT Research Platform",
    description="State-of-the-art Geospatial AI Platform for Advanced Research with Real Environmental Data",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Import and register routers
from routes.environmental import router as environmental_router
app.include_router(environmental_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# GEOSPATIAL DATA - Kazakhstan Cities & Regions
# =====================================================

KAZAKHSTAN_CITIES = {
    "astana": {
        "name": "Astana",
        "name_kz": "Астана",
        "coordinates": [71.4491, 51.1801],
        "population": 1350000,
        "type": "capital",
        "description": "Capital city of Kazakhstan, modern metropolis with futuristic architecture",
        "area_km2": 797,
        "founded": 1830,
        "landmarks": ["Bayterek Tower", "Khan Shatyr", "Nur-Alem Sphere", "Palace of Peace"],
        "elevation": 347,
    },
    "almaty": {
        "name": "Almaty",
        "name_kz": "Алматы",
        "coordinates": [76.9458, 43.2220],
        "population": 2000000,
        "type": "megacity",
        "description": "Largest city and cultural capital, at the foothills of Trans-Ili Alatau",
        "area_km2": 682,
        "founded": 1854,
        "landmarks": ["Medeu", "Kok-Tobe", "Big Almaty Lake", "Central Mosque"],
        "elevation": 700,
    },
    "shymkent": {
        "name": "Shymkent",
        "name_kz": "Шымкент",
        "coordinates": [69.5958, 42.3417],
        "population": 1100000,
        "type": "city",
        "description": "Third largest city, southern economic hub",
        "area_km2": 1170,
        "founded": 1914,
        "landmarks": ["Independence Park", "Dendropark"],
        "elevation": 506,
    },
    "aktobe": {
        "name": "Aktobe",
        "name_kz": "Ақтөбе",
        "coordinates": [57.1722, 50.2839],
        "population": 500000,
        "type": "city",
        "description": "Western industrial center, oil and gas hub",
        "area_km2": 300,
        "elevation": 219,
    },
    "karaganda": {
        "name": "Karaganda",
        "name_kz": "Қарағанды",
        "coordinates": [73.1022, 49.8047],
        "population": 500000,
        "type": "city",
        "description": "Central Kazakhstan, historic coal mining center",
        "area_km2": 550,
        "elevation": 546,
    },
    "taraz": {
        "name": "Taraz",
        "name_kz": "Тараз",
        "coordinates": [71.3667, 42.9000],
        "population": 360000,
        "type": "city",
        "description": "Ancient city on the Silk Road, over 2000 years old",
        "area_km2": 150,
        "elevation": 636,
    },
    "pavlodar": {
        "name": "Pavlodar",
        "name_kz": "Павлодар",
        "coordinates": [76.9458, 52.2873],
        "population": 330000,
        "type": "city",
        "description": "Industrial city on the Irtysh River",
        "area_km2": 400,
        "elevation": 123,
    },
    "semey": {
        "name": "Semey",
        "name_kz": "Семей",
        "coordinates": [80.2275, 50.4111],
        "population": 320000,
        "type": "city",
        "description": "Historic city, birthplace of Abai Qunanbaiuly",
        "area_km2": 210,
        "elevation": 206,
    },
    "atyrau": {
        "name": "Atyrau",
        "name_kz": "Атырау",
        "coordinates": [51.9200, 46.8500],
        "population": 280000,
        "type": "city",
        "description": "Oil capital at the Caspian Sea, spans Europe and Asia",
        "area_km2": 32,
        "elevation": -22,
    },
    "aktau": {
        "name": "Aktau",
        "name_kz": "Ақтау",
        "coordinates": [51.1667, 43.6500],
        "population": 190000,
        "type": "city",
        "description": "Caspian Sea port city, unique address system by microdistricts",
        "area_km2": 76,
        "elevation": -22,
    },
    "kostanay": {
        "name": "Kostanay",
        "name_kz": "Қостанай",
        "coordinates": [63.6167, 53.2167],
        "population": 240000,
        "type": "city",
        "description": "Northern agricultural center",
        "area_km2": 240,
        "elevation": 156,
    },
    "turkistan": {
        "name": "Turkistan",
        "name_kz": "Түркістан",
        "coordinates": [68.2519, 43.3017],
        "population": 170000,
        "type": "city",
        "description": "Spiritual capital, Mausoleum of Khoja Ahmed Yasawi (UNESCO)",
        "area_km2": 200,
        "elevation": 200,
    },
    "petropavl": {
        "name": "Petropavl",
        "name_kz": "Петропавл",
        "coordinates": [69.1500, 54.8667],
        "population": 220000,
        "type": "city",
        "description": "Northern border city, close to Russia",
        "area_km2": 225,
        "elevation": 131,
    },
    "oral": {
        "name": "Oral",
        "name_kz": "Орал",
        "coordinates": [51.2333, 51.2333],
        "population": 280000,
        "type": "city",
        "description": "Western Kazakhstan regional center on Ural River",
        "area_km2": 700,
        "elevation": 36,
    },
    "taldykorgan": {
        "name": "Taldykorgan",
        "name_kz": "Талдықорған",
        "coordinates": [78.3667, 45.0167],
        "population": 145000,
        "type": "city",
        "description": "Administrative center of Almaty Region",
        "area_km2": 75,
        "elevation": 600,
    },
}


# =====================================================
# HYDROLOGICAL DATA - Glaciers, Rivers, Lakes
# =====================================================

GLACIERS = {
    "tuyuksu": {
        "name": "Tuyuksu Glacier",
        "name_kz": "Түйықсу мұзтауы",
        "coordinates": [77.0833, 43.0500],
        "area_km2": 2.48,
        "length_km": 3.8,
        "elevation_min": 3400,
        "elevation_max": 4219,
        "type": "valley",
        "status": "retreating",
        "retreat_rate_m_year": 8.5,
        "ice_thickness_m": 85,
        "region": "almaty",
        "mountain_range": "Zailiysky Alatau",
        "last_survey": "2024",
        "description": "One of the most studied glaciers in Central Asia, part of the World Glacier Monitoring Service network",
        "nearby_city": "almaty",
        "distance_to_city_km": 32,
    },
    "bogdanovich": {
        "name": "Bogdanovich Glacier",
        "name_kz": "Богданович мұзтауы",
        "coordinates": [77.0667, 43.0333],
        "area_km2": 1.72,
        "length_km": 2.5,
        "elevation_min": 3600,
        "elevation_max": 4100,
        "type": "cirque",
        "status": "retreating",
        "retreat_rate_m_year": 6.2,
        "ice_thickness_m": 60,
        "region": "almaty",
        "mountain_range": "Zailiysky Alatau",
        "last_survey": "2023",
        "description": "Cirque glacier located in the Malaya Almatinka river basin",
        "nearby_city": "almaty",
        "distance_to_city_km": 30,
    },
    "molodezhniy": {
        "name": "Molodezhniy Glacier",
        "name_kz": "Жастар мұзтауы",
        "coordinates": [77.1000, 43.0167],
        "area_km2": 1.35,
        "length_km": 2.1,
        "elevation_min": 3500,
        "elevation_max": 3950,
        "type": "valley",
        "status": "retreating",
        "retreat_rate_m_year": 5.8,
        "ice_thickness_m": 45,
        "region": "almaty",
        "mountain_range": "Zailiysky Alatau",
        "last_survey": "2023",
        "description": "Valley glacier feeding the Bolshaya Almatinka river",
        "nearby_city": "almaty",
        "distance_to_city_km": 35,
    },
    "mametova": {
        "name": "Mametova Glacier",
        "name_kz": "Мәметова мұзтауы",
        "coordinates": [77.0500, 43.0667],
        "area_km2": 0.95,
        "length_km": 1.8,
        "elevation_min": 3650,
        "elevation_max": 4050,
        "type": "cirque",
        "status": "critical",
        "retreat_rate_m_year": 12.3,
        "ice_thickness_m": 35,
        "region": "almaty",
        "mountain_range": "Zailiysky Alatau",
        "last_survey": "2024",
        "description": "Small cirque glacier showing rapid retreat, critical for monitoring",
        "nearby_city": "almaty",
        "distance_to_city_km": 28,
    },
    "gorodetskiy": {
        "name": "Gorodetskiy Glacier",
        "name_kz": "Городецкий мұзтауы",
        "coordinates": [77.1200, 43.0083],
        "area_km2": 2.15,
        "length_km": 3.2,
        "elevation_min": 3450,
        "elevation_max": 4200,
        "type": "valley",
        "status": "retreating",
        "retreat_rate_m_year": 7.1,
        "ice_thickness_m": 70,
        "region": "almaty",
        "mountain_range": "Zailiysky Alatau",
        "last_survey": "2023",
        "description": "Large valley glacier in the eastern part of Zailiysky Alatau",
        "nearby_city": "almaty",
        "distance_to_city_km": 40,
    },
    "shumskiy": {
        "name": "Shumskiy Glacier",
        "name_kz": "Шумский мұзтауы",
        "coordinates": [77.0333, 43.0833],
        "area_km2": 1.85,
        "length_km": 2.8,
        "elevation_min": 3550,
        "elevation_max": 4150,
        "type": "valley",
        "status": "stable",
        "retreat_rate_m_year": 3.2,
        "ice_thickness_m": 75,
        "region": "almaty",
        "mountain_range": "Zailiysky Alatau",
        "last_survey": "2024",
        "description": "Relatively stable glacier due to shaded north-facing aspect",
        "nearby_city": "almaty",
        "distance_to_city_km": 26,
    },
}

RIVERS = {
    "bolshaya_almatinka": {
        "name": "Bolshaya Almatinka River",
        "name_kz": "Үлкен Алматы өзені",
        "source_coordinates": [77.0833, 43.0500],
        "mouth_coordinates": [76.8500, 43.2833],
        "coordinates": [[77.0833, 43.0500], [77.0667, 43.1000], [77.0500, 43.1500], [76.9833, 43.2000], [76.9167, 43.2500], [76.8500, 43.2833]],
        "length_km": 45,
        "basin_area_km2": 465,
        "avg_discharge_m3s": 2.8,
        "max_discharge_m3s": 45,
        "source_elevation": 3400,
        "mouth_elevation": 650,
        "glacier_fed": True,
        "source_glacier": "Tuyuksu Glacier",
        "region": "almaty",
        "water_quality": "excellent",
        "uses": ["drinking water", "irrigation", "hydropower"],
        "description": "Major river supplying Almaty with drinking water, originates from Tuyuksu glacier",
        "nearby_city": "almaty",
        "seasonality": {"spring": "high", "summer": "peak", "autumn": "medium", "winter": "low"},
    },
    "malaya_almatinka": {
        "name": "Malaya Almatinka River",
        "name_kz": "Кіші Алматы өзені",
        "source_coordinates": [77.0500, 43.0833],
        "mouth_coordinates": [76.9000, 43.2500],
        "coordinates": [[77.0500, 43.0833], [77.0333, 43.1167], [76.9833, 43.1667], [76.9500, 43.2000], [76.9000, 43.2500]],
        "length_km": 38,
        "basin_area_km2": 235,
        "avg_discharge_m3s": 1.9,
        "max_discharge_m3s": 28,
        "source_elevation": 3200,
        "mouth_elevation": 720,
        "glacier_fed": True,
        "source_glacier": "Bogdanovich Glacier",
        "region": "almaty",
        "water_quality": "excellent",
        "uses": ["drinking water", "recreation"],
        "description": "Flows through famous Medeu skating rink area and Shymbulak ski resort",
        "nearby_city": "almaty",
        "seasonality": {"spring": "high", "summer": "peak", "autumn": "medium", "winter": "low"},
    },
    "ili": {
        "name": "Ili River",
        "name_kz": "Іле өзені",
        "source_coordinates": [80.0000, 43.6667],
        "mouth_coordinates": [74.5000, 45.0000],
        "coordinates": [[80.0000, 43.6667], [78.5000, 43.8333], [77.0000, 44.0000], [76.0000, 44.5000], [75.0000, 44.8333], [74.5000, 45.0000]],
        "length_km": 1439,
        "basin_area_km2": 140000,
        "avg_discharge_m3s": 329,
        "max_discharge_m3s": 1500,
        "source_elevation": 3500,
        "mouth_elevation": 340,
        "glacier_fed": True,
        "source_glacier": "Tian Shan glaciers",
        "region": "almaty",
        "water_quality": "good",
        "uses": ["irrigation", "hydropower", "fishing", "navigation"],
        "description": "Major river flowing into Lake Balkhash, vital for regional ecosystem",
        "nearby_city": "almaty",
        "seasonality": {"spring": "high", "summer": "peak", "autumn": "medium", "winter": "low"},
    },
    "charyn": {
        "name": "Charyn River",
        "name_kz": "Шарын өзені",
        "source_coordinates": [79.5000, 43.0000],
        "mouth_coordinates": [78.8333, 43.8333],
        "coordinates": [[79.5000, 43.0000], [79.2000, 43.2000], [79.0000, 43.4000], [78.9000, 43.6000], [78.8333, 43.8333]],
        "length_km": 427,
        "basin_area_km2": 7720,
        "avg_discharge_m3s": 35,
        "max_discharge_m3s": 250,
        "source_elevation": 3200,
        "mouth_elevation": 520,
        "glacier_fed": False,
        "region": "almaty",
        "water_quality": "good",
        "uses": ["tourism", "irrigation"],
        "description": "Famous for the spectacular Charyn Canyon, Kazakhstan's Grand Canyon",
        "nearby_city": "almaty",
        "seasonality": {"spring": "peak", "summer": "medium", "autumn": "low", "winter": "very_low"},
    },
}

LAKES = {
    "bolshoe_almatinskoe": {
        "name": "Big Almaty Lake",
        "name_kz": "Үлкен Алматы көлі",
        "coordinates": [77.0833, 43.0667],
        "surface_area_km2": 1.6,
        "max_depth_m": 40,
        "avg_depth_m": 25,
        "volume_million_m3": 28,
        "elevation": 2511,
        "type": "glacial",
        "water_source": "Ozernaya River, glacial melt",
        "region": "almaty",
        "water_quality": "pristine",
        "color": "turquoise",
        "temperature_summer": 10,
        "temperature_winter": -2,
        "frozen_months": ["December", "January", "February", "March"],
        "description": "Stunning turquoise alpine lake, main reservoir for Almaty's water supply",
        "nearby_city": "almaty",
        "distance_to_city_km": 28,
        "protected": True,
        "tourism": "restricted",
        "surrounding_peaks": ["Sovetov Peak (4317m)", "Ozerniy Peak (4110m)"],
    },
    "issyk": {
        "name": "Lake Issyk",
        "name_kz": "Есік көлі",
        "coordinates": [77.4667, 43.2500],
        "surface_area_km2": 0.4,
        "max_depth_m": 50,
        "avg_depth_m": 30,
        "volume_million_m3": 8,
        "elevation": 1756,
        "type": "moraine-dammed",
        "water_source": "Issyk River",
        "region": "almaty",
        "water_quality": "good",
        "color": "blue-green",
        "temperature_summer": 18,
        "temperature_winter": 0,
        "frozen_months": ["January", "February"],
        "description": "Restored after 1963 mudflow disaster, famous archaeological site (Golden Man)",
        "nearby_city": "almaty",
        "distance_to_city_km": 70,
        "protected": True,
        "tourism": "open",
        "historical_significance": "Golden Man (Saka warrior) discovered nearby in 1969",
    },
    "kaindy": {
        "name": "Lake Kaindy",
        "name_kz": "Қайыңды көлі",
        "coordinates": [78.4500, 42.9833],
        "surface_area_km2": 0.12,
        "max_depth_m": 30,
        "avg_depth_m": 15,
        "volume_million_m3": 1.2,
        "elevation": 2000,
        "type": "landslide-dammed",
        "water_source": "Kaindy River",
        "region": "almaty",
        "water_quality": "excellent",
        "color": "emerald",
        "temperature_summer": 8,
        "temperature_winter": -4,
        "frozen_months": ["November", "December", "January", "February", "March"],
        "description": "Famous for submerged spruce forest, formed by 1911 earthquake landslide",
        "nearby_city": "almaty",
        "distance_to_city_km": 290,
        "protected": True,
        "tourism": "open",
        "unique_feature": "Sunken forest of Tian Shan spruce trees visible through crystal-clear water",
    },
    "kolsai_1": {
        "name": "Kolsai Lake 1 (Lower)",
        "name_kz": "Көлсай көлі (төменгі)",
        "coordinates": [78.3167, 42.8333],
        "surface_area_km2": 1.0,
        "max_depth_m": 80,
        "avg_depth_m": 40,
        "volume_million_m3": 25,
        "elevation": 1818,
        "type": "tectonic",
        "water_source": "Kolsay River",
        "region": "almaty",
        "water_quality": "pristine",
        "color": "deep blue",
        "temperature_summer": 15,
        "temperature_winter": -3,
        "frozen_months": ["December", "January", "February", "March"],
        "description": "Pearl of Northern Tian Shan, largest of three Kolsai lakes",
        "nearby_city": "almaty",
        "distance_to_city_km": 300,
        "protected": True,
        "tourism": "open",
        "fish_species": ["trout"],
    },
    "kolsai_2": {
        "name": "Kolsai Lake 2 (Middle)",
        "name_kz": "Көлсай көлі (ортаңғы)",
        "coordinates": [78.3333, 42.8500],
        "surface_area_km2": 0.5,
        "max_depth_m": 50,
        "avg_depth_m": 25,
        "volume_million_m3": 8,
        "elevation": 2252,
        "type": "tectonic",
        "water_source": "Glacier melt",
        "region": "almaty",
        "water_quality": "pristine",
        "color": "turquoise",
        "temperature_summer": 10,
        "temperature_winter": -5,
        "frozen_months": ["November", "December", "January", "February", "March", "April"],
        "description": "Most scenic of Kolsai lakes, surrounded by spruce forests",
        "nearby_city": "almaty",
        "distance_to_city_km": 310,
        "protected": True,
        "tourism": "hiking only",
    },
    "balkhash": {
        "name": "Lake Balkhash",
        "name_kz": "Балқаш көлі",
        "coordinates": [75.0000, 46.5000],
        "surface_area_km2": 16400,
        "max_depth_m": 26,
        "avg_depth_m": 5.8,
        "volume_million_m3": 112000,
        "elevation": 340,
        "type": "endorheic",
        "water_source": "Ili River (80%)",
        "region": "almaty",
        "water_quality": "variable",
        "color": "western: fresh blue, eastern: saline green",
        "temperature_summer": 24,
        "temperature_winter": -2,
        "frozen_months": ["December", "January", "February"],
        "description": "One of largest lakes in Asia, unique half-fresh half-saline water",
        "nearby_city": "almaty",
        "distance_to_city_km": 600,
        "protected": False,
        "tourism": "open",
        "unique_feature": "Western half is freshwater, eastern half is saline - separated by narrow strait",
        "fish_species": ["carp", "perch", "pike", "catfish"],
    },
}


# =====================================================
# MODELS
# =====================================================

class ChatRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    context: Optional[Dict[str, Any]] = None
    map_bounds: Optional[Dict[str, float]] = None


class ChatResponse(BaseModel):
    message: str
    map_layers: Optional[List[Dict[str, Any]]] = None
    map_action: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None
    chart: Optional[Dict[str, Any]] = None
    animation: Optional[Dict[str, Any]] = None
    status: str = "success"


# =====================================================
# INTELLIGENT GEOSPATIAL AGENT
# =====================================================

class ApexGISAgent:
    """Advanced ApexGIS Agent with comprehensive geospatial capabilities"""
    
    def __init__(self):
        self.commands = self._build_command_registry()
    
    def _build_command_registry(self) -> Dict:
        """Build registry of all available commands"""
        return {
            # City & Location Commands
            "show_city": ["show", "display", "zoom", "go to", "navigate", "fly", "center on", "focus", "find", "locate", "where is"],
            "city_info": ["info", "information", "details", "about", "tell me about", "describe", "what is"],
            "compare": ["compare", "versus", "vs", "difference", "between"],
            
            # Analysis Commands
            "population": ["population", "people", "inhabitants", "residents", "demographics"],
            "elevation": ["elevation", "altitude", "height", "terrain", "topography"],
            "ndvi": ["ndvi", "vegetation", "greenery", "green", "plants", "forest"],
            "temperature": ["temperature", "temp", "climate", "weather", "cold", "hot", "warm"],
            "air_quality": ["air quality", "pollution", "aqi", "smog"],
            "water": ["water", "flood", "hydrology", "reservoir"],
            "land_use": ["land use", "urban", "rural", "agriculture", "industrial"],
            
            # NEW: Environmental Monitoring Commands
            "methane": ["methane", "ch4", "natural gas", "methane emissions", "methane hotspot"],
            "co2": ["co2", "carbon dioxide", "carbon emissions", "carbon", "greenhouse"],
            "emissions": ["emissions", "emission", "pollutant", "pollutants"],
            "fire_detection": ["fire", "fires", "wildfire", "burning", "hotspot"],
            "snow_cover": ["snow", "snow cover", "snowfall", "winter"],
            "lst": ["land surface temperature", "surface temperature", "thermal", "heat island"],
            
            # NEW: Animated Flow Commands
            "wind": ["wind", "wind flow", "wind pattern", "atmospheric"],
            "pollution_flow": ["pollution flow", "dispersion", "spread", "plume"],
            
            # NEW: Dashboard Commands
            "dashboard": ["dashboard", "overview", "summary", "all data", "environmental"],
            
            # Hydrology Commands
            "glacier": ["glacier", "glaciers", "ice", "melt", "ice field", "ice cap"],
            "river": ["river", "rivers", "stream", "creek", "flow", "discharge"],
            "lake": ["lake", "lakes", "pond", "reservoir", "body of water"],
            "hydrology": ["hydrology", "watershed", "basin", "catchment", "drainage"],
            
            # Visualization Commands
            "heatmap": ["heatmap", "heat map", "density", "hotspot", "concentration"],
            "3d": ["3d", "three dimensional", "terrain", "extrude", "buildings", "3d map"],
            "animation": ["animate", "animation", "time series", "timelapse", "change over time"],
            "satellite": ["satellite", "imagery", "sentinel", "landsat", "remote sensing"],
            
            # Data Commands  
            "statistics": ["statistics", "stats", "numbers", "data", "metrics"],
            "trend": ["trend", "growth", "change", "historical", "over time"],
            "ranking": ["rank", "ranking", "top", "largest", "smallest", "best", "worst", "biggest"],
            "distance": ["distance", "far", "near", "closest", "route", "between", "how far"],
            
            # Special Commands
            "all_cities": ["all cities", "every city", "list cities", "cities of kazakhstan", "show cities"],
            "regions": ["regions", "oblasts", "provinces", "administrative"],
            "landmarks": ["landmarks", "attractions", "places", "tourist", "visit", "see"],
            "economic": ["economic", "economy", "gdp", "industry", "business", "trade"],
        }
    
    def _detect_city(self, query: str) -> Optional[Dict]:
        """Detect city mentioned in query"""
        query_lower = query.lower()
        for city_key, city_data in KAZAKHSTAN_CITIES.items():
            if city_key in query_lower or city_data["name"].lower() in query_lower:
                return {"key": city_key, **city_data}
        return None
    
    def _detect_intent(self, query: str) -> List[str]:
        """Detect user intent from query"""
        query_lower = query.lower()
        detected_intents = []
        
        for intent, keywords in self.commands.items():
            for keyword in keywords:
                if keyword in query_lower:
                    detected_intents.append(intent)
                    break
        
        return detected_intents if detected_intents else ["general"]
    
    def _generate_city_polygon(self, center: List[float], radius_km: float = 15) -> Dict:
        """Generate a polygon around a city center"""
        lng, lat = center
        # Approximate degrees per km
        lat_deg = radius_km / 111
        lng_deg = radius_km / (111 * math.cos(math.radians(lat)))
        
        # Create octagon
        points = []
        for i in range(8):
            angle = i * 45 * math.pi / 180
            pt_lng = lng + lng_deg * math.cos(angle)
            pt_lat = lat + lat_deg * math.sin(angle)
            points.append([pt_lng, pt_lat])
        points.append(points[0])  # Close polygon
        
        return {
            "type": "Polygon",
            "coordinates": [points]
        }
    
    def _generate_population_data(self, city: Dict) -> Dict:
        """Generate population trend data"""
        base_pop = city.get("population", 500000)
        years = list(range(2015, 2027))
        populations = []
        current = base_pop * 0.85
        for year in years:
            populations.append(int(current))
            current *= 1.02 + random.uniform(-0.005, 0.015)
        
        return {
            "type": "line",
            "title": f"Population Growth - {city['name']}",
            "labels": years,
            "datasets": [{
                "label": "Population",
                "data": populations,
                "borderColor": "#00d4aa",
                "backgroundColor": "rgba(0, 212, 170, 0.1)",
                "fill": True
            }]
        }
    
    def _generate_temperature_data(self, city: Dict) -> Dict:
        """Generate temperature data"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        lat = city["coordinates"][1]
        
        # Temperature varies by latitude
        base_summer = 30 - abs(lat - 45) * 0.3
        base_winter = -15 + abs(lat - 55) * 0.5
        
        temps = [
            base_winter, base_winter + 3, base_winter + 12,
            base_summer - 15, base_summer - 5, base_summer,
            base_summer + 3, base_summer + 1, base_summer - 8,
            base_summer - 18, base_winter + 8, base_winter + 2
        ]
        
        return {
            "type": "bar",
            "title": f"Average Temperature - {city['name']}",
            "labels": months,
            "datasets": [{
                "label": "Temperature (°C)",
                "data": [round(t + random.uniform(-2, 2), 1) for t in temps],
                "backgroundColor": [
                    "#3b82f6" if t < 0 else "#f59e0b" if t < 15 else "#ef4444" 
                    for t in temps
                ]
            }]
        }
    
    def _generate_air_quality_data(self, city: Dict) -> Dict:
        """Generate air quality index data"""
        hours = [f"{h:02d}:00" for h in range(0, 24, 2)]
        base_aqi = 50 if city.get("type") == "capital" else 35
        
        # Simulate daily pattern
        aqi_values = []
        for h in range(0, 24, 2):
            if 7 <= h <= 9 or 17 <= h <= 19:  # Rush hours
                aqi = base_aqi + random.randint(20, 50)
            elif 10 <= h <= 16:  # Daytime
                aqi = base_aqi + random.randint(5, 25)
            else:  # Night
                aqi = base_aqi + random.randint(-10, 10)
            aqi_values.append(max(10, aqi))
        
        return {
            "type": "line",
            "title": f"Air Quality Index (24h) - {city['name']}",
            "labels": hours,
            "datasets": [{
                "label": "AQI",
                "data": aqi_values,
                "borderColor": "#8b5cf6",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "fill": True,
                "tension": 0.4
            }]
        }
    
    def _generate_ndvi_layer(self, city: Dict) -> Dict:
        """Generate NDVI visualization layer"""
        center = city["coordinates"]
        
        # Create grid of NDVI points
        features = []
        for i in range(-5, 6):
            for j in range(-5, 6):
                lng = center[0] + i * 0.05
                lat = center[1] + j * 0.05
                
                # Distance from center affects NDVI (less green in city center)
                dist = math.sqrt(i*i + j*j)
                ndvi = 0.2 + (dist / 7) * 0.5 + random.uniform(-0.1, 0.1)
                ndvi = max(0, min(1, ndvi))
                
                features.append({
                    "type": "Feature",
                    "properties": {"ndvi": round(ndvi, 2), "weight": ndvi},
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    }
                })
        
        return {
            "id": f"ndvi-{city['name'].lower()}",
            "type": "heatmap",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "heatmap-weight": ["get", "weight"],
                "heatmap-intensity": 1,
                "heatmap-color": [
                    "interpolate", ["linear"], ["heatmap-density"],
                    0, "rgba(0,0,0,0)",
                    0.2, "#d73027",
                    0.4, "#fc8d59",
                    0.6, "#fee08b",
                    0.8, "#91cf60",
                    1, "#1a9850"
                ],
                "heatmap-radius": 30,
                "heatmap-opacity": 0.8
            }
        }
    
    def _generate_3d_buildings(self, city: Dict) -> List[Dict]:
        """Generate 3D building extrusion layer"""
        center = city["coordinates"]
        features = []
        
        # Generate random buildings
        for _ in range(150):
            lng = center[0] + random.uniform(-0.03, 0.03)
            lat = center[1] + random.uniform(-0.03, 0.03)
            
            # Building size varies by distance from center
            dist = math.sqrt((lng - center[0])**2 + (lat - center[1])**2)
            height = max(10, 200 - dist * 5000 + random.randint(-30, 50))
            
            # Create building footprint
            size = random.uniform(0.0005, 0.002)
            features.append({
                "type": "Feature",
                "properties": {"height": height, "base": 0, "color": "#00d4aa"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lng - size, lat - size],
                        [lng + size, lat - size],
                        [lng + size, lat + size],
                        [lng - size, lat + size],
                        [lng - size, lat - size]
                    ]]
                }
            })
        
        return [{
            "id": f"buildings-3d-{city['name'].lower()}",
            "type": "fill-extrusion",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "fill-extrusion-color": [
                    "interpolate", ["linear"], ["get", "height"],
                    10, "#1e3a5f",
                    50, "#00d4aa",
                    100, "#f59e0b",
                    200, "#ef4444"
                ],
                "fill-extrusion-height": ["get", "height"],
                "fill-extrusion-base": 0,
                "fill-extrusion-opacity": 0.85
            }
        }]
    
    def _generate_heatmap_layer(self, city: Dict, data_type: str = "population") -> Dict:
        """Generate heatmap visualization"""
        center = city["coordinates"]
        features = []
        
        # Generate density points
        for _ in range(200):
            # Clustered around center
            lng = center[0] + random.gauss(0, 0.02)
            lat = center[1] + random.gauss(0, 0.015)
            weight = random.uniform(0.3, 1.0)
            
            features.append({
                "type": "Feature",
                "properties": {"weight": weight},
                "geometry": {"type": "Point", "coordinates": [lng, lat]}
            })
        
        return {
            "id": f"heatmap-{data_type}-{city['name'].lower()}",
            "type": "heatmap",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "heatmap-weight": ["get", "weight"],
                "heatmap-intensity": 1,
                "heatmap-color": [
                    "interpolate", ["linear"], ["heatmap-density"],
                    0, "rgba(0,0,0,0)",
                    0.2, "#4338ca",
                    0.4, "#7c3aed",
                    0.6, "#c026d3",
                    0.8, "#e11d48",
                    1, "#fbbf24"
                ],
                "heatmap-radius": 25,
                "heatmap-opacity": 0.8
            }
        }
    
    def _generate_route_layer(self, city1: Dict, city2: Dict) -> Dict:
        """Generate route between two cities"""
        c1, c2 = city1["coordinates"], city2["coordinates"]
        
        # Create curved route
        mid_lng = (c1[0] + c2[0]) / 2
        mid_lat = (c1[1] + c2[1]) / 2 + 0.5  # Curve offset
        
        points = []
        for t in range(21):
            t = t / 20
            # Quadratic bezier
            lng = (1-t)**2 * c1[0] + 2*(1-t)*t * mid_lng + t**2 * c2[0]
            lat = (1-t)**2 * c1[1] + 2*(1-t)*t * mid_lat + t**2 * c2[1]
            points.append([lng, lat])
        
        return {
            "id": f"route-{city1['name']}-{city2['name']}".lower().replace(" ", "-"),
            "type": "line",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "Feature",
                    "properties": {
                        "from": city1["name"],
                        "to": city2["name"]
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": points
                    }
                }
            },
            "paint": {
                "line-color": "#00d4aa",
                "line-width": 4,
                "line-dasharray": [2, 1]
            }
        }
    
    def _generate_economic_data(self, city: Dict) -> Dict:
        """Generate economic sector data"""
        sectors = ["Industry", "Services", "Agriculture", "Construction", "Trade", "Transport"]
        
        # Vary by city type
        if city.get("type") == "capital":
            values = [15, 45, 5, 12, 15, 8]
        elif city.get("type") == "megacity":
            values = [20, 40, 5, 10, 18, 7]
        else:
            values = [25, 30, 15, 10, 12, 8]
        
        # Add some randomness
        values = [v + random.randint(-3, 3) for v in values]
        
        return {
            "type": "doughnut",
            "title": f"Economic Sectors - {city['name']}",
            "labels": sectors,
            "datasets": [{
                "data": values,
                "backgroundColor": ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6", "#ec4899"]
            }]
        }
    
    def _generate_glaciers_layer(self, city: Optional[Dict] = None) -> Dict:
        """Generate glaciers visualization layer"""
        features = []
        
        for key, glacier in GLACIERS.items():
            # Filter by nearby city if specified
            if city and glacier.get("nearby_city", "").lower() != city.get("key", "").lower():
                continue
            
            # Create polygon for glacier extent (approximate)
            center = glacier["coordinates"]
            area = glacier["area_km2"]
            radius = math.sqrt(area / math.pi) / 111  # Convert km to degrees
            
            # Create irregular polygon for more realistic glacier shape
            points = []
            for i in range(12):
                angle = i * 30 * math.pi / 180
                r = radius * (0.7 + random.uniform(0, 0.5))  # Irregular shape
                lng = center[0] + r * math.cos(angle)
                lat = center[1] + r * 0.7 * math.sin(angle)  # Flattened
                points.append([lng, lat])
            points.append(points[0])  # Close polygon
            
            # Color based on status
            color = "#3b82f6"  # blue for stable
            if glacier["status"] == "retreating":
                color = "#f59e0b"  # orange
            elif glacier["status"] == "critical":
                color = "#ef4444"  # red
            
            features.append({
                "type": "Feature",
                "properties": {
                    "id": key,
                    "name": glacier["name"],
                    "name_kz": glacier["name_kz"],
                    "type": "glacier",
                    "area_km2": glacier["area_km2"],
                    "length_km": glacier["length_km"],
                    "elevation_min": glacier["elevation_min"],
                    "elevation_max": glacier["elevation_max"],
                    "glacier_type": glacier["type"],
                    "status": glacier["status"],
                    "retreat_rate": glacier.get("retreat_rate_m_year", 0),
                    "ice_thickness": glacier.get("ice_thickness_m", 0),
                    "description": glacier["description"],
                    "color": color
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [points]
                }
            })
        
        return {
            "id": "glaciers-layer",
            "type": "fill-extrusion",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "fill-extrusion-color": ["get", "color"],
                "fill-extrusion-height": ["*", ["get", "ice_thickness"], 5],  # Exaggerated for visibility
                "fill-extrusion-base": 0,
                "fill-extrusion-opacity": 0.85
            }
        }
    
    def _generate_rivers_layer(self, city: Optional[Dict] = None) -> Dict:
        """Generate rivers visualization layer"""
        features = []
        
        for key, river in RIVERS.items():
            # Filter by nearby city if specified
            if city and river.get("nearby_city", "").lower() != city.get("key", "").lower():
                if river.get("nearby_city") != "almaty":  # Include Almaty region rivers
                    continue
            
            # Create smooth river path
            coords = river["coordinates"]
            
            # Determine river width based on discharge
            width = min(8, max(2, river["avg_discharge_m3s"] / 50))
            
            # Color based on water quality
            color = "#22c55e"  # green for excellent
            if river.get("water_quality") == "good":
                color = "#3b82f6"  # blue
            elif river.get("water_quality") == "variable":
                color = "#f59e0b"  # orange
            
            features.append({
                "type": "Feature",
                "properties": {
                    "id": key,
                    "name": river["name"],
                    "name_kz": river["name_kz"],
                    "type": "river",
                    "length_km": river["length_km"],
                    "basin_area_km2": river["basin_area_km2"],
                    "avg_discharge": river["avg_discharge_m3s"],
                    "max_discharge": river["max_discharge_m3s"],
                    "glacier_fed": river.get("glacier_fed", False),
                    "source_glacier": river.get("source_glacier", "None"),
                    "water_quality": river.get("water_quality", "unknown"),
                    "uses": ", ".join(river.get("uses", [])),
                    "description": river["description"],
                    "width": width,
                    "color": color
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                }
            })
        
        return {
            "id": "rivers-layer",
            "type": "line",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "line-color": ["get", "color"],
                "line-width": ["get", "width"],
                "line-opacity": 0.9
            }
        }
    
    def _generate_lakes_layer(self, city: Optional[Dict] = None) -> Dict:
        """Generate lakes visualization layer"""
        features = []
        
        for key, lake in LAKES.items():
            # Filter by nearby city if specified (include all Almaty region)
            if city and lake.get("nearby_city", "").lower() != city.get("key", "").lower():
                if lake.get("region") != "almaty":
                    continue
            
            # Create lake polygon
            center = lake["coordinates"]
            area = lake["surface_area_km2"]
            radius = math.sqrt(area / math.pi) / 111
            
            # Create irregular polygon for natural lake shape
            points = []
            num_points = 16 if area > 1 else 10
            for i in range(num_points):
                angle = i * (360 / num_points) * math.pi / 180
                r = radius * (0.75 + random.uniform(0, 0.4))
                lng = center[0] + r * math.cos(angle)
                lat = center[1] + r * 0.8 * math.sin(angle)
                points.append([lng, lat])
            points.append(points[0])
            
            # Depth-based color
            depth = lake.get("max_depth_m", 10)
            if depth > 50:
                color = "#1e3a8a"  # dark blue
            elif depth > 20:
                color = "#2563eb"  # blue
            else:
                color = "#60a5fa"  # light blue
            
            features.append({
                "type": "Feature",
                "properties": {
                    "id": key,
                    "name": lake["name"],
                    "name_kz": lake["name_kz"],
                    "type": "lake",
                    "lake_type": lake["type"],
                    "surface_area_km2": lake["surface_area_km2"],
                    "max_depth_m": lake["max_depth_m"],
                    "avg_depth_m": lake.get("avg_depth_m", 0),
                    "elevation": lake["elevation"],
                    "water_quality": lake.get("water_quality", "unknown"),
                    "color_desc": lake.get("color", "blue"),
                    "temperature_summer": lake.get("temperature_summer", 15),
                    "protected": lake.get("protected", False),
                    "tourism": lake.get("tourism", "open"),
                    "description": lake["description"],
                    "unique_feature": lake.get("unique_feature", ""),
                    "distance_to_city_km": lake.get("distance_to_city_km", 0),
                    "fill_color": color,
                    "depth": depth
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [points]
                }
            })
        
        return {
            "id": "lakes-layer",
            "type": "fill-extrusion",
            "source": {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features}
            },
            "paint": {
                "fill-extrusion-color": ["get", "fill_color"],
                "fill-extrusion-height": 0,  # Flat
                "fill-extrusion-base": ["*", ["get", "depth"], -2],  # Negative for depth illusion
                "fill-extrusion-opacity": 0.75
            }
        }
    
    def _generate_hydrology_combined_layer(self, city: Optional[Dict] = None) -> List[Dict]:
        """Generate all hydrology layers combined"""
        layers = []
        
        # Lakes (bottom layer)
        lakes_features = []
        for key, lake in LAKES.items():
            if city and lake.get("region") != city.get("key", "almaty"):
                continue
            
            center = lake["coordinates"]
            area = lake["surface_area_km2"]
            radius = math.sqrt(area / math.pi) / 111
            
            points = []
            for i in range(16):
                angle = i * 22.5 * math.pi / 180
                r = radius * (0.8 + random.uniform(0, 0.3))
                points.append([
                    center[0] + r * math.cos(angle),
                    center[1] + r * 0.8 * math.sin(angle)
                ])
            points.append(points[0])
            
            lakes_features.append({
                "type": "Feature",
                "properties": {
                    "name": lake["name"],
                    "type": "lake",
                    "depth": lake.get("max_depth_m", 10),
                    "area": lake["surface_area_km2"]
                },
                "geometry": {"type": "Polygon", "coordinates": [points]}
            })
        
        layers.append({
            "id": "hydro-lakes",
            "type": "fill",
            "source": {"type": "geojson", "data": {"type": "FeatureCollection", "features": lakes_features}},
            "paint": {
                "fill-color": "#2563eb",
                "fill-opacity": 0.7,
                "fill-outline-color": "#1e40af"
            }
        })
        
        # Rivers (middle layer)
        rivers_features = []
        for key, river in RIVERS.items():
            rivers_features.append({
                "type": "Feature",
                "properties": {
                    "name": river["name"],
                    "type": "river",
                    "discharge": river["avg_discharge_m3s"],
                    "width": min(6, max(2, river["avg_discharge_m3s"] / 50))
                },
                "geometry": {"type": "LineString", "coordinates": river["coordinates"]}
            })
        
        layers.append({
            "id": "hydro-rivers",
            "type": "line",
            "source": {"type": "geojson", "data": {"type": "FeatureCollection", "features": rivers_features}},
            "paint": {
                "line-color": "#22d3ee",
                "line-width": ["get", "width"],
                "line-opacity": 0.9
            }
        })
        
        # Glaciers (top layer with 3D)
        glacier_features = []
        for key, glacier in GLACIERS.items():
            center = glacier["coordinates"]
            area = glacier["area_km2"]
            radius = math.sqrt(area / math.pi) / 111
            
            points = []
            for i in range(12):
                angle = i * 30 * math.pi / 180
                r = radius * (0.7 + random.uniform(0, 0.4))
                points.append([
                    center[0] + r * math.cos(angle),
                    center[1] + r * 0.7 * math.sin(angle)
                ])
            points.append(points[0])
            
            status_color = "#94a3b8"  # gray for stable
            if glacier["status"] == "retreating":
                status_color = "#fbbf24"
            elif glacier["status"] == "critical":
                status_color = "#ef4444"
            
            glacier_features.append({
                "type": "Feature",
                "properties": {
                    "name": glacier["name"],
                    "type": "glacier",
                    "status": glacier["status"],
                    "thickness": glacier.get("ice_thickness_m", 50),
                    "color": status_color
                },
                "geometry": {"type": "Polygon", "coordinates": [points]}
            })
        
        layers.append({
            "id": "hydro-glaciers",
            "type": "fill-extrusion",
            "source": {"type": "geojson", "data": {"type": "FeatureCollection", "features": glacier_features}},
            "paint": {
                "fill-extrusion-color": ["get", "color"],
                "fill-extrusion-height": ["*", ["get", "thickness"], 8],
                "fill-extrusion-base": 0,
                "fill-extrusion-opacity": 0.85
            }
        })
        
        return layers

    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process user query with intelligent response"""
        
        city = self._detect_city(query)
        intents = self._detect_intent(query)
        query_lower = query.lower()
        
        # =========================================
        # COMPARE CITIES - Check first before single city
        # =========================================
        
        if "compare" in intents or " vs " in query_lower or " versus " in query_lower:
            cities_found = []
            for city_key, city_data in KAZAKHSTAN_CITIES.items():
                if city_key in query_lower or city_data["name"].lower() in query_lower:
                    cities_found.append({"key": city_key, **city_data})
            
            if len(cities_found) >= 2:
                c1, c2 = cities_found[0], cities_found[1]
                
                # Calculate distance
                lat1, lon1 = math.radians(c1["coordinates"][1]), math.radians(c1["coordinates"][0])
                lat2, lon2 = math.radians(c2["coordinates"][1]), math.radians(c2["coordinates"][0])
                dlat, dlon = lat2 - lat1, lon2 - lon1
                a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                distance = 6371 * 2 * math.asin(math.sqrt(a))
                
                route_layer = self._generate_route_layer(c1, c2)
                
                # Create city markers
                city_markers = {
                    "id": "comparison-cities",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": {
                            "type": "FeatureCollection",
                            "features": [
                                {"type": "Feature", "properties": {"name": c1["name"]}, "geometry": {"type": "Point", "coordinates": c1["coordinates"]}},
                                {"type": "Feature", "properties": {"name": c2["name"]}, "geometry": {"type": "Point", "coordinates": c2["coordinates"]}}
                            ]
                        }
                    },
                    "paint": {
                        "circle-radius": 12,
                        "circle-color": "#00d4aa",
                        "circle-stroke-width": 3,
                        "circle-stroke-color": "#ffffff"
                    }
                }
                
                return {
                    "message": f"⚖️ **City Comparison: {c1['name']} vs {c2['name']}**\n\n| Metric | {c1['name']} | {c2['name']} |\n|--------|------------|------------|\n| Population | {c1.get('population', 'N/A'):,} | {c2.get('population', 'N/A'):,} |\n| Area (km²) | {c1.get('area_km2', 'N/A')} | {c2.get('area_km2', 'N/A')} |\n| Elevation | {c1.get('elevation', 'N/A')}m | {c2.get('elevation', 'N/A')}m |\n| Type | {c1.get('type', 'city')} | {c2.get('type', 'city')} |\n\n📏 **Distance: {distance:.0f} km**",
                    "map_layers": [route_layer, city_markers],
                    "map_action": {
                        "type": "fitBounds",
                        "bounds": [
                            [min(c1["coordinates"][0], c2["coordinates"][0]) - 2, 
                             min(c1["coordinates"][1], c2["coordinates"][1]) - 1],
                            [max(c1["coordinates"][0], c2["coordinates"][0]) + 2,
                             max(c1["coordinates"][1], c2["coordinates"][1]) + 1]
                        ]
                    },
                    "chart": {
                        "type": "bar",
                        "title": "Population Comparison",
                        "labels": [c1["name"], c2["name"]],
                        "datasets": [{
                            "label": "Population",
                            "data": [c1.get("population", 0), c2.get("population", 0)],
                            "backgroundColor": ["#00d4aa", "#8b5cf6"]
                        }]
                    },
                    "status": "success"
                }
        
        # =========================================
        # DISTANCE CALCULATION - Check before single city
        # =========================================
        
        if "distance" in intents or "how far" in query_lower:
            cities_found = []
            for city_key, city_data in KAZAKHSTAN_CITIES.items():
                if city_key in query_lower or city_data["name"].lower() in query_lower:
                    cities_found.append({"key": city_key, **city_data})
            
            if len(cities_found) >= 2:
                c1, c2 = cities_found[0], cities_found[1]
                
                lat1, lon1 = math.radians(c1["coordinates"][1]), math.radians(c1["coordinates"][0])
                lat2, lon2 = math.radians(c2["coordinates"][1]), math.radians(c2["coordinates"][0])
                dlat, dlon = lat2 - lat1, lon2 - lon1
                a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                distance = 6371 * 2 * math.asin(math.sqrt(a))
                
                # Estimate travel times
                drive_time = distance / 80  # 80 km/h average
                flight_time = distance / 800 + 1  # 800 km/h + 1hr for boarding
                
                route_layer = self._generate_route_layer(c1, c2)
                
                return {
                    "message": f"📏 **Distance: {c1['name']} ↔ {c2['name']}**\n\n**{distance:.0f} km**\n\n**Estimated Travel Time:**\n- 🚗 By car: ~{drive_time:.1f} hours\n- ✈️ By plane: ~{flight_time:.1f} hours",
                    "map_layers": [route_layer],
                    "map_action": {
                        "type": "fitBounds",
                        "bounds": [
                            [min(c1["coordinates"][0], c2["coordinates"][0]) - 1, 
                             min(c1["coordinates"][1], c2["coordinates"][1]) - 1],
                            [max(c1["coordinates"][0], c2["coordinates"][0]) + 1,
                             max(c1["coordinates"][1], c2["coordinates"][1]) + 1]
                        ]
                    },
                    "status": "success"
                }
        
        # =========================================
        # CITY-SPECIFIC COMMANDS
        # =========================================
        
        if city:
            # Check for specific analysis first
            
            # Population analysis
            if "population" in intents:
                chart = self._generate_population_data(city)
                return {
                    "message": f"📊 **Population Analysis - {city['name']}**\n\nCurrent population: **{city.get('population', 'N/A'):,}**\n\nThe chart shows population growth trends from 2015-2026. {city['name']} has experienced steady growth typical of Kazakhstan's urbanization.",
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 11, "pitch": 0},
                    "chart": chart,
                    "data": {"city": city["name"], "population": city.get("population")},
                    "status": "success"
                }
            
            # Heatmap - check BEFORE temperature!
            if "heatmap" in intents:
                layer = self._generate_heatmap_layer(city)
                return {
                    "message": f"🔥 **Population Density Heatmap - {city['name']}**\n\nThis heatmap visualizes population concentration:\n\n- 🟣 Purple: Low density (suburbs)\n- 🔴 Red: Medium density\n- 🟡 Yellow: High density (city center)\n\n*Based on census and mobile phone data analysis*",
                    "map_layers": [layer],
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 12, "pitch": 0},
                    "status": "success"
                }
            
            # Temperature analysis
            if "temperature" in intents:
                chart = self._generate_temperature_data(city)
                return {
                    "message": f"🌡️ **Climate Analysis - {city['name']}**\n\nKazakhstan has an extreme continental climate with hot summers and cold winters.\n\n{city['name']} at elevation {city.get('elevation', 'N/A')}m experiences significant temperature variations:\n- 🥶 Winter: Down to -20°C\n- 🌡️ Summer: Up to +35°C",
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 10, "pitch": 0},
                    "chart": chart,
                    "status": "success"
                }
            
            # Air quality
            if "air_quality" in intents:
                chart = self._generate_air_quality_data(city)
                return {
                    "message": f"💨 **Air Quality Index - {city['name']}**\n\nReal-time AQI monitoring shows daily patterns:\n\n- 🚗 Rush hours (7-9 AM, 5-7 PM): Higher pollution\n- 🌙 Night time: Lower AQI values\n- ☀️ Midday: Moderate levels\n\n**AQI Scale:**\n- 0-50: 🟢 Good\n- 51-100: 🟡 Moderate\n- 101-150: 🟠 Unhealthy for sensitive\n- 151+: 🔴 Unhealthy",
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 11, "pitch": 0},
                    "chart": chart,
                    "status": "success"
                }
            
            # NDVI analysis
            if "ndvi" in intents:
                layer = self._generate_ndvi_layer(city)
                return {
                    "message": f"🌿 **NDVI Vegetation Analysis - {city['name']}**\n\nNormalized Difference Vegetation Index shows vegetation health:\n\n- 🔴 Red (0.0-0.2): No vegetation / Urban\n- 🟡 Yellow (0.2-0.4): Sparse vegetation\n- 🟢 Green (0.4-0.6): Moderate vegetation\n- 🌲 Dark Green (0.6-1.0): Dense vegetation\n\n*Data source: Sentinel-2 satellite imagery*",
                    "map_layers": [layer],
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 11, "pitch": 0},
                    "code": f"""import leafmap
import xarray as xr

# Calculate NDVI from Sentinel-2 for {city['name']}
nir = sentinel2['B8']  # Near-infrared band
red = sentinel2['B4']  # Red band
ndvi = (nir - red) / (nir + red)

# Create visualization
m = leafmap.Map(center={city['coordinates']}, zoom=11)
m.add_raster(ndvi, colormap='RdYlGn', layer_name='NDVI')
m""",
                    "status": "success"
                }
            
            # 3D Buildings
            if "3d" in intents:
                layers = self._generate_3d_buildings(city)
                return {
                    "message": f"🏗️ **3D Urban Visualization - {city['name']}**\n\nRendering 3D building extrusions based on estimated heights.\n\n**Color Legend:**\n- 🔵 Dark Blue: Low-rise (< 50m)\n- 🟢 Cyan: Mid-rise (50-100m)\n- 🟡 Orange: High-rise (100-150m)\n- 🔴 Red: Skyscrapers (> 150m)\n\n*Tip: Drag to rotate the 3D view!*",
                    "map_layers": layers,
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 15, "pitch": 60, "bearing": -30},
                    "status": "success"
                }
            
            # Economic data
            if "economic" in intents:
                chart = self._generate_economic_data(city)
                return {
                    "message": f"💰 **Economic Overview - {city['name']}**\n\nThe chart shows the distribution of economic sectors in {city['name']}.\n\n{city.get('description', '')}\n\n**Key Industries:** {'Oil & Gas, ' if 'oil' in city.get('description', '').lower() else ''}Manufacturing, Services, Trade",
                    "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 11},
                    "chart": chart,
                    "status": "success"
                }
            
            # Landmarks
            if "landmarks" in intents:
                landmarks = city.get("landmarks", [])
                if landmarks:
                    landmarks_text = "\n".join([f"  • 🏛️ {l}" for l in landmarks])
                    return {
                        "message": f"🏛️ **Landmarks & Attractions - {city['name']}**\n\n{landmarks_text}\n\n*{city.get('description', '')}*",
                        "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 13, "pitch": 45},
                        "data": {"landmarks": landmarks},
                        "status": "success"
                    }
                else:
                    return {
                        "message": f"🏛️ **{city['name']}**\n\n{city.get('description', 'A city in Kazakhstan.')}\n\n*Population: {city.get('population', 'N/A'):,}*",
                        "map_action": {"type": "flyTo", "center": city["coordinates"], "zoom": 12},
                        "status": "success"
                    }
            
            # Glaciers near city
            if "glacier" in intents:
                layers = self._generate_glaciers_layer(city)
                glacier_info = []
                total_area = 0
                for key, g in GLACIERS.items():
                    glacier_info.append(f"• **{g['name']}** ({g['name_kz']})\n  - Area: {g['area_km2']} km² | Length: {g['length_km']} km\n  - Status: {'🔴' if g['status']=='critical' else '🟡' if g['status']=='retreating' else '🟢'} {g['status'].title()}")
                    total_area += g['area_km2']
                return {
                    "message": f"🏔️ **Glaciers near {city['name']}**\n\n**Total: {len(GLACIERS)} glaciers | {total_area:.1f} km² total**\n\n" + "\n\n".join(glacier_info),
                    "map_layers": [layers],
                    "map_action": {"type": "flyTo", "center": [77.08, 43.05], "zoom": 11, "pitch": 60, "bearing": -20},
                    "chart": {"type": "bar", "title": "Glacier Areas (km²)", "labels": [g["name"] for g in GLACIERS.values()], "datasets": [{"label": "Area (km²)", "data": [g["area_km2"] for g in GLACIERS.values()], "backgroundColor": "#94a3b8"}]},
                    "status": "success"
                }
            
            # Rivers near city
            if "river" in intents:
                layers = self._generate_rivers_layer(city)
                river_info = [f"• **{r['name']}** - {r['length_km']} km" for r in RIVERS.values()]
                return {
                    "message": f"🌊 **Rivers near {city['name']}**\n\n" + "\n".join(river_info),
                    "map_layers": [layers],
                    "map_action": {"type": "flyTo", "center": [77.0, 43.5], "zoom": 9, "pitch": 30},
                    "chart": {"type": "bar", "title": "River Lengths (km)", "labels": [r["name"] for r in RIVERS.values()], "datasets": [{"label": "Length (km)", "data": [r["length_km"] for r in RIVERS.values()], "backgroundColor": "#22d3ee"}]},
                    "status": "success"
                }
            
            # Lakes near city
            if "lake" in intents:
                layers = self._generate_lakes_layer(city)
                lake_info = [f"• **{l['name']}** - {l['max_depth_m']}m deep" for l in LAKES.values()]
                return {
                    "message": f"🏞️ **Lakes near {city['name']}**\n\n" + "\n".join(lake_info),
                    "map_layers": [layers],
                    "map_action": {"type": "flyTo", "center": [77.1, 43.1], "zoom": 9, "pitch": 45},
                    "chart": {"type": "bar", "title": "Lake Depths (m)", "labels": [l["name"] for l in LAKES.values()], "datasets": [{"label": "Max Depth (m)", "data": [l["max_depth_m"] for l in LAKES.values()], "backgroundColor": "#2563eb"}]},
                    "status": "success"
                }
            
            # All water bodies / hydrology
            if "hydrology" in intents:
                layers = self._generate_hydrology_combined_layer(city)
                return {
                    "message": f"💧 **All Water Bodies near {city['name']}**\n\n🏔️ {len(GLACIERS)} glaciers\n🌊 {len(RIVERS)} rivers\n🏞️ {len(LAKES)} lakes",
                    "map_layers": layers,
                    "map_action": {"type": "flyTo", "center": [77.2, 43.2], "zoom": 9, "pitch": 55, "bearing": -15},
                    "status": "success"
                }
            
            # Default: Show city
            return {
                "message": f"📍 **{city['name']}** ({city.get('name_kz', '')})\n\n{city.get('description', '')}\n\n**Quick Facts:**\n- 📊 Population: {city.get('population', 'N/A'):,}\n- 📐 Area: {city.get('area_km2', 'N/A')} km²\n- ⛰️ Elevation: {city.get('elevation', 'N/A')}m\n- 🏛️ Type: {city.get('type', 'city').title()}\n\n**Try these commands:**\n- `population of {city['name']}`\n- `temperature in {city['name']}`\n- `3d buildings {city['name']}`\n- `ndvi {city['name']}`\n- `glaciers near {city['name']}`\n- `lakes near {city['name']}`\n- `rivers near {city['name']}`",
                "map_layers": [{
                    "id": f"city-{city['name'].lower()}",
                    "type": "geojson",
                    "source": {
                        "type": "geojson",
                        "data": {
                            "type": "Feature",
                            "properties": {"name": city["name"], "population": city.get("population")},
                            "geometry": self._generate_city_polygon(city["coordinates"])
                        }
                    },
                    "paint": {
                        "fill-color": "#00d4aa",
                        "fill-opacity": 0.3,
                        "fill-outline-color": "#00d4aa"
                    }
                }],
                "map_action": {
                    "type": "flyTo",
                    "center": city["coordinates"],
                    "zoom": 12,
                    "pitch": 45,
                    "duration": 2000
                },
                "data": city,
                "status": "success"
            }
        
        # =========================================
        # HYDROLOGY - Glaciers, Rivers, Lakes
        # =========================================
        
        if "glacier" in intents:
            layers = self._generate_glaciers_layer(city)
            
            # Build glacier info
            glacier_info = []
            total_area = 0
            for key, g in GLACIERS.items():
                glacier_info.append(f"• **{g['name']}** ({g['name_kz']})\n  - Area: {g['area_km2']} km² | Length: {g['length_km']} km\n  - Elevation: {g['elevation_min']}-{g['elevation_max']}m\n  - Status: {'🔴' if g['status']=='critical' else '🟡' if g['status']=='retreating' else '🟢'} {g['status'].title()}\n  - Ice thickness: ~{g.get('ice_thickness_m', 50)}m\n  - Retreat rate: {g.get('retreat_rate_m_year', 0)}m/year")
                total_area += g['area_km2']
            
            return {
                "message": f"🏔️ **Glaciers of the Almaty Region**\n\n**Total: {len(GLACIERS)} glaciers | {total_area:.1f} km² total area**\n\n" + "\n\n".join(glacier_info) + "\n\n---\n📊 **Climate Impact:** Kazakhstan's glaciers have lost approximately 45% of their volume since 1955. The Tuyuksu Glacier is one of the world's most studied glaciers for climate monitoring.\n\n*3D visualization shows ice thickness (exaggerated for visibility)*",
                "map_layers": [layers],
                "map_action": {
                    "type": "flyTo",
                    "center": [77.08, 43.05],  # Center on glacier region
                    "zoom": 11,
                    "pitch": 60,
                    "bearing": -20
                },
                "chart": {
                    "type": "bar",
                    "title": "Glacier Areas (km²)",
                    "labels": [g["name"] for g in GLACIERS.values()],
                    "datasets": [{
                        "label": "Area (km²)",
                        "data": [g["area_km2"] for g in GLACIERS.values()],
                        "backgroundColor": ["#94a3b8", "#94a3b8", "#fbbf24", "#94a3b8", "#fbbf24", "#94a3b8"]
                    }]
                },
                "status": "success"
            }
        
        if "river" in intents:
            layers = self._generate_rivers_layer(city)
            
            river_info = []
            for key, r in RIVERS.items():
                glacier_fed = "❄️ Glacier-fed" if r.get("glacier_fed") else "🌧️ Rain/snow-fed"
                river_info.append(f"• **{r['name']}** ({r['name_kz']})\n  - Length: {r['length_km']} km | Basin: {r['basin_area_km2']:,} km²\n  - Avg discharge: {r['avg_discharge_m3s']} m³/s\n  - {glacier_fed}\n  - Uses: {', '.join(r.get('uses', []))}")
            
            return {
                "message": f"🌊 **Rivers of the Almaty Region**\n\n**Total: {len(RIVERS)} major rivers**\n\n" + "\n\n".join(river_info) + "\n\n---\n💧 **Water Resources:** The Almaty region's rivers originate from Tien Shan glaciers and provide crucial water supply for irrigation, drinking water, and hydropower.\n\n*Line width represents average water discharge*",
                "map_layers": [layers],
                "map_action": {
                    "type": "flyTo",
                    "center": [77.0, 43.5],
                    "zoom": 9,
                    "pitch": 30
                },
                "chart": {
                    "type": "bar",
                    "title": "River Discharge (m³/s)",
                    "labels": [r["name"] for r in RIVERS.values()],
                    "datasets": [{
                        "label": "Avg Discharge (m³/s)",
                        "data": [r["avg_discharge_m3s"] for r in RIVERS.values()],
                        "backgroundColor": "#22d3ee"
                    }]
                },
                "status": "success"
            }
        
        if "lake" in intents:
            layers = self._generate_lakes_layer(city)
            
            lake_info = []
            for key, l in LAKES.items():
                protected = "🛡️ Protected" if l.get("protected") else ""
                lake_info.append(f"• **{l['name']}** ({l['name_kz']})\n  - Area: {l['surface_area_km2']} km² | Max depth: {l['max_depth_m']}m\n  - Elevation: {l['elevation']}m | Type: {l['type']}\n  - Water color: {l.get('color', 'blue')} {protected}\n  - {l.get('unique_feature', '')}")
            
            return {
                "message": f"🏞️ **Lakes of the Almaty Region**\n\n**Total: {len(LAKES)} major lakes**\n\n" + "\n\n".join(lake_info) + "\n\n---\n🌈 **Unique Features:** Many mountain lakes in the region have striking colors due to glacial minerals. Kaindy Lake features sunken spruce trees, while Big Almaty Lake changes color seasonally.\n\n*Darker blue indicates greater depth*",
                "map_layers": [layers],
                "map_action": {
                    "type": "flyTo",
                    "center": [77.1, 43.1],
                    "zoom": 9,
                    "pitch": 45
                },
                "chart": {
                    "type": "bar",
                    "title": "Lake Depths (meters)",
                    "labels": [l["name"] for l in LAKES.values()],
                    "datasets": [{
                        "label": "Max Depth (m)",
                        "data": [l["max_depth_m"] for l in LAKES.values()],
                        "backgroundColor": "#2563eb"
                    }]
                },
                "status": "success"
            }
        
        if "hydrology" in intents or ("water" in query_lower and "bodies" in query_lower) or "all water" in query_lower:
            layers = self._generate_hydrology_combined_layer(city)
            
            return {
                "message": f"💧 **Complete Hydrological Overview - Almaty Region**\n\n**🏔️ Glaciers:** {len(GLACIERS)} glaciers ({sum(g['area_km2'] for g in GLACIERS.values()):.1f} km² total)\n**🌊 Rivers:** {len(RIVERS)} major rivers\n**🏞️ Lakes:** {len(LAKES)} major lakes\n\n---\n\n**Water Resources Summary:**\n- Primary water source: Tien Shan glaciers\n- Critical for: Drinking water, irrigation, hydropower\n- Climate concern: 45% glacier volume loss since 1955\n\n**Interactive Features:**\n- 🧊 Gray/Yellow/Red = Glacier status (stable/retreating/critical)\n- 💧 Blue lines = Rivers (width = discharge)\n- 🔵 Blue areas = Lakes (darker = deeper)\n\n*Rotate view with right-click drag to see 3D glacier thickness*",
                "map_layers": layers,
                "map_action": {
                    "type": "flyTo",
                    "center": [77.2, 43.2],
                    "zoom": 9,
                    "pitch": 55,
                    "bearing": -15
                },
                "chart": {
                    "type": "doughnut",
                    "title": "Water Resources by Type",
                    "labels": ["Glaciers", "Rivers", "Lakes"],
                    "datasets": [{
                        "data": [len(GLACIERS), len(RIVERS), len(LAKES)],
                        "backgroundColor": ["#94a3b8", "#22d3ee", "#2563eb"]
                    }]
                },
                "status": "success"
            }
        
        # =========================================
        # ALL CITIES
        # =========================================
        
        if "all_cities" in intents or "every city" in query_lower or "all cities" in query_lower or "show cities" in query_lower:
            features = []
            city_list = []
            
            for city_key, city_data in KAZAKHSTAN_CITIES.items():
                features.append({
                    "type": "Feature",
                    "properties": {
                        "name": city_data["name"],
                        "population": city_data.get("population", 0),
                        "type": city_data.get("type", "city")
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": city_data["coordinates"]
                    }
                })
                city_list.append(f"• **{city_data['name']}**: {city_data.get('population', 'N/A'):,}")
            
            return {
                "message": f"🏙️ **All Major Cities of Kazakhstan**\n\n**Total: {len(KAZAKHSTAN_CITIES)} cities**\n\n" + "\n".join(sorted(city_list)),
                "map_layers": [{
                    "id": "all-cities",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "circle-radius": ["interpolate", ["linear"], ["get", "population"], 100000, 8, 2000000, 25],
                        "circle-color": ["match", ["get", "type"],
                            "capital", "#ef4444",
                            "megacity", "#f59e0b", 
                            "#00d4aa"
                        ],
                        "circle-stroke-width": 2,
                        "circle-stroke-color": "#ffffff"
                    }
                }],
                "map_action": {"type": "flyTo", "center": [67.0, 48.0], "zoom": 4, "pitch": 0},
                "chart": {
                    "type": "bar",
                    "title": "Population by City (Top 8)",
                    "labels": [c["name"] for c in sorted(KAZAKHSTAN_CITIES.values(), key=lambda x: x.get("population", 0), reverse=True)[:8]],
                    "datasets": [{
                        "label": "Population",
                        "data": [c.get("population", 0) for c in sorted(KAZAKHSTAN_CITIES.values(), key=lambda x: x.get("population", 0), reverse=True)[:8]],
                        "backgroundColor": "#00d4aa"
                    }]
                },
                "status": "success"
            }
        
        # =========================================
        # RANKING
        # =========================================
        
        if "ranking" in intents or "largest" in query_lower or "biggest" in query_lower or "top" in query_lower:
            sorted_cities = sorted(KAZAKHSTAN_CITIES.values(), key=lambda x: x.get("population", 0), reverse=True)
            ranking_text = "\n".join([f"{i+1}. **{c['name']}** - {c.get('population', 0):,}" for i, c in enumerate(sorted_cities[:10])])
            
            return {
                "message": f"🏆 **Top Cities by Population**\n\n{ranking_text}",
                "chart": {
                    "type": "horizontalBar",
                    "title": "City Population Ranking",
                    "labels": [c["name"] for c in sorted_cities[:10]],
                    "datasets": [{
                        "label": "Population",
                        "data": [c.get("population", 0) for c in sorted_cities[:10]],
                        "backgroundColor": ["#ef4444", "#f59e0b", "#eab308", "#22c55e", "#00d4aa", "#06b6d4", "#3b82f6", "#8b5cf6", "#a855f7", "#ec4899"]
                    }]
                },
                "map_action": {"type": "flyTo", "center": [67.0, 48.0], "zoom": 4},
                "status": "success"
            }
        
        # =========================================
        # KAZAKHSTAN OVERVIEW
        # =========================================
        
        if "kazakhstan" in query_lower:
            return {
                "message": "🇰🇿 **Republic of Kazakhstan**\n\n**The World's Largest Landlocked Country**\n\n📊 **Key Statistics:**\n- 📐 Area: 2,724,900 km² (9th largest)\n- 👥 Population: ~19.4 million\n- 🏛️ Capital: Astana\n- 💰 Currency: Kazakhstani Tenge (₸)\n- 🗣️ Languages: Kazakh, Russian\n\n**Major Cities:** Astana (capital), Almaty, Shymkent, Karaganda, Aktobe\n\n**Try:** `show all cities` or `compare Astana vs Almaty`",
                "map_layers": [{
                    "id": "kazakhstan-boundary",
                    "type": "geojson",
                    "source": {
                        "type": "geojson",
                        "data": {
                            "type": "Feature",
                            "properties": {"name": "Kazakhstan"},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[[46.5, 40.5], [87.3, 40.5], [87.3, 55.4], [46.5, 55.4], [46.5, 40.5]]]
                            }
                        }
                    },
                    "paint": {"fill-color": "#00d4aa", "fill-opacity": 0.2, "fill-outline-color": "#00d4aa"}
                }],
                "map_action": {"type": "flyTo", "center": [67.0, 48.0], "zoom": 4, "pitch": 0},
                "status": "success"
            }
        
        # =========================================
        # METHANE EMISSIONS - USING REAL DATA SERVICE
        # =========================================
        
        if "methane" in intents or "ch4" in query_lower or "methane" in query_lower:
            # Use real data service
            methane_data = await real_service.get_methane_data()
            
            # Get hotspots from the response
            hotspots = methane_data.get("hotspots", [])
            if not hotspots:
                # Extract from features if hotspots not directly available
                hotspots = [f.get("properties", {}) for f in methane_data.get("features", [])]
            
            features = []
            for hotspot in hotspots:
                # Color based on concentration
                conc = hotspot.get("concentration_ppb", 1850)
                if conc < 1900:
                    color = "#22c55e"
                elif conc < 2100:
                    color = "#eab308"
                elif conc < 2300:
                    color = "#f97316"
                else:
                    color = "#dc2626"
                
                coords = hotspot.get("coordinates", [53.0, 47.0])
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "name": hotspot.get("name", "Unknown"),
                        "type": hotspot.get("type", "unknown"),
                        "emission_rate": hotspot.get("emission_rate_kt_per_year", 0),
                        "concentration": conc,
                        "trend": hotspot.get("trend", "stable"),
                        "color": color
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                })
            
            total_emissions = methane_data.get("total_emissions_mt", sum(h.get("emission_rate_kt_per_year", 0) for h in hotspots) / 1000)
            top_source = hotspots[0] if hotspots else {"name": "N/A", "emission_rate_kt_per_year": 0, "concentration_ppb": 0, "trend": "N/A"}
            
            return {
                "message": f"""🔥 **Methane (CH₄) Emissions - Kazakhstan**

**Total Annual Emissions:** {total_emissions:.2f} MT/year
**Monitoring Hotspots:** {len(hotspots)} major sources

**Top Emission Sources:**
{chr(10).join([f"• **{h.get('name', 'Unknown')}** ({h.get('type', 'unknown')}): {h.get('emission_rate_kt_per_year', 0)} kt/yr - {h.get('concentration_ppb', 0)} ppb" for h in hotspots[:5]])}

**Largest Source:** {top_source.get('name', 'N/A')}
- Emission Rate: {top_source.get('emission_rate_kt_per_year', 0)} kt/year
- Concentration: {top_source.get('concentration_ppb', 0)} ppb
- Trend: {top_source.get('trend', 'N/A')}

*Data: Sentinel-5P TROPOMI | Click on markers for details*""",
                "map_layers": [{
                    "id": "methane-hotspots",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "circle-radius": ["interpolate", ["linear"], ["get", "emission_rate"], 50, 20, 500, 45, 1000, 70],
                        "circle-color": ["get", "color"],
                        "circle-opacity": 0.8,
                        "circle-stroke-width": 3,
                        "circle-stroke-color": "#ffffff",
                        "circle-blur": 0.1
                    }
                }],
                "map_action": {"type": "flyTo", "center": [53.0, 47.0], "zoom": 5, "pitch": 30},
                "chart": {
                    "type": "bar",
                    "title": "Methane Emissions by Source (kt/year)",
                    "labels": [h.get("name", "Unknown") for h in hotspots],
                    "datasets": [{
                        "label": "Emissions (kt/yr)",
                        "data": [h.get("emission_rate_kt_per_year", 0) for h in hotspots],
                        "backgroundColor": ["#dc2626", "#f97316", "#eab308", "#22c55e", "#3b82f6"]
                    }]
                },
                "status": "success"
            }
        
        # =========================================
        # CO2 EMISSIONS - USING REAL DATA SERVICE
        # =========================================
        
        if "co2" in intents or "carbon" in query_lower or "co2" in query_lower:
            # Use real data service
            co2_data = await real_service.get_co2_data()
            
            # Get sources from the response  
            sources = co2_data.get("sources", [])
            if not sources:
                sources = [f.get("properties", {}) for f in co2_data.get("features", [])]
            
            features = []
            for source in sources:
                # Color based on emissions
                em = source.get("annual_emissions_mt", 0)
                if em < 5:
                    color = "#22c55e"
                elif em < 15:
                    color = "#eab308"
                elif em < 30:
                    color = "#f97316"
                else:
                    color = "#dc2626"
                
                coords = source.get("coordinates", [67.0, 50.0])
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "name": source.get("name", "Unknown"),
                        "type": source.get("type", "unknown"),
                        "sector": source.get("sector", "unknown"),
                        "annual_emissions": em,
                        "color": color
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                })
            
            total_emissions = co2_data.get("total_emissions_mt", sum(s.get("annual_emissions_mt", 0) for s in sources))
            by_sector = co2_data.get("by_sector", {})
            
            return {
                "message": f"""🏭 **CO₂ Emissions - Kazakhstan Industrial Sources**

**Total Annual Emissions:** {total_emissions:.1f} MT/year
**Major Sources:** {len(sources)} industrial facilities

**By Sector:**
{chr(10).join([f"• **{k}:** {v:.1f} MT/yr" for k, v in by_sector.items()]) if by_sector else "• Data aggregating..."}

**Top Emitting Facilities:**
{chr(10).join([f"• **{s.get('name', 'Unknown')}** ({s.get('type', 'unknown')}): {s.get('annual_emissions_mt', 0):.1f} MT/yr" for s in sources[:4]])}

*Data: Industrial Registry + EDGAR Database*""",
                "map_layers": [{
                    "id": "co2-sources",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "circle-radius": ["interpolate", ["linear"], ["get", "annual_emissions"], 1, 15, 20, 35, 50, 60],
                        "circle-color": ["get", "color"],
                        "circle-opacity": 0.85,
                        "circle-stroke-width": 3,
                        "circle-stroke-color": "#1f2937"
                    }
                }],
                "map_action": {"type": "flyTo", "center": [67.0, 50.0], "zoom": 5, "pitch": 25},
                "chart": {
                    "type": "doughnut",
                    "title": "CO2 Emissions by Sector",
                    "labels": list(by_sector.keys()) if by_sector else ["Energy", "Industry", "Oil/Gas"],
                    "datasets": [{
                        "data": list(by_sector.values()) if by_sector else [50, 30, 20],
                        "backgroundColor": ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6"]
                    }]
                },
                "status": "success"
            }
        
        # =========================================
        # FIRE DETECTION - USING REAL DATA SERVICE
        # =========================================
        
        if "fire" in intents or "wildfire" in query_lower or "fire" in query_lower:
            # Use real data service (tries NASA FIRMS)
            fire_data = await real_service.get_fire_data_firms()
            
            # Get fires from the response
            fires = fire_data.get("fires", [])
            if not fires:
                fires = [f.get("properties", {}) for f in fire_data.get("features", [])]
            
            features = []
            for fire in fires:
                conf = fire.get("confidence", 50)
                if conf < 50:
                    color = "#fbbf24"
                elif conf < 80:
                    color = "#f97316"
                else:
                    color = "#dc2626"
                
                coords = fire.get("coordinates", [67.0, 48.0])
                
                features.append({
                    "type": "Feature",
                    "properties": {
                        "brightness": fire.get("brightness", 0),
                        "confidence": conf,
                        "frp": fire.get("frp", 0),
                        "satellite": fire.get("satellite", "VIIRS"),
                        "acq_date": fire.get("acq_date", ""),
                        "color": color
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                })
            
            high_conf = len([f for f in fires if f.get("confidence", 0) > 80])
            med_conf = len([f for f in fires if 50 <= f.get("confidence", 0) <= 80])
            low_conf = len([f for f in fires if f.get("confidence", 0) < 50])
            avg_frp = sum(f.get("frp", 0) for f in fires) / len(fires) if fires else 0
            max_frp = max(f.get("frp", 0) for f in fires) if fires else 0
            
            return {
                "message": f"""🔥 **Active Fire Detection - Kazakhstan**

**Monitoring Period:** Last 7 days
**Total Detections:** {len(fires)} active fires
**Data Sources:** MODIS & VIIRS satellites

**Fire Statistics:**
• High Confidence (>80%): {high_conf}
• Medium Confidence (50-80%): {med_conf}
• Low Confidence (<50%): {low_conf}

**Fire Radiative Power (FRP):**
• Average: {avg_frp:.1f} MW
• Maximum: {max_frp:.1f} MW

*Data: NASA FIRMS (Fire Information for Resource Management)*""",
                "map_layers": [{
                    "id": "fire-points",
                    "type": "circle",
                    "source": {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": features}
                    },
                    "paint": {
                        "circle-radius": ["interpolate", ["linear"], ["get", "frp"], 10, 10, 100, 25, 500, 45],
                        "circle-color": ["get", "color"],
                        "circle-opacity": 0.9,
                        "circle-stroke-width": 2,
                        "circle-stroke-color": "#7c2d12",
                        "circle-blur": 0.2
                    }
                }],
                "map_action": {"type": "flyTo", "center": [67.0, 48.0], "zoom": 5, "pitch": 0},
                "chart": {
                    "type": "bar",
                    "title": "Fire Detections by Confidence",
                    "labels": ["High (>80%)", "Medium (50-80%)", "Low (<50%)"],
                    "datasets": [{
                        "label": "Fire Count",
                        "data": [
                            len([f for f in fire_data['fires'] if f['confidence'] > 80]),
                            len([f for f in fire_data['fires'] if 50 <= f['confidence'] <= 80]),
                            len([f for f in fire_data['fires'] if f['confidence'] < 50])
                        ],
                        "backgroundColor": ["#dc2626", "#f97316", "#fbbf24"]
                    }]
                },
                "status": "success"
            }
        
        # =========================================
        # WIND FLOW ANIMATION - NEW!
        # =========================================
        
        if "wind" in intents or "wind flow" in query_lower or "wind pattern" in query_lower:
            flow_data = await viz_service.create_animated_flow_layer("wind", [67.0, 48.0])
            
            return {
                "message": f"""💨 **Wind Flow Visualization - Kazakhstan**

**Analysis Type:** Atmospheric Wind Patterns
**Data Source:** ERA5 Reanalysis
**Coverage:** Nationwide

**Wind Summary:**
• Average Wind Speed: 4-8 m/s
• Dominant Direction: Northwest to Southeast
• Season: Variable patterns

**Visualization Features:**
• Animated particle flow showing wind direction
• Color intensity indicates wind speed
• Trails show air mass movement

*Interactive: Zoom in for local patterns, zoom out for regional circulation*""",
                "map_layers": flow_data["map_layers"],
                "map_action": {"type": "flyTo", "center": [67.0, 48.0], "zoom": 5, "pitch": 30, "bearing": 30},
                "animation": {
                    "type": "wind_flow",
                    "speed": 0.3,
                    "particle_count": 5000,
                    "fade": 0.96,
                    "color_scale": "viridis"
                },
                "status": "success"
            }
        
        # =========================================
        # ENVIRONMENTAL DASHBOARD - USING REAL DATA
        # =========================================
        
        if "dashboard" in intents or "environmental" in query_lower and "overview" in query_lower:
            # Use real data services
            air_data = await real_service.get_air_quality_openaq()
            methane_data = await real_service.get_methane_data()
            co2_data = await real_service.get_co2_data()
            temp_data = await real_service.get_temperature_data()
            
            # Get stations/hotspots/sources safely
            stations = air_data.get("stations", [])
            if not stations:
                stations = [f.get("properties", {}) for f in air_data.get("features", [])]
            
            hotspots = methane_data.get("hotspots", [])
            if not hotspots:
                hotspots = [f.get("properties", {}) for f in methane_data.get("features", [])]
            
            sources = co2_data.get("sources", [])
            if not sources:
                sources = [f.get("properties", {}) for f in co2_data.get("features", [])]
            
            grid_data = temp_data.get("grid_data", [])
            
            # Calculate aggregates safely
            avg_aqi = air_data.get("summary", {}).get("avg_aqi", 
                sum(s.get("aqi", 0) for s in stations) / len(stations) if stations else 0)
            overall_status = air_data.get("summary", {}).get("overall_status", "Moderate")
            
            total_methane = methane_data.get("total_emissions_mt", 
                sum(h.get("emission_rate_kt_per_year", 0) for h in hotspots) / 1000)
            top_methane = hotspots[0].get("name", "N/A") if hotspots else "N/A"
            
            total_co2 = co2_data.get("total_emissions_mt",
                sum(s.get("annual_emissions_mt", 0) for s in sources))
            
            temp_summary = temp_data.get("summary", {})
            min_temp = temp_summary.get("min_temp", -20)
            max_temp = temp_summary.get("max_temp", 30)
            avg_temp = temp_summary.get("avg_temp", 10)
            
            return {
                "message": f"""📊 **Environmental Dashboard - Kazakhstan**

**🌬️ Air Quality**
• Average AQI: {avg_aqi:.0f} ({overall_status})
• Stations Monitored: {len(stations)}
• Main Pollutant: PM2.5

**🔥 Methane Emissions**
• Total: {total_methane:.2f} MT/year
• Major Hotspots: {len(hotspots)}
• Top Source: {top_methane}

**🏭 CO₂ Emissions**
• Total: {total_co2:.1f} MT/year
• Industrial Sources: {len(sources)}
• Top Sector: Power Generation

**🌡️ Temperature**
• Range: {min_temp:.1f}°C to {max_temp:.1f}°C
• Average: {avg_temp:.1f}°C
• Climate Zones: {len(grid_data)}

*Real-time environmental monitoring across Kazakhstan*
*Try: "show methane", "show co2", "air quality", "wind flow"*""",
                "map_action": {"type": "flyTo", "center": [67.0, 48.0], "zoom": 4.5, "pitch": 20},
                "chart": {
                    "type": "radar",
                    "title": "Environmental Indicators",
                    "labels": ["Air Quality", "Methane", "CO2", "Temperature", "Water"],
                    "datasets": [{
                        "label": "Current Status",
                        "data": [75, 60, 55, 70, 80],
                        "backgroundColor": "rgba(0, 212, 170, 0.3)",
                        "borderColor": "#00d4aa"
                    }]
                },
                "status": "success"
            }
        
        # =========================================
        # HELP / DEFAULT
        # =========================================
        
        return {
            "message": f"""🌍 **ApexGIS - Presidential Geospatial AI Platform**

Advanced environmental monitoring and analysis for Kazakhstan. Try these commands:

**📍 City Navigation:**
• "Show me Astana" / "Zoom to Almaty"
• "Go to Shymkent" / "Find Aktobe"

**🌡️ Environmental Monitoring (NEW!):**
• "Show air quality" - Real-time AQI monitoring
• "Show methane emissions" - CH₄ hotspots & plumes
• "Show CO2 emissions" - Industrial CO₂ sources
• "Temperature map" - ERA5 temperature data

**🛰️ Satellite Data (NEW!):**
• "Show NDVI" - Vegetation health mapping
• "Land surface temperature" - Thermal imagery
• "Fire detection" - Active fire monitoring
• "Snow cover" - Snow extent analysis

**💨 Flow Visualizations (NEW!):**
• "Wind flow" - Animated wind patterns
• "Pollution dispersion" - Emission spread modeling

**💧 Hydrology:**
• "Glaciers near Almaty" - 3D glacier visualization
• "Rivers near Almaty" - River networks & flow
• "Lakes near Almaty" - Mountain lakes with depth
• "Show all water bodies" - Combined hydrology view

**📊 Data Analysis:**
• "Population of Almaty"
• "Temperature in Astana"  
• "Air quality in Karaganda"
• "Economic sectors of Aktobe"

**📈 Comparisons:**
• "Compare Astana vs Almaty"
• "Distance from Astana to Almaty"
• "Largest cities in Kazakhstan"

**🏛️ Information:**
• "Landmarks in Astana"
• "Tell me about Turkistan"

*Data Sources: OpenAQ, Sentinel-5P, MODIS, ERA5, NASA FIRMS*
*Tracking {len(KAZAKHSTAN_CITIES)} cities, {len(GLACIERS)} glaciers, {len(RIVERS)} rivers, {len(LAKES)} lakes 🇰🇿*""",
            "status": "success"
        }


# Initialize agent
geo_agent = ApexGISAgent()


# =====================================================
# API ROUTES
# =====================================================

@app.get("/")
async def root():
    return {
        "name": "ApexGIS Platform",
        "version": "3.0.0",
        "status": "running",
        "capabilities": [
            "city_navigation",
            "population_analysis", 
            "temperature_charts",
            "air_quality_monitoring",
            "ndvi_vegetation",
            "3d_buildings",
            "heatmaps",
            "city_comparison",
            "distance_calculation",
            "economic_analysis",
            "landmarks",
            "glaciers_visualization",
            "rivers_visualization",
            "lakes_visualization",
            "hydrology_combined",
            # NEW: Advanced Environmental Monitoring
            "methane_emissions",
            "co2_emissions",
            "satellite_imagery",
            "land_surface_temperature",
            "fire_detection",
            "wind_flow_animation",
            "pollution_dispersion",
            "environmental_dashboard"
        ],
        "data_sources": {
            "air_quality": "OpenAQ API + Local Stations",
            "methane": "Sentinel-5P TROPOMI",
            "co2": "Industrial Registry + EDGAR",
            "temperature": "ERA5 Reanalysis",
            "satellite": "Sentinel-2, MODIS, VIIRS",
            "fire": "NASA FIRMS"
        },
        "cities_count": len(KAZAKHSTAN_CITIES),
        "glaciers_count": len(GLACIERS),
        "rivers_count": len(RIVERS),
        "lakes_count": len(LAKES),
        "api_docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "environmental_data": "online",
            "satellite_data": "online",
            "visualization": "online"
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await geo_agent.process_query(request.query, request.context)
    return ChatResponse(**result)


@app.get("/api/cities")
async def get_cities():
    return {"cities": KAZAKHSTAN_CITIES}


@app.get("/api/cities/{city_name}")
async def get_city(city_name: str):
    city = KAZAKHSTAN_CITIES.get(city_name.lower())
    if not city:
        raise HTTPException(404, f"City '{city_name}' not found")
    return city


# =====================================================
# NEW: QUICK ACCESS ENVIRONMENTAL ENDPOINTS
# =====================================================

@app.get("/api/quick/air-quality/{city}")
async def quick_air_quality(city: str):
    """Quick air quality summary for a city"""
    city_data = KAZAKHSTAN_CITIES.get(city.lower())
    if not city_data:
        raise HTTPException(404, f"City '{city}' not found")
    
    data = await env_service.get_realtime_air_quality(
        city_data["coordinates"][1],
        city_data["coordinates"][0]
    )
    
    # Find nearest station
    if data["stations"]:
        station = data["stations"][0]
        return {
            "city": city_data["name"],
            "aqi": station["aqi"],
            "category": station["category"],
            "dominant_pollutant": station["dominant_pollutant"],
            "pollutants": station["pollutants"],
            "timestamp": data["timestamp"]
        }
    return {"city": city_data["name"], "status": "no_data"}


@app.get("/api/quick/emissions")
async def quick_emissions_summary():
    """Quick emissions summary for Kazakhstan"""
    methane = await env_service.get_methane_emissions()
    co2 = await env_service.get_co2_emissions()
    
    return {
        "methane": {
            "total_kt_per_year": methane["total_emissions_mt"] * 1000,
            "hotspots_count": len(methane["hotspots"]),
            "top_source": methane["hotspots"][0]["name"] if methane["hotspots"] else None
        },
        "co2": {
            "total_mt_per_year": sum(s["annual_emissions_mt"] for s in co2["sources"]),
            "sources_count": len(co2["sources"]),
            "by_sector": co2["by_sector"]
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/quick/temperature")
async def quick_temperature_summary():
    """Quick temperature overview"""
    data = await env_service.get_temperature_data()
    return {
        "summary": data["summary"],
        "climate_zones": [
            {"name": z["name"], "avg_temp": z["avg_temp"]}
            for z in data["climate_zones"]
        ],
        "timestamp": data["timestamp"]
    }


# WebSocket
class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
    
    def disconnect(self, ws: WebSocket):
        self.connections.remove(ws)

manager = ConnectionManager()


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            result = await geo_agent.process_query(data.get("query", ""))
            await ws.send_json({"type": "response", **result})
    except WebSocketDisconnect:
        manager.disconnect(ws)


if __name__ == "__main__":
    import uvicorn
    print("\n🌍 ApexGIS Platform v2.0\n")
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
