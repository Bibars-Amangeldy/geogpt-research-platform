# 🌍 GeoGPT Research Platform

## State-of-the-Art Geospatial AI Platform for Kazakhstan

A cutting-edge geospatial research platform combining the world's best open-source GIS technologies with advanced AI capabilities.

### 🚀 Technologies Used

**AI & Machine Learning:**
- **GeoGPT** - Specialized geoscience language models (Llama3.1-70B-GeoGPT, Qwen2.5-72B-GeoGPT)
- **GeoAgent** - 4-agent LangGraph pipeline for geospatial analysis
- **IBM-NASA Prithvi** - Foundation models for Earth observation
- **LangChain** - AI orchestration framework

**Mapping & Visualization:**
- **MapLibre GL JS** - High-performance vector maps
- **Deck.gl** - Large-scale data visualization
- **Leafmap** - Interactive geospatial mapping
- **3D Terrain** - Realistic terrain visualization

**Data Sources:**
- NASA Earth Data
- Planetary Computer
- AWS Open Data
- STAC Catalogs
- OpenStreetMap / Overture Maps

### 📋 Requirements

- Python 3.10+
- Node.js 18+
- API Keys: OpenAI, Anthropic, or Google (at least one)

### 🛠️ Installation

```bash
# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install

# Start both servers
cd backend && python main.py  # http://localhost:8000
cd frontend && npm run dev    # http://localhost:3000
```

### 🔑 Environment Variables

Create `.env` file in the backend directory:

```env
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
```

### 🎯 Features

1. **Natural Language Queries** - Ask questions in plain language
2. **Interactive Map** - Pan, zoom, and explore geospatial data
3. **Multi-Layer Visualization** - Satellite imagery, terrain, vector data
4. **Real-time Analysis** - NDVI, flood detection, land use classification
5. **Dark Mode UI** - Professional research interface
6. **Code Transparency** - See generated Python code

### 🇰🇿 Optimized for Kazakhstan

- Pre-configured with Kazakhstan boundaries
- Access to regional satellite data
- Support for Central Asian geographic features

---

Built with ❤️ using the best open-source geospatial tools from:
- [OpenGeos](https://github.com/opengeos)
- [GeoGPT Research Project](https://github.com/GeoGPT-Research-Project)
- [IBM-NASA Geospatial](https://huggingface.co/ibm-nasa-geospatial)
