import { useState, useEffect, useCallback } from 'react'
import { 
  Factory, 
  Wind, 
  Thermometer, 
  Flame,
  Gauge,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Eye,
  EyeOff,
  Layers,
  Activity
} from 'lucide-react'
import { useAppStore } from '../store'

// Get API URL - production or local
const getApiBase = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  if (typeof window !== 'undefined' && 
      (window.location.hostname.includes('vercel.app') || 
       window.location.hostname.includes('apexgeo'))) {
    return 'https://apexgeo-api-production.up.railway.app'
  }
  return 'http://localhost:8000'
}

const API_BASE = getApiBase()

// Environmental layer types
type EnvLayerType = 'air-quality' | 'methane' | 'co2' | 'temperature' | 'fire' | 'wind'

interface EnvLayerConfig {
  id: EnvLayerType
  name: string
  icon: typeof Factory
  color: string
  description: string
  enabled: boolean
}

// Layer configurations
const ENV_LAYERS: EnvLayerConfig[] = [
  { 
    id: 'air-quality', 
    name: 'Air Quality (AQI)', 
    icon: Wind, 
    color: '#22c55e',
    description: 'Real-time air quality monitoring stations',
    enabled: false 
  },
  { 
    id: 'methane', 
    name: 'Methane (CH₄)', 
    icon: Flame, 
    color: '#f97316',
    description: 'Methane emission hotspots from Sentinel-5P',
    enabled: false 
  },
  { 
    id: 'co2', 
    name: 'CO₂ Emissions', 
    icon: Factory, 
    color: '#ef4444',
    description: 'Industrial CO2 emission sources',
    enabled: false 
  },
  { 
    id: 'temperature', 
    name: 'Temperature', 
    icon: Thermometer, 
    color: '#3b82f6',
    description: 'ERA5 temperature data grid',
    enabled: false 
  },
  { 
    id: 'fire', 
    name: 'Active Fires', 
    icon: Flame, 
    color: '#dc2626',
    description: 'NASA FIRMS fire detection',
    enabled: false 
  },
  { 
    id: 'wind', 
    name: 'Wind Flow', 
    icon: Wind, 
    color: '#06b6d4',
    description: 'Animated wind patterns',
    enabled: false 
  },
]

// AQI color scale
const getAqiColor = (aqi: number): string => {
  if (aqi <= 50) return '#00e400'    // Good
  if (aqi <= 100) return '#ffff00'   // Moderate
  if (aqi <= 150) return '#ff7e00'   // Unhealthy for Sensitive
  if (aqi <= 200) return '#ff0000'   // Unhealthy
  if (aqi <= 300) return '#8f3f97'   // Very Unhealthy
  return '#7e0023'                    // Hazardous
}

// Dashboard data interfaces
interface AirQualityData {
  stations: Array<{
    name: string
    aqi: number
    category: string
    dominant_pollutant: string
    coordinates: { lat: number; lon: number }
    pollutants: {
      pm25: { value: number; unit: string }
      pm10: { value: number; unit: string }
      no2: { value: number; unit: string }
      o3: { value: number; unit: string }
    }
  }>
  summary: {
    overall_status: string
    monitoring_count: number
    avg_aqi: number
  }
}

interface MethaneData {
  hotspots: Array<{
    name: string
    type: string
    emission_rate_kt_per_year: number
    concentration_ppb: number
    trend: string
    coordinates: [number, number]
  }>
  total_emissions_mt: number
}

interface CO2Data {
  sources: Array<{
    name: string
    type: string
    sector: string
    annual_emissions_mt: number
    coordinates: [number, number]
  }>
  by_sector: Record<string, number>
}

interface DashboardData {
  airQuality?: AirQualityData
  methane?: MethaneData
  co2?: CO2Data
  lastUpdated: string
}

