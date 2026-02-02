import { useState, useCallback, useRef, useEffect } from 'react'
import Map, { NavigationControl, ScaleControl, GeolocateControl, Source, Layer } from 'react-map-gl/maplibre'
import type { MapRef, MapLayerMouseEvent } from 'react-map-gl/maplibre'
import { useAppStore } from '../store'
import { 
  Layers, 
  Globe2, 
  Mountain, 
  Satellite,
  Map as MapIcon,
  ZoomIn,
  ZoomOut,
  Compass,
  Maximize2
} from 'lucide-react'

// Dark mode map style
const DARK_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'

// Basemap options
const BASEMAPS = [
  { id: 'dark', name: 'Dark', icon: MapIcon, style: DARK_STYLE },
  { 
    id: 'satellite', 
    name: 'Satellite', 
    icon: Satellite, 
    style: {
      version: 8,
      sources: {
        satellite: {
          type: 'raster',
          tiles: [
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
          ],
          tileSize: 256,
          attribution: '© Esri'
        }
      },
      layers: [
        {
          id: 'satellite-layer',
          type: 'raster',
          source: 'satellite',
          minzoom: 0,
          maxzoom: 22
        }
      ]
    }
  },
]

export default function MapView() {
  const mapRef = useRef<MapRef>(null)
  const { viewState, setViewState, layers, selectedBasemap, setBasemap, is3DEnabled, toggle3D } = useAppStore()
  const [cursorPosition, setCursorPosition] = useState<{ lng: number; lat: number } | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Get current basemap style
  const currentBasemap = BASEMAPS.find(b => b.id === selectedBasemap) || BASEMAPS[0]

  // Handle map movement
  const onMove = useCallback((evt: { viewState: typeof viewState }) => {
    setViewState(evt.viewState)
  }, [setViewState])

  // Handle mouse move for coordinates display
  const onMouseMove = useCallback((evt: MapLayerMouseEvent) => {
    setCursorPosition({ lng: evt.lngLat.lng, lat: evt.lngLat.lat })
  }, [])

  // Zoom controls
  const zoomIn = () => {
    setViewState({ zoom: viewState.zoom + 1 })
  }

  const zoomOut = () => {
    setViewState({ zoom: Math.max(0, viewState.zoom - 1) })
  }

  const resetBearing = () => {
    setViewState({ bearing: 0, pitch: 0 })
  }

  // Fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  // Fly to Kazakhstan
  const flyToKazakhstan = () => {
    mapRef.current?.flyTo({
      center: [67.0, 48.0],
      zoom: 4,
      pitch: is3DEnabled ? 45 : 0,
      duration: 2000
    })
  }

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  return (
    <div className="relative w-full h-full">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={onMove}
        onMouseMove={onMouseMove}
        mapStyle={currentBasemap.style}
        attributionControl={false}
        reuseMaps
      >
        {/* Navigation Controls */}
        <NavigationControl position="top-right" showCompass showZoom={false} />
        <ScaleControl position="bottom-right" maxWidth={200} unit="metric" />
        <GeolocateControl position="top-right" />

        {/* Render dynamic layers from store */}
        {layers.filter(l => l.visible).map((layer) => (
          <Source
            key={layer.id}
            id={layer.id}
            type={layer.source?.type || 'geojson'}
            data={layer.source?.data}
          >
            {layer.type === 'geojson' && (
              <Layer
                id={`${layer.id}-fill`}
                type="fill"
                paint={{
                  'fill-color': layer.paint?.['fill-color'] || '#00d4aa',
                  'fill-opacity': (layer.paint?.['fill-opacity'] || 0.3) * layer.opacity,
                }}
              />
            )}
            {layer.type === 'geojson' && (
              <Layer
                id={`${layer.id}-line`}
                type="line"
                paint={{
                  'line-color': layer.paint?.['fill-outline-color'] || layer.paint?.['fill-color'] || '#00d4aa',
                  'line-width': 2,
                  'line-opacity': layer.opacity,
                }}
              />
            )}
          </Source>
        ))}
      </Map>

      {/* Custom Controls Panel - Top Left */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
        {/* Logo/Title */}
        <div className="glass-panel px-4 py-2 flex items-center gap-2">
          <Globe2 className="w-5 h-5 text-accent-primary" />
          <span className="font-semibold text-sm">GeoGPT</span>
        </div>
      </div>

      {/* Zoom Controls - Right Side */}
      <div className="absolute top-24 right-4 z-10 flex flex-col gap-1">
        <button
          onClick={zoomIn}
          className="glass-panel p-2 hover:bg-dark-600 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={zoomOut}
          className="glass-panel p-2 hover:bg-dark-600 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={resetBearing}
          className="glass-panel p-2 hover:bg-dark-600 transition-colors"
          title="Reset Bearing"
        >
          <Compass className="w-4 h-4" />
        </button>
        <button
          onClick={toggleFullscreen}
          className="glass-panel p-2 hover:bg-dark-600 transition-colors"
          title="Fullscreen"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Basemap Selector - Bottom Left */}
      <div className="absolute bottom-8 left-4 z-10">
        <div className="glass-panel p-2 flex gap-1">
          {BASEMAPS.map((basemap) => {
            const Icon = basemap.icon
            return (
              <button
                key={basemap.id}
                onClick={() => setBasemap(basemap.id)}
                className={`p-2 rounded-lg transition-all ${
                  selectedBasemap === basemap.id
                    ? 'bg-accent-primary/20 text-accent-primary'
                    : 'hover:bg-dark-600'
                }`}
                title={basemap.name}
              >
                <Icon className="w-4 h-4" />
              </button>
            )
          })}
          <div className="w-px bg-dark-500 mx-1" />
          <button
            onClick={toggle3D}
            className={`p-2 rounded-lg transition-all ${
              is3DEnabled
                ? 'bg-accent-primary/20 text-accent-primary'
                : 'hover:bg-dark-600'
            }`}
            title="Toggle 3D"
          >
            <Mountain className="w-4 h-4" />
          </button>
          <button
            onClick={flyToKazakhstan}
            className="p-2 rounded-lg hover:bg-dark-600 transition-all"
            title="Fly to Kazakhstan"
          >
            🇰🇿
          </button>
        </div>
      </div>

      {/* Coordinates Display - Bottom Right */}
      {cursorPosition && (
        <div className="absolute bottom-8 right-4 z-10">
          <div className="glass-panel px-3 py-1.5 text-xs font-mono text-dark-100">
            {cursorPosition.lat.toFixed(4)}°, {cursorPosition.lng.toFixed(4)}° | Zoom: {viewState.zoom.toFixed(1)}
          </div>
        </div>
      )}

      {/* Layer indicator */}
      {layers.length > 0 && (
        <div className="absolute top-4 right-16 z-10">
          <div className="glass-panel px-3 py-1.5 flex items-center gap-2 text-xs">
            <Layers className="w-3 h-3 text-accent-primary" />
            <span>{layers.filter(l => l.visible).length} layers active</span>
          </div>
        </div>
      )}
    </div>
  )
}
