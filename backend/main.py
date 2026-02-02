"""
GeoGPT Research Platform - Main Application
State-of-the-art Geospatial AI Platform
"""

import os
import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,https://frontend-alpha-pied-55.vercel.app,https://frontend-dpixdkizn-bars-projects-1465.vercel.app"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="GeoGPT Research Platform",
    description="State-of-the-art Geospatial AI Platform for Advanced Research",
    version="1.0.0",
)

# CORS configuration - allow all origins for production
origins = settings.cors_origins.split(",")
origins.extend(["*"])  # Allow all origins for API access

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., description="Natural language query for geospatial analysis")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    map_bounds: Optional[Dict[str, float]] = Field(default=None, description="Current map viewport bounds")


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    map_layers: Optional[List[Dict[str, Any]]] = None
    code: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None
    status: str = "success"


class MapLayerRequest(BaseModel):
    """Request model for adding map layers"""
    layer_type: str  # "geojson", "raster", "vector-tile", "3d-terrain"
    source: str
    style: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None


# GeoAgent Integration
class GeoGPTAgent:
    """
    GeoGPT Agent - Combines GeoAgent capabilities with custom geospatial AI
    """
    
    def __init__(self):
        self.agent = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the GeoAgent with available LLM provider"""
        try:
            # Try to import GeoAgent but don't fail if not available
            try:
                from geoagent import GeoAgent
            except ImportError:
                print("⚠️ GeoAgent not installed - running in demo mode")
                self.agent = None
                return
            
            # Determine which provider to use
            provider = None
            model = None
            
            if settings.openai_api_key:
                provider = "openai"
                model = settings.default_llm_model
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key
            elif settings.anthropic_api_key:
                provider = "anthropic"
                model = "claude-sonnet-4-5-20250929"
                os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
            elif settings.google_api_key:
                provider = "google"
                model = "gemini-2.5-flash"
                os.environ["GOOGLE_API_KEY"] = settings.google_api_key
            
            if provider:
                self.agent = GeoAgent(provider=provider, model=model)
                print(f"✅ GeoAgent initialized with {provider}/{model}")
            else:
                print("⚠️ No LLM API key configured - running in demo mode")
                
        except ImportError as e:
            print(f"⚠️ GeoAgent not available: {e}")
            self.agent = None
        except Exception as e:
            print(f"⚠️ Error initializing GeoAgent: {e}")
            self.agent = None
    
    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a natural language query"""
        
        # Demo responses for when no API key is available
        demo_responses = self._get_demo_response(query)
        if self.agent is None:
            return demo_responses
        
        try:
            # Use GeoAgent to process the query
            result = self.agent.chat(query)
            
            response = {
                "message": str(result) if hasattr(result, '__str__') else "Analysis complete",
                "code": getattr(result, 'code', None),
                "map_layers": [],
                "status": "success"
            }
            
            # Extract map data if available
            if hasattr(result, 'map') and result.map is not None:
                response["visualization"] = {
                    "type": "leafmap",
                    "data": "Map generated - view in notebook environment"
                }
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return demo_responses
    
    def _get_demo_response(self, query: str) -> Dict[str, Any]:
        """Generate demo responses for demonstration purposes"""
        
        query_lower = query.lower()
        
        # Kazakhstan-specific demo data
        if "kazakhstan" in query_lower or "astana" in query_lower or "almaty" in query_lower:
            return {
                "message": "🇰🇿 Analyzing Kazakhstan region. Displaying administrative boundaries and satellite imagery.",
                "map_layers": [
                    {
                        "id": "kazakhstan-boundary",
                        "type": "geojson",
                        "source": {
                            "type": "geojson",
                            "data": {
                                "type": "Feature",
                                "properties": {"name": "Kazakhstan", "admin": "KZ"},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [[[46.5, 40.5], [87.3, 40.5], [87.3, 55.4], [46.5, 55.4], [46.5, 40.5]]]
                                }
                            }
                        },
                        "paint": {
                            "fill-color": "#00ff88",
                            "fill-opacity": 0.2,
                            "fill-outline-color": "#00ff88"
                        }
                    }
                ],
                "code": """import leafmap
import geopandas as gpd

# Load Kazakhstan boundary
kz = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
kz = kz[kz['name'] == 'Kazakhstan']

# Create interactive map
m = leafmap.Map(center=[48.0, 67.0], zoom=4)
m.add_gdf(kz, layer_name='Kazakhstan')
m""",
                "data": {
                    "country": "Kazakhstan",
                    "capital": "Astana",
                    "area_km2": 2724900,
                    "population": 19398000
                },
                "status": "success"
            }
        
        # NDVI analysis demo
        elif "ndvi" in query_lower or "vegetation" in query_lower:
            return {
                "message": "🌿 Calculating NDVI (Normalized Difference Vegetation Index). Higher values indicate healthy vegetation.",
                "map_layers": [
                    {
                        "id": "ndvi-layer",
                        "type": "raster",
                        "source": {
                            "type": "raster",
                            "tiles": ["https://tiles.planet.com/basemaps/v1/planet-tiles/global_monthly_2024_01_mosaic/gmap/{z}/{x}/{y}.png"],
                            "tileSize": 256
                        }
                    }
                ],
                "code": """import leafmap
import xarray as xr
from pystac_client import Client

# Search for Sentinel-2 imagery
catalog = Client.open("https://earth-search.aws.element84.com/v1")
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[66, 47, 68, 49],
    datetime="2024-07-01/2024-07-31",
    max_items=1
)

# Calculate NDVI
# NDVI = (NIR - RED) / (NIR + RED)
items = list(search.items())
nir = xr.open_dataarray(items[0].assets["nir"].href)
red = xr.open_dataarray(items[0].assets["red"].href)
ndvi = (nir - red) / (nir + red)

# Visualize
m = leafmap.Map()
m.add_raster(ndvi, colormap="RdYlGn", layer_name="NDVI")
m""",
                "visualization": {
                    "type": "ndvi",
                    "colormap": "RdYlGn",
                    "range": [-1, 1]
                },
                "status": "success"
            }
        
        # Flood detection demo
        elif "flood" in query_lower or "water" in query_lower:
            return {
                "message": "🌊 Analyzing water bodies and potential flood areas using SAR imagery analysis.",
                "map_layers": [
                    {
                        "id": "water-layer",
                        "type": "fill",
                        "source": {
                            "type": "geojson",
                            "data": {
                                "type": "FeatureCollection",
                                "features": []
                            }
                        },
                        "paint": {
                            "fill-color": "#0066ff",
                            "fill-opacity": 0.6
                        }
                    }
                ],
                "code": """import leafmap
from pystac_client import Client

# Search for Sentinel-1 SAR data for flood mapping
catalog = Client.open("https://earth-search.aws.element84.com/v1")
search = catalog.search(
    collections=["sentinel-1-grd"],
    bbox=[66, 47, 68, 49],
    datetime="2024-01-01/2024-12-31"
)

# Apply water detection algorithm
# Water appears dark in SAR VV polarization
m = leafmap.Map()
m.add_stac_layer(search, assets=["vv"], name="SAR VV")
m""",
                "status": "success"
            }
        
        # Land use classification demo
        elif "land use" in query_lower or "classification" in query_lower:
            return {
                "message": "🏙️ Performing land use classification using deep learning models.",
                "map_layers": [],
                "code": """import leafmap
from samgeo import SamGeo

# Initialize Segment Anything Model for geospatial
sam = SamGeo(
    model_type="vit_h",
    checkpoint="sam_vit_h_4b8939.pth"
)

# Perform automatic segmentation
sam.generate(
    source="satellite_image.tif",
    output="segmented.tif",
    batch=True
)

# Visualize results
m = leafmap.Map()
m.add_raster("segmented.tif", layer_name="Land Use")
m""",
                "status": "success"
            }
        
        # Default response
        else:
            return {
                "message": f"🌍 Processing your query: '{query}'. I can help with:\n\n• Satellite imagery analysis (NDVI, land cover)\n• Flood and water body detection\n• Land use classification\n• Terrain analysis\n• Geographic data visualization\n\nTry asking about a specific region like Kazakhstan!",
                "map_layers": [],
                "code": """# Example: Create an interactive map
import leafmap

m = leafmap.Map(center=[48.0, 67.0], zoom=4)
m.add_basemap("SATELLITE")
m""",
                "status": "success"
            }


