import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { geoApi } from './api'

export interface MapLayer {
  id: string
  name: string
  type: 'geojson' | 'raster' | 'vector-tile' | '3d-terrain' | 'deck' | 'fill-extrusion' | 'heatmap' | 'circle' | 'line'
  visible: boolean
  opacity: number
  source: any
  paint?: any
  deckLayer?: any
}

export interface ChartData {
  type: 'line' | 'bar' | 'horizontalBar' | 'doughnut' | 'pie' | 'radar'
  title: string
  labels: (string | number)[]
  datasets: {
    label?: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string
    fill?: boolean
    tension?: number
  }[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  code?: string
  mapLayers?: MapLayer[]
  data?: any
  chart?: ChartData
  mapAction?: any
}

export interface MapViewState {
  longitude: number
  latitude: number
  zoom: number
  pitch: number
  bearing: number
}

interface AppState {
  // Map state
  viewState: MapViewState
  layers: MapLayer[]
  selectedBasemap: string
  is3DEnabled: boolean
  pendingMapAction: any | null
  
  // Chat state
  messages: ChatMessage[]
  isLoading: boolean
  currentChart: ChartData | null
  
  // UI state
  isSidebarOpen: boolean
  activePanel: 'chat' | 'layers' | 'data' | 'code'
  showCode: boolean
  showChart: boolean
  
  // Actions
  setViewState: (viewState: Partial<MapViewState>) => void
  addLayer: (layer: MapLayer) => void
  removeLayer: (layerId: string) => void
  clearLayers: () => void
  toggleLayerVisibility: (layerId: string) => void
  setLayerOpacity: (layerId: string, opacity: number) => void
  setBasemap: (basemapId: string) => void
  toggle3D: () => void
  setMapAction: (action: any) => void
  clearMapAction: () => void
  
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  setChart: (chart: ChartData | null) => void
  sendMessage: (query: string) => Promise<void>
  
  toggleSidebar: () => void
  setActivePanel: (panel: 'chat' | 'layers' | 'data' | 'code') => void
  toggleCode: () => void
  toggleChart: () => void
}

export const useAppStore = create<AppState>()(
  subscribeWithSelector((set) => ({
    // Initial map state - centered on Kazakhstan
    viewState: {
      longitude: 67.0,
      latitude: 48.0,
      zoom: 4,
      pitch: 0,
      bearing: 0,
    },
    layers: [],
    selectedBasemap: 'dark',
    is3DEnabled: false,
    pendingMapAction: null,
    
    // Initial chat state
    messages: [
      {
        id: 'welcome',
        role: 'assistant',
        content: `# 🌍 Welcome to ApexGIS v3.0 - Presidential Platform

I'm your AI assistant for advanced geospatial and environmental analysis. Here's what I can do:

**🌡️ Environmental Monitoring (NEW!):**
- "Show air quality" - Real-time AQI data
- "Show methane emissions" - CH₄ hotspots
- "Show CO2 emissions" - Industrial sources
- "Wind flow" - Animated wind patterns

**🔥 Active Monitoring:**
- "Show fires" - NASA FIRMS fire detection
- "Temperature map" - ERA5 temperature data
- "Environmental dashboard" - All data overview

**📍 City Navigation:**
- "Show me Astana" / "Zoom to Almaty"
- "Go to Shymkent"

**💧 Hydrology:**
- "Glaciers near Almaty"
- "Rivers near Almaty"
- "Show all water bodies"

**📊 Data Analysis:**
- "Population of Almaty"
- "Compare Astana vs Almaty"
- "Show all cities"

*Data Sources: OpenAQ, Sentinel-5P, NASA FIRMS, ERA5*
Currently tracking environmental data across Kazakhstan 🇰🇿`,
        timestamp: new Date(),
      },
    ],
    isLoading: false,
    currentChart: null,
    
    // Initial UI state
    isSidebarOpen: true,
    activePanel: 'chat',
    showCode: false,
    showChart: true,
    
    // Map actions
    setViewState: (viewState) =>
      set((state) => ({
        viewState: { ...state.viewState, ...viewState },
      })),
    
    addLayer: (layer) =>
      set((state) => ({
        layers: [...state.layers.filter((l) => l.id !== layer.id), layer],
      })),
    
    removeLayer: (layerId) =>
      set((state) => ({
        layers: state.layers.filter((l) => l.id !== layerId),
      })),
    
    clearLayers: () => set({ layers: [] }),
    
    toggleLayerVisibility: (layerId) =>
      set((state) => ({
        layers: state.layers.map((l) =>
          l.id === layerId ? { ...l, visible: !l.visible } : l
        ),
      })),
    
    setLayerOpacity: (layerId, opacity) =>
      set((state) => ({
        layers: state.layers.map((l) =>
          l.id === layerId ? { ...l, opacity } : l
        ),
      })),
    
    setBasemap: (basemapId) => set({ selectedBasemap: basemapId }),
    
    toggle3D: () =>
      set((state) => ({
        is3DEnabled: !state.is3DEnabled,
        viewState: {
          ...state.viewState,
          pitch: state.is3DEnabled ? 0 : 45,
        },
      })),
    
    setMapAction: (action) => set({ pendingMapAction: action }),
    clearMapAction: () => set({ pendingMapAction: null }),
    
    // Chat actions
    addMessage: (message) =>
      set((state) => ({
        messages: [
          ...state.messages,
          {
            ...message,
            id: `msg-${Date.now()}`,
            timestamp: new Date(),
          },
        ],
      })),
    
    clearMessages: () =>
      set({
        messages: [
          {
            id: 'welcome',
            role: 'assistant',
            content: '🌍 Chat cleared. How can I help you with geospatial analysis?',
            timestamp: new Date(),
          },
        ],
        currentChart: null,
      }),
    
    setLoading: (loading) => set({ isLoading: loading }),
    
    setChart: (chart) => set({ currentChart: chart }),
    
    // Send message and process response
    sendMessage: async (query) => {
      const state = useAppStore.getState()
      
      // Add user message
      state.addMessage({ role: 'user', content: query })
      state.setLoading(true)
      
      try {
        const response = await geoApi.chat({ query })
        
        // Add assistant message
        state.addMessage({
          role: 'assistant',
          content: response.message,
          chart: response.chart as ChartData | undefined,
          mapAction: response.map_action,
          mapLayers: response.map_layers?.map((layer: any) => ({
            id: layer.id,
            name: layer.id,
            type: layer.type,
            visible: true,
            opacity: 1,
            source: layer.source,
            paint: layer.paint
          }))
        })
        
        // Handle map layers
        if (response.map_layers) {
          state.clearLayers()
          response.map_layers.forEach((layer: any) => {
            state.addLayer({
              id: layer.id,
              name: layer.id,
              type: layer.type,
              visible: true,
              opacity: 1,
              source: layer.source,
              paint: layer.paint
            })
          })
        }
        
        // Handle chart
        if (response.chart) {
          state.setChart(response.chart as ChartData)
        }
        
        // Handle map action
        if (response.map_action) {
          state.setMapAction(response.map_action)
        }
      } catch (error) {
        state.addMessage({
          role: 'assistant',
          content: '❌ Failed to process request. Please try again.'
        })
        console.error('Chat error:', error)
      } finally {
        state.setLoading(false)
      }
    },
    
    // UI actions
    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    setActivePanel: (panel) => set({ activePanel: panel }),
    toggleCode: () => set((state) => ({ showCode: !state.showCode })),
    toggleChart: () => set((state) => ({ showChart: !state.showChart })),
  }))
)