export default function EnvironmentalPanel() {
  const [isExpanded, setIsExpanded] = useState(true)
  const [activeTab, setActiveTab] = useState<'layers' | 'dashboard'>('layers')
  const [layers, setLayers] = useState<EnvLayerConfig[]>(ENV_LAYERS)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { sendMessage } = useAppStore()

  // Toggle layer visibility
  const toggleLayer = useCallback((layerId: EnvLayerType) => {
    setLayers(prev => prev.map(l => 
      l.id === layerId ? { ...l, enabled: !l.enabled } : l
    ))
    
    // Send command to chat to load data
    const layer = layers.find(l => l.id === layerId)
    if (layer && !layer.enabled) {
      const commands: Record<EnvLayerType, string> = {
        'air-quality': 'show air quality',
        'methane': 'show methane emissions',
        'co2': 'show co2 emissions',
        'temperature': 'temperature map',
        'fire': 'show fires',
        'wind': 'wind flow'
      }
      sendMessage(commands[layerId])
    }
  }, [layers, sendMessage])

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE}/api/environmental/dashboard`)
      if (response.ok) {
        const data = await response.json()
        setDashboardData({
          ...data.dashboard,
          lastUpdated: new Date().toISOString()
        })
      } else {
        // Try individual endpoints as fallback
        const [airRes, methaneRes, co2Res] = await Promise.allSettled([
          fetch(`${API_BASE}/api/environmental/air-quality`),
          fetch(`${API_BASE}/api/environmental/methane`),
          fetch(`${API_BASE}/api/environmental/co2`)
        ])
        
        const dashboard: DashboardData = { lastUpdated: new Date().toISOString() }
        
        if (airRes.status === 'fulfilled' && airRes.value.ok) {
          dashboard.airQuality = await airRes.value.json()
        }
        if (methaneRes.status === 'fulfilled' && methaneRes.value.ok) {
          dashboard.methane = await methaneRes.value.json()
        }
        if (co2Res.status === 'fulfilled' && co2Res.value.ok) {
          dashboard.co2 = await co2Res.value.json()
        }
        
        setDashboardData(dashboard)
      }
    } catch (err) {
      setError('Failed to fetch environmental data')
      console.error('Dashboard fetch error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Load dashboard data on mount
  useEffect(() => {
    fetchDashboardData()
    // Refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [fetchDashboardData])

  return (
    <div className="absolute top-4 right-4 z-20 w-80">
      {/* Header */}
      <div 
        className="bg-dark-800/95 backdrop-blur-sm rounded-t-xl border border-dark-600 px-4 py-3 cursor-pointer hover:bg-dark-700/95 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-white text-sm">Environmental Monitor</h3>
              <p className="text-xs text-dark-300">Real-time data</p>
            </div>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-dark-300" />
          ) : (
            <ChevronDown className="w-5 h-5 text-dark-300" />
          )}
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="bg-dark-800/95 backdrop-blur-sm border border-t-0 border-dark-600 rounded-b-xl overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-dark-600">
            <button
              onClick={() => setActiveTab('layers')}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === 'layers' 
                  ? 'text-primary bg-dark-700/50 border-b-2 border-primary' 
                  : 'text-dark-300 hover:text-white hover:bg-dark-700/30'
              }`}
            >
              <Layers className="w-4 h-4 inline mr-1.5" />
              Layers
            </button>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === 'dashboard' 
                  ? 'text-primary bg-dark-700/50 border-b-2 border-primary' 
                  : 'text-dark-300 hover:text-white hover:bg-dark-700/30'
              }`}
            >
              <Gauge className="w-4 h-4 inline mr-1.5" />
              Dashboard
            </button>
          </div>

          {/* Layers Tab */}
          {activeTab === 'layers' && (
            <div className="p-3 space-y-2 max-h-[400px] overflow-y-auto scrollbar-thin">
              {layers.map((layer) => {
                const Icon = layer.icon
                return (
                  <button
                    key={layer.id}
                    onClick={() => toggleLayer(layer.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all ${
                      layer.enabled 
                        ? 'bg-dark-600/80 ring-1 ring-primary/50' 
                        : 'bg-dark-700/50 hover:bg-dark-600/50'
                    }`}
                  >
                    <div 
                      className="p-2 rounded-lg"
                      style={{ backgroundColor: `${layer.color}20` }}
                    >
                      <Icon className="w-4 h-4" style={{ color: layer.color }} />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white text-sm">{layer.name}</span>
                        {layer.enabled ? (
                          <Eye className="w-3.5 h-3.5 text-primary" />
                        ) : (
                          <EyeOff className="w-3.5 h-3.5 text-dark-400" />
                        )}
                      </div>
                      <p className="text-xs text-dark-300 line-clamp-1">{layer.description}</p>
                    </div>
                  </button>
                )
              })}
              
              {/* Quick Commands */}
              <div className="pt-3 mt-3 border-t border-dark-600">
                <p className="text-xs text-dark-400 mb-2">Quick Commands</p>
                <div className="flex flex-wrap gap-1.5">
                  {['Show dashboard', 'Compare emissions', 'Air quality history'].map(cmd => (
                    <button
                      key={cmd}
                      onClick={() => sendMessage(cmd)}
                      className="px-2 py-1 text-xs bg-dark-700 hover:bg-dark-600 text-dark-200 hover:text-white rounded-md transition-colors"
                    >
                      {cmd}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div className="p-3 space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin">
              {/* Refresh Button */}
              <div className="flex justify-between items-center">
                <span className="text-xs text-dark-400">
                  {dashboardData?.lastUpdated 
                    ? `Updated: ${new Date(dashboardData.lastUpdated).toLocaleTimeString()}`
                    : 'Loading...'
                  }
                </span>
                <button
                  onClick={fetchDashboardData}
                  disabled={isLoading}
                  className="p-1.5 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 text-dark-300 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {error && (
                <div className="p-2 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  {error}
                </div>
              )}

              {/* Air Quality Card */}
              <div className="bg-dark-700/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Wind className="w-4 h-4 text-emerald-400" />
                  <span className="font-medium text-white text-sm">Air Quality</span>
                </div>
                {dashboardData?.airQuality ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Average AQI</span>
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: getAqiColor(dashboardData.airQuality.summary?.avg_aqi || 50) }}
                        />
                        <span className="font-bold text-white">
                          {Math.round(dashboardData.airQuality.summary?.avg_aqi || 50)}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Status</span>
                      <span className="text-xs text-emerald-400">
                        {dashboardData.airQuality.summary?.overall_status || 'Moderate'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Stations</span>
                      <span className="text-xs text-dark-200">
                        {dashboardData.airQuality.summary?.monitoring_count || 8} active
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="h-16 flex items-center justify-center">
                    <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
              </div>

              {/* Methane Card */}
              <div className="bg-dark-700/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Flame className="w-4 h-4 text-orange-400" />
                  <span className="font-medium text-white text-sm">Methane (CH₄)</span>
                </div>
                {dashboardData?.methane ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Total Emissions</span>
                      <span className="font-bold text-white">
                        {dashboardData.methane.total_emissions_mt?.toFixed(2) || '2.35'} MT/yr
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Hotspots</span>
                      <span className="text-xs text-orange-400">
                        {dashboardData.methane.hotspots?.length || 5} sources
                      </span>
                    </div>
                    {dashboardData.methane.hotspots?.[0] && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-dark-300">Largest</span>
                        <span className="text-xs text-dark-200">
                          {dashboardData.methane.hotspots[0].name}
                        </span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="h-16 flex items-center justify-center">
                    <div className="w-5 h-5 border-2 border-orange-400 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
              </div>

              {/* CO2 Card */}
              <div className="bg-dark-700/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Factory className="w-4 h-4 text-red-400" />
                  <span className="font-medium text-white text-sm">CO₂ Emissions</span>
                </div>
                {dashboardData?.co2 ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Total</span>
                      <span className="font-bold text-white">
                        {Object.values(dashboardData.co2.by_sector || {}).reduce((a, b) => a + b, 0).toFixed(1)} MT/yr
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-dark-300">Sources</span>
                      <span className="text-xs text-red-400">
                        {dashboardData.co2.sources?.length || 6} facilities
                      </span>
                    </div>
                    {/* Sector breakdown mini-chart */}
                    {dashboardData.co2.by_sector && (
                      <div className="pt-2 border-t border-dark-600">
                        <span className="text-xs text-dark-400">By Sector</span>
                        <div className="flex gap-1 mt-1.5">
                          {Object.entries(dashboardData.co2.by_sector).slice(0, 4).map(([sector, value], i) => {
                            const colors = ['#ef4444', '#f97316', '#22c55e', '#3b82f6']
                            const total = Object.values(dashboardData.co2?.by_sector || {}).reduce((a, b) => a + b, 0)
                            return (
                              <div 
                                key={sector} 
                                className="flex-1 h-2 rounded-full"
                                style={{ 
                                  backgroundColor: colors[i],
                                  opacity: (value / total) + 0.3
                                }}
                                title={`${sector}: ${value.toFixed(1)} MT`}
                              />
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="h-16 flex items-center justify-center">
                    <div className="w-5 h-5 border-2 border-red-400 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
              </div>

              {/* Legend */}
              <div className="pt-2 border-t border-dark-600">
                <p className="text-xs text-dark-400 mb-2">AQI Scale</p>
                <div className="flex gap-0.5">
                  {[
                    { color: '#00e400', label: 'Good' },
                    { color: '#ffff00', label: 'Mod' },
                    { color: '#ff7e00', label: 'USG' },
                    { color: '#ff0000', label: 'Bad' },
                    { color: '#8f3f97', label: 'V.Bad' },
                    { color: '#7e0023', label: 'Haz' }
                  ].map(item => (
                    <div key={item.label} className="flex-1 text-center">
                      <div className="h-2 rounded-sm" style={{ backgroundColor: item.color }} />
                      <span className="text-[9px] text-dark-400">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
