import { useAppStore } from '../store'
import { 
  MessageSquare, 
  Layers, 
  Database, 
  Code,
  ChevronLeft,
  ChevronRight,
  Settings,
  HelpCircle,
  Globe2
} from 'lucide-react'
import ChatPanel from './ChatPanel'
import LayersPanel from './LayersPanel'

export default function Sidebar() {
  const { isSidebarOpen, toggleSidebar, activePanel, setActivePanel } = useAppStore()

  const panels = [
    { id: 'chat' as const, icon: MessageSquare, label: 'Chat', component: ChatPanel },
    { id: 'layers' as const, icon: Layers, label: 'Layers', component: LayersPanel },
    { id: 'data' as const, icon: Database, label: 'Data', component: DataPanel },
    { id: 'code' as const, icon: Code, label: 'Code', component: CodePanel },
  ]

  const ActiveComponent = panels.find(p => p.id === activePanel)?.component || ChatPanel

  return (
    <div className={`flex h-full transition-all duration-300 ${isSidebarOpen ? 'w-[26rem]' : 'w-14'}`}>
      {/* Navigation rail */}
      <div className="w-14 flex-shrink-0 bg-dark-800 border-r border-dark-500 flex flex-col">
        {/* Logo */}
        <div className="p-3 border-b border-dark-500">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
            <Globe2 className="w-5 h-5 text-dark-900" />
          </div>
        </div>

        {/* Panel buttons */}
        <div className="flex-1 py-2 space-y-1">
          {panels.map((panel) => {
            const Icon = panel.icon
            const isActive = activePanel === panel.id
            return (
              <button
                key={panel.id}
                onClick={() => {
                  setActivePanel(panel.id)
                  if (!isSidebarOpen) toggleSidebar()
                }}
                className={`w-full p-3 flex flex-col items-center gap-1 transition-colors relative ${
                  isActive
                    ? 'text-accent-primary'
                    : 'text-dark-200 hover:text-white hover:bg-dark-700'
                }`}
                title={panel.label}
              >
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-accent-primary rounded-r" />
                )}
                <Icon className="w-5 h-5" />
                <span className="text-[10px]">{panel.label}</span>
              </button>
            )
          })}
        </div>

        {/* Bottom actions */}
        <div className="py-2 border-t border-dark-500 space-y-1">
          <button
            className="w-full p-3 flex flex-col items-center gap-1 text-dark-200 hover:text-white hover:bg-dark-700 transition-colors"
            title="Help"
          >
            <HelpCircle className="w-5 h-5" />
            <span className="text-[10px]">Help</span>
          </button>
          <button
            className="w-full p-3 flex flex-col items-center gap-1 text-dark-200 hover:text-white hover:bg-dark-700 transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
            <span className="text-[10px]">Settings</span>
          </button>
        </div>
      </div>

      {/* Main panel content */}
      {isSidebarOpen && (
        <div className="flex-1 bg-dark-800 border-r border-dark-500 flex flex-col relative">
          <ActiveComponent />
          
          {/* Collapse button */}
          <button
            onClick={toggleSidebar}
            className="absolute -right-3 top-1/2 -translate-y-1/2 p-1 bg-dark-700 border border-dark-500 rounded-full hover:bg-dark-600 transition-colors z-20"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Expand button when collapsed */}
      {!isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="absolute left-14 top-1/2 -translate-y-1/2 p-1 bg-dark-700 border border-dark-500 rounded-full hover:bg-dark-600 transition-colors z-20"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

// Data Panel placeholder
function DataPanel() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 p-4 border-b border-dark-500">
        <Database className="w-5 h-5 text-accent-primary" />
        <h2 className="font-semibold">Data Sources</h2>
      </div>
      <div className="flex-1 p-4 space-y-4">
        <div className="p-3 bg-dark-700 rounded-lg border border-dark-500">
          <h3 className="font-medium text-sm mb-2">Available Catalogs</h3>
          <ul className="space-y-2 text-sm text-dark-200">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-accent-success rounded-full"></span>
              NASA Earth Data
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-accent-success rounded-full"></span>
              Planetary Computer
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-accent-success rounded-full"></span>
              Earth Search (AWS)
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-accent-success rounded-full"></span>
              USGS STAC
            </li>
          </ul>
        </div>
        
        <div className="p-3 bg-dark-700 rounded-lg border border-dark-500">
          <h3 className="font-medium text-sm mb-2">Satellite Imagery</h3>
          <ul className="space-y-1 text-sm text-dark-200">
            <li>• Sentinel-2 (10m optical)</li>
            <li>• Sentinel-1 (SAR)</li>
            <li>• Landsat 8/9</li>
            <li>• MODIS</li>
          </ul>
        </div>

        <div className="p-3 bg-dark-700 rounded-lg border border-dark-500">
          <h3 className="font-medium text-sm mb-2">AI Models</h3>
          <ul className="space-y-1 text-sm text-dark-200">
            <li>• IBM-NASA Prithvi (EO)</li>
            <li>• Segment Anything (SAM)</li>
            <li>• ApexGIS (Llama/Qwen)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Code Panel placeholder
function CodePanel() {
  const { messages } = useAppStore()
  
  // Get all code from messages
  const codeSnippets = messages
    .filter((m: any) => m.code)
    .map((m: any) => ({ timestamp: m.timestamp, code: m.code }))

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 p-4 border-b border-dark-500">
        <Code className="w-5 h-5 text-accent-primary" />
        <h2 className="font-semibold">Generated Code</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {codeSnippets.length === 0 ? (
          <div className="text-center text-dark-300 p-4">
            <Code className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No code generated yet</p>
            <p className="text-xs mt-1">
              Ask ApexGIS AI to analyze data to see the Python code
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {codeSnippets.map((snippet: any, idx: number) => (
              <div key={idx} className="bg-dark-900 rounded-lg border border-dark-500 overflow-hidden">
                <div className="px-3 py-2 bg-dark-800 border-b border-dark-500 flex items-center justify-between">
                  <span className="text-xs text-dark-300">
                    {snippet.timestamp.toLocaleTimeString()}
                  </span>
                  <span className="text-xs text-accent-primary">Python</span>
                </div>
                <pre className="p-4 text-sm font-mono text-dark-100 overflow-x-auto">
                  <code>{snippet.code}</code>
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