# Initialize the agent
geo_agent = GeoGPTAgent()


# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "GeoGPT Research Platform",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "websocket": "/ws/chat",
            "health": "/health",
            "layers": "/api/layers"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_available": geo_agent.agent is not None
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat request"""
    try:
        result = await geo_agent.process_query(
            query=request.query,
            context=request.context
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/layers/basemaps")
async def get_basemaps():
    """Get available basemap layers"""
    return {
        "basemaps": [
            {
                "id": "dark",
                "name": "Dark Mode",
                "url": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                "type": "style"
            },
            {
                "id": "satellite",
                "name": "Satellite",
                "url": "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg",
                "type": "raster",
                "attribution": "© MapTiler © OpenStreetMap contributors"
            },
            {
                "id": "terrain",
                "name": "Terrain",
                "url": "https://api.maptiler.com/maps/outdoor-v2/style.json",
                "type": "style"
            },
            {
                "id": "osm",
                "name": "OpenStreetMap",
                "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "type": "raster"
            }
        ]
    }


@app.get("/api/data/kazakhstan")
async def get_kazakhstan_data():
    """Get Kazakhstan geographic data"""
    return {
        "center": [67.0, 48.0],
        "zoom": 4,
        "bounds": [[46.5, 40.5], [87.3, 55.4]],
        "regions": [
            {"name": "Astana", "coordinates": [71.4491, 51.1801], "type": "capital"},
            {"name": "Almaty", "coordinates": [76.9458, 43.2220], "type": "city"},
            {"name": "Shymkent", "coordinates": [69.5958, 42.3417], "type": "city"},
            {"name": "Aktobe", "coordinates": [57.1722, 50.2839], "type": "city"},
            {"name": "Karaganda", "coordinates": [73.1022, 49.8047], "type": "city"},
        ]
    }


# WebSocket for real-time chat
class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("query", "")
            
            # Send processing status
            await manager.send_message({
                "type": "status",
                "message": "Processing your query...",
                "status": "processing"
            }, websocket)
            
            # Process the query
            result = await geo_agent.process_query(query, data.get("context"))
            
            # Send result
            await manager.send_message({
                "type": "response",
                **result
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🌍 GeoGPT Research Platform                                 ║
    ║   State-of-the-Art Geospatial AI                              ║
    ║                                                               ║
    ║   Server starting at http://localhost:8000                    ║
    ║   API Docs: http://localhost:8000/docs                        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
