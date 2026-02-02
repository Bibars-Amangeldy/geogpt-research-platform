import { create } from 'zustand'

export interface MapLayer {
  id: string
  name: string
  type: 'geojson' | 'raster' | 'vector-tile' | '3d-terrain' | 'deck'
  visible: boolean
  opacity: number
  source: any
  paint?: any
  deckLayer?: any
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  code?: string
  mapLayers?: MapLayer[]
  data?: any
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
  
  // Chat state
  messages: ChatMessage[]
  isLoading: boolean
  
  // UI state
  isSidebarOpen: boolean
  activePanel: 'chat' | 'layers' | 'data' | 'code'
  showCode: boolean
  
  // Actions
  setViewState: (viewState: Partial<MapViewState>) => void
  addLayer: (layer: MapLayer) => void
  removeLayer: (layerId: string) => void
  toggleLayerVisibility: (layerId: string) => void
  setLayerOpacity: (layerId: string, opacity: number) => void
  setBasemap: (basemapId: string) => void
  toggle3D: () => void
  
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  
  toggleSidebar: () => void
  setActivePanel: (panel: 'chat' | 'layers' | 'data' | 'code') => void
  toggleCode: () => void
}

export const useAppStore = create<AppState>((set) => ({
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
  
  // Initial chat state
  messages: [
    {
      id: 'welcome',
      role: 'assistant',
      content: `# 🌍 Welcome to GeoGPT Research Platform

I'm your AI assistant for geospatial analysis and visualization. I can help you with:

- **Satellite imagery analysis** (NDVI, land cover, change detection)
- **Flood and water body detection**
- **Land use classification** using deep learning
- **Terrain analysis** and 3D visualization
- **Geographic data** from NASA, ESA, and other sources

Try asking me something like:
- "Show me Kazakhstan on the map"
- "Calculate NDVI for Almaty region"
- "Detect water bodies near Astana"
- "Show land use classification"

The map is currently centered on **Kazakhstan** 🇰🇿`,
      timestamp: new Date(),
    },
  ],
  isLoading: false,
  
  // Initial UI state
  isSidebarOpen: true,
  activePanel: 'chat',
  showCode: false,
  
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
    }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  // UI actions
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setActivePanel: (panel) => set({ activePanel: panel }),
  toggleCode: () => set((state) => ({ showCode: !state.showCode })),
}))
