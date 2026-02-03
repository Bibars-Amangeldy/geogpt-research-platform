import { useState } from 'react'
import { 
  Layers, 
  Wind, 
  Factory, 
  Flame,
  Thermometer,
  Gauge,
  Eye,
  EyeOff,
  ChevronDown,
  RefreshCw,
  Satellite,
  Map as MapIcon,
  Mountain
} from 'lucide-react'
import { useAppStore } from '../store'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface DataLayer {
  id: string
  name: string
  icon: typeof Layers
  color: string
  endpoint: string
  description: string
  enabled: boolean
  loading: boolean
}

export default function MapToolbar() {
  const { sendMessage, addLayer, removeLayer, layers } = useAppStore()
  const [isExpanded, setIsExpanded] = useState(true)
  const [dataLayers, setDataLayers] = useState<DataLayer[]>([
    {
      id: 'air-quality',
      name: 'Air Quality',
      icon: Wind,
      color: '#22c55e',
      endpoint: '/api/environmental/air-quality',
      description: 'Real-time AQI monitoring',
      enabled: false,
      loading: false
    },
    {
      id: 'methane',
      name: 'Methane CH₄',
      icon: Flame,
      color: '#f97316',
      endpoint: '/api/environmental/methane',
      description: 'Methane emission hotspots',
      enabled: false,
      loading: false
    },
    {
      id: 'co2',
      name: 'CO₂ Emissions',
      icon: Factory,
      color: '#ef4444',
      endpoint: '/api/environmental/co2',
      description: 'Industrial CO₂ sources',
      enabled: false,
      loading: false
    },
    {
      id: 'temperature',
      name: 'Temperature',
      icon: Thermometer,
      color: '#3b82f6',
      endpoint: '/api/environmental/temperature',
      description: 'Surface temperature grid',
      enabled: false,
      loading: false
    },
    {
      id: 'fire',
      name: 'Active Fires',
      icon: Flame,
      color: '#dc2626',
      endpoint: '/api/environmental/fire',
      description: 'NASA FIRMS fire detection',
      enabled: false,
      loading: false
    }
  ])

  const toggleLayer = async (layerId: string) => {
    const layer = dataLayers.find(l => l.id === layerId)
    if (!layer) return

    // Update loading state
    setDataLayers(prev => prev.map(l => 
      l.id === layerId ? { ...l, loading: true } : l
    ))

    if (layer.enabled) {
      // Remove layer
      removeLayer(layerId)
      setDataLayers(prev => prev.map(l => 
        l.id === layerId ? { ...l, enabled: false, loading: false } : l
      ))
    } else {
      // Fetch and add layer using chat command for now
      const commands: Record<string, string> = {
        'air-quality': 'show air quality',
        'methane': 'show methane emissions',
        'co2': 'show co2 emissions',
        'temperature': 'temperature map',
        'fire': 'show fires'
      }
      
      try {
        await sendMessage(commands[layerId])
        setDataLayers(prev => prev.map(l => 
          l.id === layerId ? { ...l, enabled: true, loading: false } : l
        ))
      } catch (error) {
        console.error('Failed to load layer:', error)
        setDataLayers(prev => prev.map(l => 
          l.id === layerId ? { ...l, loading: false } : l
        ))
      }
    }
  }

  const enabledCount = dataLayers.filter(l => l.enabled).length

  return (
    <div className="absolute left-4 top-20 z-20">
      <div className="bg-dark-800/95 backdrop-blur-md border border-dark-500 rounded-xl shadow-2xl overflow-hidden w-56">
        {/* Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-3 py-2.5 flex items-center justify-between hover:bg-dark-700 transition-colors"
        >
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-accent-primary/20 rounded-lg">
              <Layers className="w-4 h-4 text-accent-primary" />
            </div>
            <span className="font-medium text-sm">Data Layers</span>
          </div>
          <div className="flex items-center gap-2">
            {enabledCount > 0 && (
              <span className="px-1.5 py-0.5 bg-accent-primary/20 text-accent-primary text-xs rounded-full">
                {enabledCount}
              </span>
            )}
            <ChevronDown className={`w-4 h-4 text-dark-300 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
          </div>
        </button>

        {/* Layer List */}
        {isExpanded && (
          <div className="border-t border-dark-500">
            {dataLayers.map((layer) => {
              const Icon = layer.icon
              return (
                <button
                  key={layer.id}
                  onClick={() => toggleLayer(layer.id)}
                  disabled={layer.loading}
                  className={`
                    w-full px-3 py-2 flex items-center gap-3 transition-all
                    ${layer.enabled 
                      ? 'bg-dark-700' 
                      : 'hover:bg-dark-700/50'
                    }
                    ${layer.loading ? 'opacity-50 cursor-wait' : ''}
                  `}
                >
                  {/* Icon */}
                  <div 
                    className="p-1.5 rounded-lg transition-colors"
                    style={{ 
                      backgroundColor: layer.enabled ? `${layer.color}20` : 'transparent',
                      border: `1px solid ${layer.enabled ? layer.color : 'transparent'}`
                    }}
                  >
                    {layer.loading ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" style={{ color: layer.color }} />
                    ) : (
                      <Icon className="w-3.5 h-3.5" style={{ color: layer.color }} />
                    )}
                  </div>
                  
                  {/* Label */}
                  <div className="flex-1 text-left">
                    <div className="text-sm font-medium" style={{ color: layer.enabled ? layer.color : 'inherit' }}>
                      {layer.name}
                    </div>
                    <div className="text-[10px] text-dark-400">{layer.description}</div>
                  </div>
                  
                  {/* Toggle Icon */}
                  {layer.enabled ? (
                    <Eye className="w-4 h-4" style={{ color: layer.color }} />
                  ) : (
                    <EyeOff className="w-4 h-4 text-dark-400" />
                  )}
                </button>
              )
            })}
          </div>
        )}

        {/* Quick Actions */}
        {isExpanded && (
          <div className="border-t border-dark-500 p-2">
            <div className="flex gap-1">
              <button
                onClick={() => dataLayers.forEach(l => !l.enabled && toggleLayer(l.id))}
                className="flex-1 px-2 py-1.5 text-xs bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors"
              >
                Show All
              </button>
              <button
                onClick={() => dataLayers.forEach(l => l.enabled && toggleLayer(l.id))}
                className="flex-1 px-2 py-1.5 text-xs bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors"
              >
                Hide All
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
