import { useState, useCallback, useRef, useEffect } from 'react'
import Map, { 
  NavigationControl, 
  ScaleControl, 
  Source, 
  Layer,
  Popup,
  type MapRef,
  type MapLayerMouseEvent 
} from 'react-map-gl/maplibre'
import { useAppStore } from '../store'
import { 
  Layers, 
  Globe2, 
  Mountain, 
  Satellite,
  Map as MapIcon,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  X,
  Snowflake,
  TrendingDown,
  Ruler,
  Info,
  AlertTriangle,
  Droplets
} from 'lucide-react'
import type { StyleSpecification } from 'maplibre-gl'

// Feature popup data interface
interface PopupData {
  type: 'glacier' | 'river' | 'lake' | 'city' | 'generic'
  coordinates: [number, number]
  properties: Record<string, any>
}

// Dark mode map style
const DARK_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'

// Basemap options
const BASEMAPS: Array<{
  id: string
  name: string
  icon: typeof MapIcon
  style: string | StyleSpecification
}> = [
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
    } as StyleSpecification
  },
]

export default function MapView() {
  const mapRef = useRef<MapRef>(null)
  const { viewState, setViewState, layers, selectedBasemap, setBasemap, is3DEnabled, toggle3D } = useAppStore()
  const [cursorPosition, setCursorPosition] = useState<{ lng: number; lat: number } | null>(null)
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null)
  const [popupData, setPopupData] = useState<PopupData | null>(null)

  // Get current basemap style
  const currentBasemap = BASEMAPS.find(b => b.id === selectedBasemap) || BASEMAPS[0]

  // Handle map movement
  const onMove = useCallback((evt: { viewState: typeof viewState }) => {
    setViewState(evt.viewState)
  }, [setViewState])

  // Handle mouse move for coordinates display
  const onMouseMove = useCallback((evt: MapLayerMouseEvent) => {
    setCursorPosition({ lng: evt.lngLat.lng, lat: evt.lngLat.lat })
    
    // Check for hovered features
    if (evt.features && evt.features.length > 0) {
      const feature = evt.features[0]
      if (feature.properties?.name) {
        setHoveredFeature(feature.properties.name)
      }
    } else {
      setHoveredFeature(null)
    }
  }, [])

  // Handle click on map features
  const onClick = useCallback((evt: MapLayerMouseEvent) => {
    if (evt.features && evt.features.length > 0) {
      const feature = evt.features[0]
      const props = feature.properties || {}
      
      // Determine feature type
      let featureType: PopupData['type'] = 'generic'
      if (props.type === 'glacier' || props.glacier_type) {
        featureType = 'glacier'
      } else if (props.type === 'river' || props.discharge) {
        featureType = 'river'
      } else if (props.type === 'lake' || props.lake_type) {
        featureType = 'lake'
      } else if (props.population) {
        featureType = 'city'
      }
      
      setPopupData({
        type: featureType,
        coordinates: [evt.lngLat.lng, evt.lngLat.lat],
        properties: props
      })
    }
  }, [])

  // Close popup
  const closePopup = useCallback(() => {
    setPopupData(null)
  }, [])

  // Handle map actions from API responses
  useEffect(() => {
    const handleMapAction = (action: any) => {
      if (!mapRef.current || !action) return
      
      const map = mapRef.current.getMap()
      
      if (action.type === 'flyTo') {
        map.flyTo({
          center: action.center,
          zoom: action.zoom || 12,
          pitch: action.pitch || 0,
          bearing: action.bearing || 0,
          duration: action.duration || 2000
        })
      } else if (action.type === 'fitBounds' && action.bounds) {
        map.fitBounds(action.bounds, {
          padding: 50,
          duration: 2000
        })
      }
    }
    
    // Subscribe to map action changes
    const unsubscribe = useAppStore.subscribe(
      (state: any) => state.pendingMapAction,
      (action: any) => {
        if (action) {
          handleMapAction(action)
          // Clear the pending action
          useAppStore.getState().clearMapAction()
        }
      }
    )
    
    return () => unsubscribe()
  }, [])

  // Zoom controls
  const zoomIn = () => setViewState({ zoom: viewState.zoom + 1 })
  const zoomOut = () => setViewState({ zoom: Math.max(0, viewState.zoom - 1) })
  const resetView = () => setViewState({ bearing: 0, pitch: 0 })

  // Fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
    } else {
      document.exitFullscreen()
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

  // Render Glacier Popup Content
  const renderGlacierPopup = (props: Record<string, any>) => {
    const statusColor = props.status === 'critical' ? 'text-red-500' : 
                       props.status === 'retreating' ? 'text-yellow-500' : 'text-green-500'
    const statusBg = props.status === 'critical' ? 'bg-red-500/20' : 
                    props.status === 'retreating' ? 'bg-yellow-500/20' : 'bg-green-500/20'
    
    return (
      <div className="min-w-[320px] max-w-[400px]">
        {/* Header */}
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-dark-500">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Snowflake className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="font-bold text-white text-lg">{props.name}</h3>
              <p className="text-xs text-dark-200">{props.name_kz || 'Glacier'}</p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBg} ${statusColor}`}>
            {props.status?.toUpperCase() || 'UNKNOWN'}
          </span>
        </div>

        {/* Description */}
        {props.description && (
          <p className="text-sm text-dark-100 mb-3 leading-relaxed">{props.description}</p>
        )}

        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-dark-700 rounded-lg p-2">
            <div className="flex items-center gap-1 text-xs text-dark-300 mb-1">
              <Ruler className="w-3 h-3" /> Area
            </div>
            <div className="text-lg font-bold text-white">{props.area_km2} km²</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-2">
            <div className="flex items-center gap-1 text-xs text-dark-300 mb-1">
              <Mountain className="w-3 h-3" /> Length
            </div>
            <div className="text-lg font-bold text-white">{props.length_km} km</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-2">
            <div className="flex items-center gap-1 text-xs text-dark-300 mb-1">
              <Snowflake className="w-3 h-3" /> Ice Thickness
            </div>
            <div className="text-lg font-bold text-white">{props.ice_thickness || 'N/A'} m</div>
          </div>
          <div className="bg-dark-700 rounded-lg p-2">
            <div className="flex items-center gap-1 text-xs text-dark-300 mb-1">
              <TrendingDown className="w-3 h-3" /> Retreat Rate
            </div>
            <div className="text-lg font-bold text-red-400">{props.retreat_rate || 0} m/yr</div>
          </div>
        </div>

        {/* Elevation Range */}
        <div className="bg-dark-700 rounded-lg p-3 mb-3">
          <div className="flex items-center gap-1 text-xs text-dark-300 mb-2">
            <Mountain className="w-3 h-3" /> Elevation Range
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-200">Min: {props.elevation_min || 'N/A'}m</span>
            <div className="flex-1 mx-3 h-2 bg-dark-600 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400" 
                style={{ width: '100%' }}
              />
            </div>
            <span className="text-sm text-dark-200">Max: {props.elevation_max || 'N/A'}m</span>
          </div>
        </div>

        {/* Glacier Type */}
        <div className="flex items-center gap-2 text-sm">
          <Info className="w-4 h-4 text-dark-300" />
          <span className="text-dark-200">Type:</span>
          <span className="text-white font-medium">{props.glacier_type || 'Valley Glacier'}</span>
        </div>

        {/* Warning if critical */}
        {props.status === 'critical' && (
          <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="text-xs text-red-400">This glacier is at critical risk due to climate change</span>
          </div>
        )}

        {/* Retreat Trend Mini Chart */}
        <div className="mt-3 pt-3 border-t border-dark-500">
          <div className="text-xs text-dark-300 mb-2 flex items-center gap-1">
            <TrendingDown className="w-3 h-3" /> Retreat Trend (Simulated)
          </div>
          <div className="flex items-end gap-1 h-12">
            {[100, 95, 88, 82, 75, 70, 65, 58, 52, 48].map((val, i) => (
              <div 
                key={i} 
                className="flex-1 bg-gradient-to-t from-red-500 to-blue-500 rounded-t"
                style={{ height: `${val}%` }}
                title={`${2015 + i}: ${val}%`}
              />
            ))}
          </div>
          <div className="flex justify-between text-[10px] text-dark-400 mt-1">
            <span>2015</span>
            <span>2024</span>
          </div>
        </div>
      </div>
    )
  }

  // Render River Popup Content
  const renderRiverPopup = (props: Record<string, any>) => (
    <div className="min-w-[280px]">
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-dark-500">
        <div className="p-2 bg-cyan-500/20 rounded-lg">
          <Droplets className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h3 className="font-bold text-white">{props.name}</h3>
          <p className="text-xs text-dark-200">{props.name_kz || 'River'}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-2">
        <div className="bg-dark-700 rounded p-2">
          <div className="text-xs text-dark-300">Length</div>
          <div className="font-bold text-white">{props.length_km} km</div>
        </div>
        <div className="bg-dark-700 rounded p-2">
          <div className="text-xs text-dark-300">Discharge</div>
          <div className="font-bold text-cyan-400">{props.avg_discharge} m³/s</div>
        </div>
      </div>
      {props.uses && (
        <div className="text-xs text-dark-200 mt-2">
          <strong>Uses:</strong> {props.uses}
        </div>
      )}
      {props.glacier_fed && (
        <div className="mt-2 text-xs text-blue-400 flex items-center gap-1">
          <Snowflake className="w-3 h-3" /> Glacier-fed river
        </div>
      )}
    </div>
  )

  // Render Lake Popup Content
  const renderLakePopup = (props: Record<string, any>) => (
    <div className="min-w-[280px]">
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-dark-500">
        <div className="p-2 bg-blue-600/20 rounded-lg">
          <Droplets className="w-5 h-5 text-blue-500" />
        </div>
        <div>
          <h3 className="font-bold text-white">{props.name}</h3>
          <p className="text-xs text-dark-200">{props.name_kz || 'Lake'}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-2">
        <div className="bg-dark-700 rounded p-2">
          <div className="text-xs text-dark-300">Area</div>
          <div className="font-bold text-white">{props.surface_area_km2} km²</div>
        </div>
        <div className="bg-dark-700 rounded p-2">
          <div className="text-xs text-dark-300">Max Depth</div>
          <div className="font-bold text-blue-400">{props.max_depth_m} m</div>
        </div>
        <div className="bg-dark-700 rounded p-2">
          <div className="text-xs text-dark-300">Elevation</div>
          <div className="font-bold text-white">{props.elevation} m</div>
        </div>
        <div className="bg-dark-700 rounded p-2">
          <div className="text-xs text-dark-300">Type</div>
          <div className="font-bold text-white">{props.lake_type || 'Natural'}</div>
        </div>
      </div>
      {props.unique_feature && (
        <div className="text-xs text-dark-100 mt-2 p-2 bg-dark-700 rounded">
          ✨ {props.unique_feature}
        </div>
      )}
      {props.protected && (
        <div className="mt-2 text-xs text-green-400 flex items-center gap-1">
          🛡️ Protected area
        </div>
      )}
    </div>
  )

  // Render popup based on type
  const renderPopupContent = (data: PopupData) => {
    switch (data.type) {
      case 'glacier':
        return renderGlacierPopup(data.properties)
      case 'river':
        return renderRiverPopup(data.properties)
      case 'lake':
        return renderLakePopup(data.properties)
      default:
        return (
          <div className="min-w-[200px]">
            <h3 className="font-bold text-white mb-2">{data.properties.name || 'Feature'}</h3>
            <pre className="text-xs text-dark-200 overflow-auto max-h-40">
              {JSON.stringify(data.properties, null, 2)}
            </pre>
          </div>
        )
    }
  }

  // Render layer based on type
  const renderLayer = (layer: any) => {
    if (!layer.visible) return null
    
    const sourceData = layer.source?.data || layer.source

    // Handle different layer types
    switch (layer.type) {
      case 'fill-extrusion':
        // 3D Buildings
        return (
          <Source
            key={layer.id}
            id={layer.id}
            type="geojson"
            data={sourceData}
          >
            <Layer
              id={`${layer.id}-extrusion`}
              type="fill-extrusion"
              paint={{
                'fill-extrusion-color': layer.paint?.['fill-extrusion-color'] || '#00d4aa',
                'fill-extrusion-height': layer.paint?.['fill-extrusion-height'] || ['get', 'height'],
                'fill-extrusion-base': layer.paint?.['fill-extrusion-base'] || 0,
                'fill-extrusion-opacity': layer.paint?.['fill-extrusion-opacity'] || 0.8
              }}
            />
          </Source>
        )

      case 'heatmap':
        // Heatmap layer
        return (
          <Source
            key={layer.id}
            id={layer.id}
            type="geojson"
            data={sourceData}
          >
            <Layer
              id={`${layer.id}-heat`}
              type="heatmap"
              paint={{
                'heatmap-weight': layer.paint?.['heatmap-weight'] || 1,
                'heatmap-intensity': layer.paint?.['heatmap-intensity'] || 1,
                'heatmap-color': layer.paint?.['heatmap-color'] || [
                  'interpolate', ['linear'], ['heatmap-density'],
                  0, 'rgba(0,0,0,0)',
                  0.2, '#4338ca',
                  0.4, '#7c3aed',
                  0.6, '#c026d3',
                  0.8, '#e11d48',
                  1, '#fbbf24'
                ],
                'heatmap-radius': layer.paint?.['heatmap-radius'] || 20,
                'heatmap-opacity': layer.paint?.['heatmap-opacity'] || 0.8
              }}
            />
          </Source>
        )

      case 'circle':
        // Point/Circle layer
        return (
          <Source
            key={layer.id}
            id={layer.id}
            type="geojson"
            data={sourceData}
          >
            <Layer
              id={`${layer.id}-circle`}
              type="circle"
              paint={{
                'circle-radius': layer.paint?.['circle-radius'] || 8,
                'circle-color': layer.paint?.['circle-color'] || '#00d4aa',
                'circle-stroke-width': layer.paint?.['circle-stroke-width'] || 2,
                'circle-stroke-color': layer.paint?.['circle-stroke-color'] || '#ffffff',
                'circle-opacity': layer.opacity || 1
              }}
            />
            <Layer
              id={`${layer.id}-label`}
              type="symbol"
              layout={{
                'text-field': ['get', 'name'],
                'text-size': 12,
                'text-offset': [0, 1.5],
                'text-anchor': 'top'
              }}
              paint={{
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 1
              }}
            />
          </Source>
        )

      case 'line':
        // Line layer (routes)
        return (
          <Source
            key={layer.id}
            id={layer.id}
            type="geojson"
            data={sourceData}
          >
            <Layer
              id={`${layer.id}-line`}
              type="line"
              paint={{
                'line-color': layer.paint?.['line-color'] || '#00d4aa',
                'line-width': layer.paint?.['line-width'] || 3,
                'line-opacity': layer.opacity || 1,
                'line-dasharray': layer.paint?.['line-dasharray'] || [1, 0]
              }}
            />
          </Source>
        )

      case 'geojson':
      default:
        // Default polygon/fill layer
        return (
          <Source
            key={layer.id}
            id={layer.id}
            type="geojson"
            data={sourceData}
          >
            <Layer
              id={`${layer.id}-fill`}
              type="fill"
              paint={{
                'fill-color': layer.paint?.['fill-color'] || '#00d4aa',
                'fill-opacity': (layer.paint?.['fill-opacity'] || 0.3) * layer.opacity
              }}
            />
            <Layer
              id={`${layer.id}-outline`}
              type="line"
              paint={{
                'line-color': layer.paint?.['fill-outline-color'] || layer.paint?.['fill-color'] || '#00d4aa',
                'line-width': 2,
                'line-opacity': layer.opacity
              }}
            />
          </Source>
        )
    }
  }

  return (
    <div className="relative w-full h-full">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={onMove}
        onMouseMove={onMouseMove}
        onClick={onClick}
        mapStyle={currentBasemap.style}
        attributionControl={false}
        reuseMaps
        cursor={hoveredFeature ? 'pointer' : 'grab'}
        interactiveLayerIds={
          layers.flatMap((l: any) => [
            `${l.id}-fill`, 
            `${l.id}-circle`, 
            `${l.id}-extrusion`,
            `${l.id}-line`
          ])
        }
      >
        {/* Navigation Controls */}
        <NavigationControl position="top-right" showCompass showZoom={false} />
        <ScaleControl position="bottom-right" maxWidth={200} unit="metric" />

        {/* Render all layers */}
        {layers.filter((l: any) => l.visible).map(renderLayer)}

        {/* Feature Popup */}
        {popupData && (
          <Popup
            longitude={popupData.coordinates[0]}
            latitude={popupData.coordinates[1]}
            onClose={closePopup}
            closeButton={false}
            closeOnClick={false}
            anchor="bottom"
            maxWidth="450px"
            className="feature-popup"
          >
            <div className="bg-dark-800 rounded-lg p-4 shadow-2xl border border-dark-500 relative">
              {/* Close Button */}
              <button
                onClick={closePopup}
                className="absolute top-2 right-2 p-1 hover:bg-dark-600 rounded transition-colors"
              >
                <X className="w-4 h-4 text-dark-300 hover:text-white" />
              </button>
              
              {/* Popup Content */}
              {renderPopupContent(popupData)}
            </div>
          </Popup>
        )}
      </Map>

      {/* Custom Controls Panel - Top Left */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
        {/* Logo/Title */}
        <div className="glass-panel px-4 py-2 flex items-center gap-2">
          <Globe2 className="w-5 h-5 text-accent-primary" />
          <span className="font-semibold text-sm">ApexGIS v2.0</span>
        </div>
        
        {/* Hovered feature tooltip */}
        {hoveredFeature && (
          <div className="glass-panel px-3 py-2 text-sm">
            📍 {hoveredFeature}
          </div>
        )}
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
          onClick={resetView}
          className="glass-panel p-2 hover:bg-dark-600 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
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
            title="Toggle 3D View"
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
            {cursorPosition.lat.toFixed(4)}°, {cursorPosition.lng.toFixed(4)}° | 
            Zoom: {viewState.zoom.toFixed(1)} | 
            Pitch: {viewState.pitch.toFixed(0)}°
          </div>
        </div>
      )}

      {/* Layer indicator */}
      {layers.length > 0 && (
        <div className="absolute top-4 right-16 z-10">
          <div className="glass-panel px-3 py-1.5 flex items-center gap-2 text-xs">
            <Layers className="w-3 h-3 text-accent-primary" />
            <span>{layers.filter((l: any) => l.visible).length} layers</span>
          </div>
        </div>
      )}

      {/* 3D Mode Indicator */}
      {is3DEnabled && (
        <div className="absolute top-16 left-4 z-10">
          <div className="glass-panel px-3 py-1.5 text-xs text-accent-primary flex items-center gap-1">
            <Mountain className="w-3 h-3" />
            3D Mode
          </div>
        </div>
      )}
    </div>
  )
}
