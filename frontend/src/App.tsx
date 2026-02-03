import { useEffect, useState } from 'react'
import MapView from './components/MapView'
import Sidebar from './components/Sidebar'
import EnvironmentalPanel from './components/EnvironmentalPanel'
import ReportDownload from './components/ReportDownload'
import MapToolbar from './components/MapToolbar'
import { geoApi } from './api'
import { Globe2, Menu } from 'lucide-react'
import { useAppStore } from './store'

function App() {
  const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null)
  const { isSidebarOpen, toggleSidebar } = useAppStore()

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
      {/* Sidebar - Collapsible */}
      <Sidebar />

      {/* Main content area - Map-centric */}
      <div className="flex-1 relative">
        {/* Full-screen Map */}
        <MapView />

        {/* Top Header Bar */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30">
          <div className="glass-panel px-5 py-2.5 flex items-center gap-4">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-lg">
                <Globe2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-bold text-lg">ApexGIS</span>
                <span className="text-[10px] text-dark-300 ml-2 hidden md:inline">Presidential Platform</span>
              </div>
            </div>
            
            {/* Divider */}
            <div className="w-px h-6 bg-dark-500" />
            
            {/* Status */}
            {isBackendConnected === null ? (
              <span className="text-xs text-dark-300">Connecting...</span>
            ) : isBackendConnected ? (
              <div className="flex items-center gap-1.5 text-xs">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-green-400">Live Data</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-xs">
                <div className="w-2 h-2 bg-amber-500 rounded-full" />
                <span className="text-amber-400">Demo Mode</span>
              </div>
            )}
            
            {/* Divider */}
            <div className="w-px h-6 bg-dark-500" />
            
            {/* Report Download */}
            <ReportDownload />
          </div>
        </div>

        {/* Map Toolbar - Data Layers Control */}
        <MapToolbar />

        {/* Environmental Data Panel - Right Side */}
        <EnvironmentalPanel />

        {/* Toggle Sidebar Button (when collapsed) */}
        {!isSidebarOpen && (
          <button
            onClick={toggleSidebar}
            className="absolute left-4 bottom-4 z-30 p-3 bg-dark-800/90 backdrop-blur-sm border border-dark-500 rounded-xl hover:bg-dark-700 transition-colors shadow-lg"
            title="Open Chat Panel"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

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
            <h2 className="text-xl font-semibold mb-2">ApexGIS Platform</h2>
            <p className="text-dark-300">Initializing geospatial AI systems...</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
