import { useEffect, useState } from 'react'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import { geoApi } from './api'
import { Globe2, AlertCircle, CheckCircle2 } from 'lucide-react'

function App() {
  const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null)

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await geoApi.health()
        setIsBackendConnected(true)
      } catch (error) {
        setIsBackendConnected(false)
      }
    }
    
    checkBackend()
    // Re-check every 30 seconds
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex h-screen bg-dark-900 text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area - Map */}
      <div className="flex-1 relative">
        <MapView />

        {/* Status indicator */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10">
          <div className="glass-panel px-4 py-2 flex items-center gap-3">
            <Globe2 className="w-5 h-5 text-accent-primary" />
            <span className="font-semibold">GeoGPT Research Platform</span>
            <div className="w-px h-4 bg-dark-500" />
            {isBackendConnected === null ? (
              <span className="text-xs text-dark-300">Connecting...</span>
            ) : isBackendConnected ? (
              <div className="flex items-center gap-1 text-xs text-accent-success">
                <CheckCircle2 className="w-3 h-3" />
                <span>Backend connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-xs text-accent-warning">
                <AlertCircle className="w-3 h-3" />
                <span>Demo mode</span>
              </div>
            )}
          </div>
        </div>

        {/* Kazakhstan flag overlay for presentation */}
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-10 opacity-0 hover:opacity-100 transition-opacity">
          <div className="glass-panel px-4 py-2 text-center">
            <div className="text-2xl mb-1">🇰🇿</div>
            <div className="text-xs text-dark-200">Republic of Kazakhstan</div>
          </div>
        </div>
      </div>

      {/* Global loading overlay for initial load */}
      {isBackendConnected === null && (
        <div className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 relative">
              <Globe2 className="w-16 h-16 text-accent-primary animate-pulse" />
              <div className="absolute inset-0 border-4 border-accent-primary/30 rounded-full animate-ping" />
            </div>
            <h2 className="text-xl font-semibold mb-2">GeoGPT Research Platform</h2>
            <p className="text-dark-300">Initializing geospatial AI systems...</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
