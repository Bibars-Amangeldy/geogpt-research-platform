import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ChatRequest {
  query: string
  context?: Record<string, any>
  map_bounds?: {
    north: number
    south: number
    east: number
    west: number
  }
}

export interface ChatResponse {
  message: string
  map_layers?: any[]
  code?: string
  data?: Record<string, any>
  visualization?: Record<string, any>
  status: string
}

export interface BasemapInfo {
  id: string
  name: string
  url: string
  type: 'style' | 'raster'
  attribution?: string
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 second timeout for AI queries
  headers: {
    'Content-Type': 'application/json',
  },
})

export const geoApi = {
  // Health check
  health: async () => {
    const response = await api.get('/health')
    return response.data
  },

  // Chat endpoint
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await api.post('/api/chat', request)
      return response.data
    } catch (error) {
      console.error('Chat API error:', error)
      // Return a fallback response for demo
      return {
        message: `I received your query: "${request.query}". The backend server might not be running. Please start the backend with: \`cd backend && python main.py\``,
        status: 'error',
      }
    }
  },

  // Get available basemaps
  getBasemaps: async (): Promise<BasemapInfo[]> => {
    try {
      const response = await api.get('/api/layers/basemaps')
      return response.data.basemaps
    } catch (error) {
      // Return default basemaps if API is not available
      return [
        {
          id: 'dark',
          name: 'Dark Mode',
          url: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
          type: 'style',
        },
        {
          id: 'satellite',
          name: 'Satellite',
          url: 'https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg',
          type: 'raster',
        },
      ]
    }
  },

  // Get Kazakhstan data
  getKazakhstanData: async () => {
    try {
      const response = await api.get('/api/data/kazakhstan')
      return response.data
    } catch (error) {
      // Return default data
      return {
        center: [67.0, 48.0],
        zoom: 4,
        bounds: [[46.5, 40.5], [87.3, 55.4]],
        regions: [
          { name: 'Astana', coordinates: [71.4491, 51.1801], type: 'capital' },
          { name: 'Almaty', coordinates: [76.9458, 43.2220], type: 'city' },
        ],
      }
    }
  },
}

// WebSocket connection for real-time chat
export class ChatWebSocket {
  private ws: WebSocket | null = null
  private messageHandler: ((data: any) => void) | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(onMessage: (data: any) => void) {
    this.messageHandler = onMessage
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/chat'
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (this.messageHandler) {
          this.messageHandler(data)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      this.ws.onclose = () => {
        console.log('WebSocket closed')
        this.attemptReconnect()
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.messageHandler) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => this.connect(this.messageHandler!), 2000 * this.reconnectAttempts)
    }
  }

  send(query: string, context?: Record<string, any>) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ query, context }))
    } else {
      console.error('WebSocket not connected')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export const chatWebSocket = new ChatWebSocket()
