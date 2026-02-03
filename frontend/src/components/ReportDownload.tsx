import { useState } from 'react'
import { 
  FileDown, 
  Loader2, 
  Check, 
  FileText,
  Settings2,
  X
} from 'lucide-react'

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

interface ReportOptions {
  title: string
  includeAirQuality: boolean
  includeMethane: boolean
  includeCO2: boolean
  includeFires: boolean
}

export default function ReportDownload() {
  const [isDownloading, setIsDownloading] = useState(false)
  const [showOptions, setShowOptions] = useState(false)
  const [downloadComplete, setDownloadComplete] = useState(false)
  const [options, setOptions] = useState<ReportOptions>({
    title: 'Environmental Monitoring Report',
    includeAirQuality: true,
    includeMethane: true,
    includeCO2: true,
    includeFires: true
  })

  const handleDownload = async () => {
    setIsDownloading(true)
    setDownloadComplete(false)
    
    try {
      const params = new URLSearchParams({
        title: options.title,
        include_air_quality: String(options.includeAirQuality),
        include_methane: String(options.includeMethane),
        include_co2: String(options.includeCO2),
        include_fires: String(options.includeFires)
      })
      
      const response = await fetch(`${API_BASE}/api/environmental/report/pdf?${params}`)
      
      if (!response.ok) {
        throw new Error('Failed to generate report')
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition')
      const filename = contentDisposition 
        ? contentDisposition.split('filename=')[1] 
        : `ApexGIS_Report_${new Date().toISOString().split('T')[0]}.pdf`
      
      a.download = filename.replace(/"/g, '')
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      setDownloadComplete(true)
      setTimeout(() => setDownloadComplete(false), 3000)
      
    } catch (error) {
      console.error('Download failed:', error)
      alert('Failed to download report. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="relative">
      {/* Main Download Button */}
      <div className="flex items-center gap-1">
        <button
          onClick={handleDownload}
          disabled={isDownloading}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg font-medium
            transition-all duration-300 shadow-lg
            ${isDownloading 
              ? 'bg-dark-600 text-dark-300 cursor-wait' 
              : downloadComplete
                ? 'bg-green-600 text-white'
                : 'bg-gradient-to-r from-accent-primary to-accent-secondary text-white hover:shadow-accent-primary/30 hover:shadow-xl'
            }
          `}
        >
          {isDownloading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Generating...</span>
            </>
          ) : downloadComplete ? (
            <>
              <Check className="w-4 h-4" />
              <span>Downloaded!</span>
            </>
          ) : (
            <>
              <FileDown className="w-4 h-4" />
              <span>Download Report</span>
            </>
          )}
        </button>
        
        {/* Options Toggle */}
        <button
          onClick={() => setShowOptions(!showOptions)}
          className={`
            p-2 rounded-lg transition-colors
            ${showOptions ? 'bg-accent-primary text-white' : 'bg-dark-700 hover:bg-dark-600 text-dark-200'}
          `}
          title="Report Options"
        >
          <Settings2 className="w-4 h-4" />
        </button>
      </div>

      {/* Options Panel */}
      {showOptions && (
        <div className="absolute top-full right-0 mt-2 w-72 bg-dark-800 border border-dark-500 rounded-xl shadow-2xl z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-dark-700 border-b border-dark-500">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-accent-primary" />
              <span className="font-medium text-sm">Report Options</span>
            </div>
            <button 
              onClick={() => setShowOptions(false)}
              className="p-1 hover:bg-dark-600 rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          {/* Options Content */}
          <div className="p-4 space-y-4">
            {/* Title Input */}
            <div>
              <label className="block text-xs text-dark-300 mb-1.5">Report Title</label>
              <input
                type="text"
                value={options.title}
                onChange={(e) => setOptions({ ...options, title: e.target.value })}
                className="w-full px-3 py-2 bg-dark-700 border border-dark-500 rounded-lg text-sm focus:border-accent-primary focus:outline-none transition-colors"
                placeholder="Enter report title..."
              />
            </div>
            
            {/* Include Options */}
            <div>
              <label className="block text-xs text-dark-300 mb-2">Include Sections</label>
              <div className="space-y-2">
                <OptionCheckbox 
                  checked={options.includeAirQuality}
                  onChange={(checked) => setOptions({ ...options, includeAirQuality: checked })}
                  label="Air Quality Data"
                  color="text-green-400"
                />
                <OptionCheckbox 
                  checked={options.includeMethane}
                  onChange={(checked) => setOptions({ ...options, includeMethane: checked })}
                  label="Methane Emissions"
                  color="text-orange-400"
                />
                <OptionCheckbox 
                  checked={options.includeCO2}
                  onChange={(checked) => setOptions({ ...options, includeCO2: checked })}
                  label="CO₂ Emissions"
                  color="text-red-400"
                />
                <OptionCheckbox 
                  checked={options.includeFires}
                  onChange={(checked) => setOptions({ ...options, includeFires: checked })}
                  label="Active Fires"
                  color="text-amber-400"
                />
              </div>
            </div>
          </div>
          
          {/* Footer */}
          <div className="px-4 py-3 bg-dark-700 border-t border-dark-500">
            <button
              onClick={() => {
                setShowOptions(false)
                handleDownload()
              }}
              className="w-full py-2 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            >
              <FileDown className="w-4 h-4" />
              Generate & Download
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Checkbox Component
function OptionCheckbox({ 
  checked, 
  onChange, 
  label, 
  color 
}: { 
  checked: boolean
  onChange: (checked: boolean) => void
  label: string
  color: string
}) {
  return (
    <label className="flex items-center gap-2 cursor-pointer group">
      <div className={`
        w-4 h-4 rounded border-2 flex items-center justify-center transition-all
        ${checked 
          ? 'bg-accent-primary border-accent-primary' 
          : 'border-dark-400 group-hover:border-dark-300'
        }
      `}>
        {checked && <Check className="w-3 h-3 text-white" />}
      </div>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />
      <span className={`text-sm ${color}`}>{label}</span>
    </label>
  )
}
