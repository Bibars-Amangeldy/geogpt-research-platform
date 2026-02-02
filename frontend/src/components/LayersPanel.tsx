import { useAppStore } from '../store'
import { 
  Eye, 
  EyeOff, 
  Trash2, 
  Layers,
  ChevronDown,
  ChevronRight,
  Circle
} from 'lucide-react'
import { useState } from 'react'

export default function LayersPanel() {
  const { layers, toggleLayerVisibility, removeLayer, setLayerOpacity } = useAppStore()
  const [expandedLayers, setExpandedLayers] = useState<Set<string>>(new Set())

  const toggleExpand = (layerId: string) => {
    const newExpanded = new Set(expandedLayers)
    if (newExpanded.has(layerId)) {
      newExpanded.delete(layerId)
    } else {
      newExpanded.add(layerId)
    }
    setExpandedLayers(newExpanded)
  }

  // Layer type colors
  const getLayerColor = (type: string) => {
    switch (type) {
      case 'geojson':
        return 'text-accent-primary'
      case 'raster':
        return 'text-accent-secondary'
      case 'vector-tile':
        return 'text-accent-warning'
      case '3d-terrain':
        return 'text-purple-400'
      default:
        return 'text-dark-200'
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-500">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-accent-primary" />
          <h2 className="font-semibold">Layers</h2>
        </div>
        <span className="text-xs text-dark-300 bg-dark-600 px-2 py-1 rounded">
          {layers.length} total
        </span>
      </div>

      {/* Layer list */}
      <div className="flex-1 overflow-y-auto p-2">
        {layers.length === 0 ? (
          <div className="p-4 text-center text-dark-300">
            <Layers className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No layers added yet</p>
            <p className="text-xs mt-1">
              Use the chat to add geospatial layers to the map
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {layers.map((layer) => (
              <div
                key={layer.id}
                className={`layer-item ${layer.visible ? 'active' : ''}`}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleExpand(layer.id)}
                      className="p-0.5 hover:bg-dark-500 rounded"
                    >
                      {expandedLayers.has(layer.id) ? (
                        <ChevronDown className="w-3 h-3" />
                      ) : (
                        <ChevronRight className="w-3 h-3" />
                      )}
                    </button>
                    <Circle className={`w-2 h-2 ${getLayerColor(layer.type)}`} fill="currentColor" />
                    <span className="text-sm font-medium truncate">{layer.name}</span>
                  </div>
                  
                  {/* Expanded content */}
                  {expandedLayers.has(layer.id) && (
                    <div className="mt-2 ml-6 space-y-2">
                      <div className="text-xs text-dark-300">
                        Type: <span className={getLayerColor(layer.type)}>{layer.type}</span>
                      </div>
                      
                      {/* Opacity slider */}
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-dark-300 w-12">Opacity</span>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={layer.opacity}
                          onChange={(e) => setLayerOpacity(layer.id, parseFloat(e.target.value))}
                          className="flex-1 h-1 bg-dark-500 rounded-lg appearance-none cursor-pointer"
                        />
                        <span className="text-xs text-dark-300 w-8">
                          {Math.round(layer.opacity * 100)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Layer controls */}
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => toggleLayerVisibility(layer.id)}
                    className="p-1.5 rounded hover:bg-dark-500 transition-colors"
                    title={layer.visible ? 'Hide layer' : 'Show layer'}
                  >
                    {layer.visible ? (
                      <Eye className="w-4 h-4 text-accent-primary" />
                    ) : (
                      <EyeOff className="w-4 h-4 text-dark-300" />
                    )}
                  </button>
                  <button
                    onClick={() => removeLayer(layer.id)}
                    className="p-1.5 rounded hover:bg-dark-500 transition-colors text-dark-300 hover:text-accent-danger"
                    title="Remove layer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Layer legend */}
      <div className="p-4 border-t border-dark-500">
        <div className="text-xs text-dark-300 mb-2">Layer Types</div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <Circle className="w-2 h-2 text-accent-primary" fill="currentColor" />
            <span>Vector</span>
          </div>
          <div className="flex items-center gap-2">
            <Circle className="w-2 h-2 text-accent-secondary" fill="currentColor" />
            <span>Raster</span>
          </div>
          <div className="flex items-center gap-2">
            <Circle className="w-2 h-2 text-accent-warning" fill="currentColor" />
            <span>Tiles</span>
          </div>
          <div className="flex items-center gap-2">
            <Circle className="w-2 h-2 text-purple-400" fill="currentColor" />
            <span>3D</span>
          </div>
        </div>
      </div>
    </div>
  )
}
